#!/usr/bin/env python3
from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
B17_DIR = REPO_ROOT / "examples" / "b17_etf_v1_base_tech"
OUT_PATH = Path(__file__).resolve().parents[1] / "data" / "strategy_dashboard_data.json"


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def fnum(value: Any) -> float | None:
    if value in (None, ""):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def pct(value: Any) -> float | None:
    num = fnum(value)
    if num is None:
        return None
    return round(num * 100, 4)


def compact_summary(row: dict[str, Any]) -> dict[str, Any]:
    return {
        "window": str(row.get("window", "")),
        "strategy": row.get("strategy", ""),
        "window_start": row.get("window_start", ""),
        "window_end": row.get("window_end", ""),
        "folds": int(fnum(row.get("folds")) or 0),
        "total_return_pct": pct(row.get("total_return")),
        "max_drawdown_pct": pct(row.get("max_drawdown")),
        "win_rate_pct": pct(row.get("win_rate")),
        "mean_turnover_pct": pct(row.get("mean_turnover")),
        "avg_holding_days": round(fnum(row.get("avg_holding_days")) or 0, 2),
        "buy_count": int(fnum(row.get("buy_count")) or 0),
        "sell_count": int(fnum(row.get("sell_count")) or 0),
    }


def build_curves(rows: list[dict[str, str]]) -> dict[str, list[dict[str, Any]]]:
    curves: dict[str, list[dict[str, Any]]] = {}
    for row in rows:
        key = f"{row.get('strategy')}__{row.get('window')}"
        curves.setdefault(key, [])

    for key, key_rows in ((k, [r for r in rows if f"{r.get('strategy')}__{r.get('window')}" == k]) for k in curves):
        cumulative = 1.0
        points: list[dict[str, Any]] = []
        for row in sorted(key_rows, key=lambda r: r.get("signal_day", "")):
            r = fnum(row.get("fold_return")) or 0.0
            cumulative *= 1.0 + r
            points.append(
                {
                    "date": row.get("signal_day", ""),
                    "value_pct": round((cumulative - 1.0) * 100, 4),
                    "turnover_pct": pct(row.get("fold_turnover")),
                    "position_count": int(fnum(row.get("position_count")) or 0),
                }
            )
        curves[key] = points[-180:]
    return curves


def extract_live_signal(path: Path) -> dict[str, Any]:
    data = read_json(path, {})
    top10 = data.get("top10") or []
    by_symbol = {row.get("symbol"): row for row in top10 if isinstance(row, dict)}

    def describe(symbol: str) -> dict[str, Any]:
        row = by_symbol.get(symbol, {})
        return {
            "symbol": symbol,
            "name": row.get("name", ""),
            "rank": row.get("rank"),
            "score": row.get("score"),
        }

    return {
        "strategy": data.get("strategy", ""),
        "signal_source_day": data.get("signal_source_day", ""),
        "next_exec_day": data.get("next_exec_day", ""),
        "generated_at": data.get("generated_at", ""),
        "top_targets": [describe(symbol) for symbol in data.get("top_targets", [])],
        "planned_buy_count": len(data.get("planned_buys", []) or []),
        "planned_sell_count": len(data.get("planned_sells", []) or []),
        "summary": {
            "mean_turnover_pct": pct((data.get("summary") or {}).get("mean_turnover")),
            "avg_holding_days": round(fnum((data.get("summary") or {}).get("avg_holding_days")) or 0, 2),
            "buy_count": int(fnum((data.get("summary") or {}).get("buy_count")) or 0),
            "sell_count": int(fnum((data.get("summary") or {}).get("sell_count")) or 0),
        },
    }


