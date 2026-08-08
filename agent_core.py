from __future__ import annotations

import json
import os
import re
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable
from urllib import error, request

ROOT = Path(__file__).resolve().parent
DATA_PATH = ROOT / "data" / "strategy_dashboard_data.json"


@dataclass(frozen=True)
class AscendSettings:
    base_url: str = os.getenv("ASCEND_BASE_URL", "https://api.atomgit.com/api/v5")
    api_key: str = os.getenv("ASCEND_API_KEY", os.getenv("ATOMGIT_TOKEN", ""))
    model: str = os.getenv("ASCEND_MODEL", "deepseek-v4-flash")
    timeout_seconds: int = int(os.getenv("ASCEND_TIMEOUT_SECONDS", "45"))

    @property
    def configured(self) -> bool:
        return bool(self.api_key.strip())

    @property
    def endpoint(self) -> str:
        base = self.base_url.rstrip("/")
        if base.endswith("/chat/completions"):
            return base
        return f"{base}/chat/completions"


class AgentConfigurationError(RuntimeError):
    pass


class AgentProviderError(RuntimeError):
    pass


def load_dataset() -> dict[str, Any]:
    with DATA_PATH.open("r", encoding="utf-8") as fh:
        return json.load(fh)


def _deep_keys_containing(data: dict[str, Any], needles: tuple[str, ...]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in data.items():
        lowered = key.lower()
        if any(needle in lowered for needle in needles):
            out[key] = value
    return out


def _normalize_window(question: str, fallback: str = "all") -> str:
    q = question.lower()
    if re.search(r"\b60\s*d(?:ay)?\b|60\s*天|60\s*日", q):
        return "60"
    if re.search(r"\b120\s*d(?:ay)?\b|120\s*天|120\s*日", q):
        return "120"
    if "全样本" in q or "全部" in q or "all" in q:
        return "all"
    return fallback


def tool_project_overview(data: dict[str, Any], question: str) -> dict[str, Any]:
    return {
        "project": data.get("project", {}),
        "generated_at": data.get("generated_at"),
        "data_version": data.get("version"),
        "public_safety": data.get("public_safety", {}),
        "common_date_range": data.get("same_period", {}).get("common_date_range", {}),
        "refresh_status": data.get("refresh_status", {}),
    }


def tool_strategy_comparison(data: dict[str, Any], question: str) -> dict[str, Any]:
    window = _normalize_window(question)
    rows = data.get("same_period", {}).get("summary", [])
    chosen = [row for row in rows if str(row.get("window")) == window]
    if not chosen and rows:
        windows = [str(row.get("window")) for row in rows]
        window = "all" if "all" in windows else windows[-1]
        chosen = [row for row in rows if str(row.get("window")) == window]

    ranked_return = sorted(chosen, key=lambda x: float(x.get("total_return_pct") or -1e18), reverse=True)
    ranked_drawdown = sorted(chosen, key=lambda x: abs(float(x.get("max_drawdown_pct") or 1e18)))
    return {
        "window": window,
        "rows": chosen,
        "highest_historical_return": ranked_return[0].get("strategy") if ranked_return else None,
        "smallest_absolute_drawdown": ranked_drawdown[0].get("strategy") if ranked_drawdown else None,
        "interpretation_boundary": "Historical same-period research evidence only; no future-return claim.",
    }


def tool_signal_snapshot(data: dict[str, Any], question: str) -> dict[str, Any]:
    live = data.get("live_signals")
    if live is None:
        live = _deep_keys_containing(data, ("signal", "target"))
    return {
        "generated_at": data.get("generated_at"),
        "refresh_status": data.get("refresh_status", {}),
        "signal_snapshot": live or {},
        "boundary": "Displayed research/simulation snapshot; never a broker instruction or live order.",
    }


def tool_execution_research(data: dict[str, Any], question: str) -> dict[str, Any]:
    exact = data.get("execution_research")
    if exact is None:
        exact = _deep_keys_containing(data, ("execution", "policy", "cluster"))
    return {
        "execution_research": exact or {},
        "boundary": "Execution-policy evidence is hypothesis research only and is not production-approved.",
    }


def tool_risk_guardrails(data: dict[str, Any], question: str) -> dict[str, Any]:
    rows = data.get("same_period", {}).get("summary", [])
    all_rows = [row for row in rows if str(row.get("window")) == "all"] or rows
    risk_rows = [
        {
            "strategy": row.get("strategy"),
            "max_drawdown_pct": row.get("max_drawdown_pct"),
            "mean_turnover_pct": row.get("mean_turnover_pct"),
            "avg_holding_days": row.get("avg_holding_days"),
        }
        for row in all_rows
    ]
    return {
        "public_safety": data.get("public_safety", {}),
        "refresh_status": data.get("refresh_status", {}),
        "generated_at": data.get("generated_at"),
        "risk_rows": risk_rows,
        "hard_guardrails": [
            "No broker connectivity or order execution.",
            "No personalized buy/sell recommendation.",
            "Always distinguish historical evidence from forward-looking claims.",
            "Surface stale-data or refresh warnings instead of hiding them.",
        ],
    }


TOOLS: dict[str, Callable[[dict[str, Any], str], dict[str, Any]]] = {
    "project_overview": tool_project_overview,
    "strategy_comparison": tool_strategy_comparison,
    "signal_snapshot": tool_signal_snapshot,
    "execution_research": tool_execution_research,
    "risk_guardrails": tool_risk_guardrails,
}

TOOL_DESCRIPTIONS = {
    "project_overview": "Project scope, data range, refresh state and safety boundary.",
    "strategy_comparison": "Same-period strategy metrics: return, drawdown, win rate, turnover, holding period.",
    "signal_snapshot": "Research/simulation signal snapshot and refresh date.",
    "execution_research": "5-minute execution-policy research and frozen-hypothesis evidence.",
    "risk_guardrails": "Risk metrics, stale-data warnings and non-trading guardrails.",
}


def _heuristic_plan(question: str) -> list[str]:
    q = question.lower()
    tools: list[str] = []
    if any(k in q for k in ["策略", "strategy", "收益", "return", "回撤", "drawdown", "胜率", "换手"]):
        tools.append("strategy_comparison")
    if any(k in q for k in ["信号", "signal", "target", "持仓", "目标"]):
        tools.append("signal_snapshot")
    if any(k in q for k in ["执行", "execution", "5m", "5 分钟", "卖出", "sell"]):
        tools.append("execution_research")
    if any(k in q for k in ["风险", "risk", "安全吗", "能不能买", "推荐", "建议"]):
        tools.append("risk_guardrails")
    if not tools:
        tools = ["project_overview", "strategy_comparison"]
    return list(dict.fromkeys(tools))[:3]


def _extract_text(payload: dict[str, Any]) -> str:
    choices = payload.get("choices")
    if isinstance(choices, list) and choices:
        first = choices[0] or {}
        message = first.get("message") or {}
        content = message.get("content")
        if isinstance(content, str):
            return content
        if isinstance(content, list):
            parts: list[str] = []
            for item in content:
                if isinstance(item, dict) and isinstance(item.get("text"), str):
                    parts.append(item["text"])
            if parts:
                return "\n".join(parts)
        if isinstance(first.get("text"), str):
            return first["text"]
    data = payload.get("data")
    if isinstance(data, dict):
        return _extract_text(data)
    raise AgentProviderError("Provider response did not contain recognizable text output.")


def _post_chat(settings: AscendSettings, messages: list[dict[str, str]], temperature: float = 0.2) -> tuple[str, float]:
    if not settings.configured:
        raise AgentConfigurationError(
            "ASCEND_API_KEY is not configured. Set ASCEND_API_KEY (or ATOMGIT_TOKEN) before running the competition demo."
        )

    payload = {
        "model": settings.model,
        "messages": messages,
        "temperature": temperature,
        "stream": False,
    }
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    req = request.Request(
        settings.endpoint,
        data=body,
        method="POST",
        headers={
            "Authorization": f"Bearer {settings.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": "ETF-Research-Copilot/1.0",
        },
    )
    started = time.perf_counter()
    try:
        with request.urlopen(req, timeout=settings.timeout_seconds) as resp:
            raw = resp.read().decode("utf-8")
    except error.HTTPError as exc:
        details = exc.read().decode("utf-8", errors="replace")[:1000]
        raise AgentProviderError(f"Ascend/AtomGit API HTTP {exc.code}: {details}") from exc
    except error.URLError as exc:
        raise AgentProviderError(f"Ascend/AtomGit API connection failed: {exc.reason}") from exc
    latency_ms = (time.perf_counter() - started) * 1000

    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise AgentProviderError("Ascend/AtomGit API returned non-JSON content.") from exc
    return _extract_text(parsed), latency_ms


def _parse_plan(text: str) -> list[str]:
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", cleaned, flags=re.S)
    try:
        parsed = json.loads(cleaned)
    except json.JSONDecodeError:
        return []
    raw_tools = parsed.get("tools", []) if isinstance(parsed, dict) else []
    tools = [name for name in raw_tools if name in TOOLS]
    return list(dict.fromkeys(tools))[:3]


def plan_tools(question: str, settings: AscendSettings) -> tuple[list[str], float, bool]:
    descriptions = "\n".join(f"- {name}: {desc}" for name, desc in TOOL_DESCRIPTIONS.items())
    messages = [
        {
            "role": "system",
            "content": (
                "You are the planner for a financial research evidence agent. "
                "Choose only the minimum tools needed. Never select trading or broker actions because none exist. "
                "Return strict JSON only: {\"tools\":[\"tool_name\"],\"focus\":\"short phrase\"}.\n"
                f"Available tools:\n{descriptions}"
            ),
        },
        {"role": "user", "content": question[:2000]},
    ]
    try:
        text, latency = _post_chat(settings, messages, temperature=0.0)
        tools = _parse_plan(text)
        if tools:
            return tools, latency, False
    except AgentProviderError:
        raise
    return _heuristic_plan(question), latency if "latency" in locals() else 0.0, True


def build_evidence(data: dict[str, Any], question: str, tool_names: list[str]) -> dict[str, Any]:
    evidence: dict[str, Any] = {}
    for name in tool_names:
        tool = TOOLS.get(name)
        if tool:
            evidence[name] = tool(data, question)
    return evidence


def answer_query(question: str) -> dict[str, Any]:
    question = (question or "").strip()
    if not question:
        raise ValueError("question is required")

    settings = AscendSettings()
    data = load_dataset()

    total_started = time.perf_counter()
    tools, planner_latency, planner_fallback = plan_tools(question, settings)
    evidence_started = time.perf_counter()
    evidence = build_evidence(data, question, tools)
    evidence_latency = (time.perf_counter() - evidence_started) * 1000

    synthesis_messages = [
        {
            "role": "system",
            "content": (
                "You are ETF Research Copilot, a finance research evidence agent running with Ascend model inference. "
                "Answer in the user's language. Ground every numerical claim in the supplied evidence. "
                "Separate facts from interpretation. Never claim future performance from historical backtests. "
                "Do not provide personalized investment instructions or tell the user to buy/sell. "
                "If refresh data is stale or contains warnings, state that clearly. "
                "Keep the answer concise and decision-useful: conclusion, evidence, risks/limits, next verification step."
            ),
        },
        {
            "role": "user",
            "content": json.dumps(
                {
                    "question": question,
                    "selected_tools": tools,
                    "evidence": evidence,
                },
                ensure_ascii=False,
            ),
        },
    ]
    answer, synthesis_latency = _post_chat(settings, synthesis_messages, temperature=0.2)
    total_latency = (time.perf_counter() - total_started) * 1000

    return {
        "answer": answer.strip(),
        "tools": tools,
        "evidence": evidence,
        "trace": [
            {"step": "plan", "detail": ", ".join(tools), "fallback": planner_fallback},
            {"step": "retrieve", "detail": f"{len(evidence)} evidence bundles"},
            {"step": "synthesize", "detail": settings.model},
        ],
        "provider": "Ascend / AtomGit AI API",
        "model": settings.model,
        "latency_ms": {
            "planner": round(planner_latency, 1),
            "evidence": round(evidence_latency, 1),
            "synthesis": round(synthesis_latency, 1),
            "total": round(total_latency, 1),
        },
        "data_version": data.get("version"),
        "generated_at": data.get("generated_at"),
    }
