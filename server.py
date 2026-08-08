from __future__ import annotations

import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

from agent_core import (
    AscendSettings,
    AgentConfigurationError,
    AgentProviderError,
    answer_query,
    build_evidence,
    load_dataset,
)

ROOT = Path(__file__).resolve().parent
app = FastAPI(
    title="ETF Research Copilot",
    description="Ascend-powered, tool-augmented ETF research evidence Agent.",
    version="1.0.0",
)


class AgentRequest(BaseModel):
    question: str = Field(min_length=2, max_length=2000)


@app.get("/api/health")
def health() -> dict:
    settings = AscendSettings()
    data = load_dataset()
    return {
        "status": "ok",
        "ascend_configured": settings.configured,
        "provider": "Ascend / AtomGit AI API",
        "endpoint": settings.endpoint,
        "model": settings.model,
        "data_version": data.get("version"),
        "generated_at": data.get("generated_at"),
        "agent_mode": "tool-augmented two-stage plan/retrieve/synthesize",
        "broker_connected": False,
    }


@app.post("/api/agent/query")
def query_agent(payload: AgentRequest):
    try:
        return answer_query(payload.question)
    except AgentConfigurationError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc
    except AgentProviderError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@app.get("/api/benchmark")
def benchmark(runs: int = 100) -> JSONResponse:
    runs = max(1, min(runs, 1000))
    data = load_dataset()
    question = "比较全样本三个策略的收益、回撤和风险"
    selected_tools = ["strategy_comparison", "risk_guardrails"]
    samples: list[float] = []
    for _ in range(runs):
        started = time.perf_counter()
        build_evidence(data, question, selected_tools)
        samples.append((time.perf_counter() - started) * 1000)
    samples.sort()
    p50 = samples[len(samples) // 2]
    p95 = samples[min(len(samples) - 1, int(len(samples) * 0.95))]
    return JSONResponse(
        {
            "runs": runs,
            "tool_retrieval_ms": {
                "p50": round(p50, 3),
                "p95": round(p95, 3),
                "max": round(max(samples), 3),
            },
            "note": "Measures local evidence-tool latency only. Model latency is reported per /api/agent/query response.",
        }
    )


app.mount("/", StaticFiles(directory=ROOT, html=True), name="static")