def main() -> int:
    same_period_json = read_json(
        B17_DIR / "output" / "b17_same_period_execution_comparison" / "b17_same_period_execution_comparison_latest.json",
        {},
    )
    same_period_rows = same_period_json.get("summary_rows") or []
    same_period_daily = read_csv(
        B17_DIR / "output" / "b17_same_period_execution_comparison" / "b17_same_period_execution_comparison_daily_latest.csv"
    )

    policy_summary_rows = read_csv(B17_DIR / "artifacts" / "b17_exit_execution_5m_policy_search" / "policy_summary.csv")
    fixed_policy_rows = [
        {
            "policy": row.get("policy"),
            "event_count": int(fnum(row.get("event_count")) or 0),
            "mean_vs_open_pct": pct(row.get("mean_vs_open")),
            "median_vs_open_pct": pct(row.get("median_vs_open")),
            "win_rate_vs_open_pct": pct(row.get("win_rate_vs_open")),
            "p25_pct": pct(row.get("p25")),
            "p75_pct": pct(row.get("p75")),
        }
        for row in policy_summary_rows
        if row.get("policy_family") == "fixed_time"
    ]

    validation = read_json(
        B17_DIR / "artifacts" / "b17_5m_policy_candidate_validation" / "b17_5m_policy_candidate_validation_report.json",
        {},
    )
    window_clusters = read_csv(
        B17_DIR / "artifacts" / "b17_5m_policy_candidate_validation" / "candidate_window_cluster_summary.csv"
    )

    auto_refresh = read_json(B17_DIR / "output" / "auto_refresh_status_latest.json", {})
    ghostfolio = read_json(B17_DIR / "output" / "sim_trade" / "ghostfolio_core2_import_latest.json", {})

    payload = {
        "version": "strategy-dashboard-public-v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "public_safety": {
            "research_only": True,
            "not_investment_advice": True,
            "no_tokens_or_account_data": True,
            "no_production_sell_rule": True,
        },
        "project": {
            "name": "B17 ETF Rotation Research System",
            "scope": "A-share ETF rotation research, simulated execution, and non-production execution-policy validation.",
            "primary_strategies": ["b17_base_5d", "hold_bonus_1.0", "core2_satellite1"],
            "status": "research-to-paper system; not a production trading system",
        },
        "refresh_status": {
            "status": auto_refresh.get("status", ""),
            "ok": bool(auto_refresh.get("ok")),
            "started_at": auto_refresh.get("started_at", ""),
            "finished_at": auto_refresh.get("finished_at", ""),
            "live_signal_source_day": (auto_refresh.get("verification") or {}).get("live_signal_source_day", ""),
            "ghostfolio_sync_status": ghostfolio.get("sync_status", ""),
            "warning_steps": [w.get("step") for w in auto_refresh.get("warnings", [])],
        },
        "same_period": {
            "common_date_range": same_period_json.get("common_date_range", {}),
            "summary": [compact_summary(row) for row in same_period_rows],
            "curves": build_curves(same_period_daily),
        },
        "live_signals": {
            "hold_bonus_1.0": extract_live_signal(
                B17_DIR / "output" / "live_signal" / "rank_rotation_execution_hold_bonus_1p0_live_signal_latest.json"
            ),
            "core2_satellite1": extract_live_signal(
                B17_DIR / "output" / "live_signal" / "rank_rotation_execution_core2_satellite1_live_signal_latest.json"
            ),
        },
        "execution_research": {
            "candidate_policy_status": validation.get("candidate_policy_status", ""),
            "candidate_window": validation.get("candidate_window", "sell_10m to sell_50m"),
            "representative_candidate": validation.get("candidate_policy", "sell_45m"),
            "broad_window_evidence": validation.get("broad_window_evidence", {}),
            "window_clusters": [
                {
                    "window": row.get("window"),
                    "policies": row.get("policies"),
                    "average_mean_vs_open_pct": pct(row.get("average_mean_vs_open")),
                    "average_median_vs_open_pct": pct(row.get("average_median_vs_open")),
                    "average_win_rate_pct": pct(row.get("average_win_rate")),
                    "window_consistency_score": round(fnum(row.get("window_consistency_score")) or 0, 3),
                }
                for row in window_clusters
            ],
            "fixed_time_policy_summary": fixed_policy_rows,
            "notes": [
                "This is a 5m proxy execution study, not a true 1m intraday execution backtest.",
                "No sell rule is production-approved.",
                "Future forward 1m validation is required before any production use.",
            ],
        },
        "engineering_timeline": [
            {"phase": "Research", "label": "Feature engineering and rank-rotation backtests"},
            {"phase": "Execution design", "label": "Hold Bonus and Core2/Satellite constraints"},
            {"phase": "Paper tracking", "label": "Futu SIMULATE / Ghostfolio observer boundaries"},
            {"phase": "Execution research", "label": "BaoStock 5m proxy and frozen delayed-sell hypothesis"},
            {"phase": "Publication", "label": "Static dashboard + Cloudflare/GitHub-ready public artifacts"},
        ],
    }
    OUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUT_PATH.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(OUT_PATH)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
