#!/usr/bin/env python3
"""B1 kill-card audit for forced/aggressive-flow candidates.

This script is intentionally a data/power audit only. It does not backtest,
does not tune alpha parameters, and does not read HOLDOUT paths.
"""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path


RESEARCH_ROOT = Path(__file__).resolve().parents[1]
PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA = RESEARCH_ROOT / "DATA"
CODE = RESEARCH_ROOT / "CODE"
OUTPUT = CODE / "output"

READ_DIRS = [
    DATA / "LIQUIDATIONS",
    DATA / "LIQ_SAMPLE",
    DATA / "SPOT",
    DATA / "FUTURES",
]

FORBIDDEN_PARTS = {"HOLDOUT", "sealed_holdout.enc"}


def assert_not_holdout(path: Path) -> None:
    parts = set(path.resolve().parts)
    if parts & FORBIDDEN_PARTS:
        raise RuntimeError(f"Refusing to read holdout/sealed path: {path}")


def count_files_and_rows(path: Path) -> dict:
    assert_not_holdout(path)
    files = []
    if path.exists():
        for item in sorted(path.rglob("*")):
            if item.is_file():
                assert_not_holdout(item)
                rows = 0
                try:
                    with item.open("rb") as handle:
                        rows = sum(1 for _ in handle)
                except OSError:
                    rows = None
                files.append({"path": str(item.relative_to(PROJECT_ROOT)), "rows": rows})
    return {"path": str(path.relative_to(PROJECT_ROOT)), "exists": path.exists(), "file_count": len(files), "files": files}


def load_json(path: Path) -> dict | None:
    assert_not_holdout(path)
    if not path.exists():
        return None
    return json.loads(path.read_text())


def collector_log_summary(path: Path) -> dict:
    assert_not_holdout(path)
    if not path.exists():
        return {"exists": False}
    text = path.read_text(errors="replace")
    heartbeat_rows = [int(match.group(1)) for match in re.finditer(r"today_rows=\s*(\d+)", text)]
    errors = {}
    for key in [
        "ping/pong timed out",
        "UNEXPECTED_EOF_WHILE_READING",
        "Connection to remote host was lost",
    ]:
        errors[key] = text.count(key)
    return {
        "exists": True,
        "heartbeat_count": len(heartbeat_rows),
        "heartbeat_nonzero_count": sum(1 for value in heartbeat_rows if value > 0),
        "heartbeat_max_rows": max(heartbeat_rows) if heartbeat_rows else None,
        "errors": errors,
    }


def bp(percent: float) -> float:
    return percent * 100.0


def cost_scenarios() -> dict:
    """Return round-trip break-even drift hurdles in basis points."""
    taker_fee_bp = 5.0
    maker_fee_bp = 2.0
    protocol_fee_bp = 10.0

    taker_base_slippage_bp = 10.0
    stress_slippage_bp = [30.0, 50.0, 100.0]

    maker_scenarios = [
        {"name": "optimistic", "fill_rate": 0.70, "adverse_selection_bp_per_side": 3.0},
        {"name": "base", "fill_rate": 0.50, "adverse_selection_bp_per_side": 5.0},
        {"name": "stress", "fill_rate": 0.25, "adverse_selection_bp_per_side": 8.0},
    ]

    maker = []
    for item in maker_scenarios:
        filled_trade_cost = 2.0 * maker_fee_bp + 2.0 * item["adverse_selection_bp_per_side"]
        signal_level_hurdle = filled_trade_cost / item["fill_rate"]
        maker.append(
            {
                **item,
                "nominal_fee_roundtrip_bp": 2.0 * maker_fee_bp,
                "filled_trade_effective_cost_bp": round(filled_trade_cost, 2),
                "signal_level_effective_hurdle_bp": round(signal_level_hurdle, 2),
            }
        )

    return {
        "founder_taker_taker_base_bp": 2.0 * (taker_fee_bp + taker_base_slippage_bp),
        "protocol_conservative_taker_taker_base_bp": 2.0 * (protocol_fee_bp + taker_base_slippage_bp),
        "event_taker_taker_stress_bp": [
            {"slippage_bp_per_side": s, "roundtrip_bp": 2.0 * (taker_fee_bp + s)}
            for s in stress_slippage_bp
        ],
        "maker_maker": maker,
    }


def gate_results(costs: dict, data_audit: dict, diag: dict | None, log: dict) -> dict:
    empty_orderflow = data_audit["SPOT"]["file_count"] == 0
    no_l2_rebuilder = True
    if (CODE / "orderbook_rebuilder.py").exists() or (CODE / "ofi_rebuilder.py").exists():
        no_l2_rebuilder = False

    diag_zero_frames = False
    if diag:
        tests = diag.get("tests", [])
        diag_zero_frames = bool(tests) and all(test.get("frames", 0) == 0 for test in tests)

    liq_empty = data_audit["LIQUIDATIONS"]["file_count"] == 0 and data_audit["LIQ_SAMPLE"]["file_count"] == 0
    log_zero = log.get("exists") and log.get("heartbeat_count", 0) > 0 and log.get("heartbeat_nonzero_count") == 0

    maker_best_signal_hurdle = min(
        item["signal_level_effective_hurdle_bp"] for item in costs["maker_maker"]
    )
    taker_base = costs["founder_taker_taker_base_bp"]
    protocol_base = costs["protocol_conservative_taker_taker_base_bp"]

    # B1 is a kill card, not an alpha calibration. These upper bounds are
    # pre-specified economic priors from the B0 red-team wording: public,
    # minute-level OFI is expected to be single-digit bps; lead-lag at
    # second-minute non-colocated horizons is also assumed single-digit bps
    # unless data proves otherwise. No data in this repo proves otherwise.
    effect_priors = {
        "ofi_public_minute_upper_bp": 10.0,
        "lead_lag_public_minute_upper_bp": 10.0,
        "liquidation_free_data_upper_bp": None,
    }

    return {
        "OFI": {
            "gate1_cost": {
                "decision": "KILL_AS_TRADABLE",
                "basis": (
                    f"Reasonable gross upper bound {effect_priors['ofi_public_minute_upper_bp']}bp "
                    f"does not exceed best maker signal-level hurdle {maker_best_signal_hurdle}bp; "
                    f"taker base is {taker_base}bp and protocol conservative base is {protocol_base}bp."
                ),
            },
            "gate2_data": {
                "decision": "KILL",
                "basis": (
                    "No local aggTrades/depth sample files; "
                    f"dataplane zero-frames={diag_zero_frames}; "
                    f"L2 rebuilder present={not no_l2_rebuilder}."
                ),
            },
            "gate3_anti_a1": {"decision": "N/A", "basis": "OFI is not the A-1 liquidation rebound path."},
            "gate4_anti_sweep": {
                "decision": "PASS_CONDITIONAL",
                "basis": "Pure OFI/MLOFI uses flow variables only, but no tradable/data-ready design passed gates 1-2.",
            },
            "overall": "KILL_AS_TRADABLE",
        },
        "LIQUIDATION_FLOW": {
            "gate1_cost": {
                "decision": "KILL_TO_SLEEP",
                "basis": (
                    "Event execution must survive taker stress costs "
                    f"{[x['roundtrip_bp'] for x in costs['event_taker_taker_stress_bp']]}bp; "
                    "free data provides no reliable gross-effect upper bound."
                ),
            },
            "gate2_data": {
                "decision": "KILL_TO_SLEEP",
                "basis": (
                    f"Liquidation files empty={liq_empty}; collector heartbeats all zero={log_zero}; "
                    "free forceOrder missingness cannot be bounded from current artifacts."
                ),
            },
            "gate3_anti_a1": {
                "decision": "KILL_TO_SLEEP",
                "basis": (
                    "No single liquidation direction thesis (continuation or exhaustion) is frozen in an executable "
                    "preregistration; without full direct data, true separation from A-1 cannot be established."
                ),
            },
            "gate4_anti_sweep": {
                "decision": "PASS_CONDITIONAL",
                "basis": "Allowed only if trigger, direction, and maker levels are derived from liquidation/order-flow variables, not chart levels.",
            },
            "overall": "SLEEP_DATA_ACCUMULATION_ONLY",
        },
        "SPOT_PERP_LEAD_LAG": {
            "gate1_cost": {
                "decision": "KILL_NOW",
                "basis": (
                    f"Reasonable gross upper bound {effect_priors['lead_lag_public_minute_upper_bp']}bp "
                    f"does not exceed best maker signal-level hurdle {maker_best_signal_hurdle}bp; "
                    f"taker base is {taker_base}bp. This remains only a future data-audit candidate."
                ),
            },
            "gate2_data": {
                "decision": "KILL_NOW",
                "basis": (
                    f"Spot aggressive-flow files empty={empty_orderflow}; no paired spot/perp trade+book continuity audit exists."
                ),
            },
            "gate3_anti_a1": {"decision": "N/A", "basis": "Not a liquidation rebound hypothesis."},
            "gate4_anti_sweep": {
                "decision": "PASS_CONDITIONAL",
                "basis": "Can be whitelist-clean only if entry/direction use signed aggressive flow and book variables.",
            },
            "overall": "KILL_NOW_NOT_B2",
        },
    }


def main() -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)

    data_audit = {}
    for path in READ_DIRS:
        data_audit[path.name] = count_files_and_rows(path)

    diag = load_json(OUTPUT / "collector_dataplane_diag.json")
    log = collector_log_summary(CODE / "collector.log")
    costs = cost_scenarios()
    gates = gate_results(costs, data_audit, diag, log)

    result = {
        "task_id": "P1-RES-036-B1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "holdout_policy": "No HOLDOUT or sealed_holdout paths read; script refuses those paths.",
        "data_audit": data_audit,
        "collector_dataplane_diag_summary": {
            "present": diag is not None,
            "layer_diagnosis": diag.get("layer_diagnosis") if diag else None,
            "test_count": len(diag.get("tests", [])) if diag else 0,
            "zero_frame_tests": sum(1 for test in diag.get("tests", []) if test.get("frames", 0) == 0) if diag else 0,
        },
        "collector_log_summary": log,
        "cost_scenarios": costs,
        "candidate_gates": gates,
        "overall_recommendation": "Do not enter B2. Kill OFI as tradable under current public/minute assumptions; keep liquidation flow asleep for paid/full or 3-6 month forward data; do not take lead-lag without a new clean data audit.",
    }

    out = OUTPUT / "b1_killcard_forced_flow_audit.json"
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(out)


if __name__ == "__main__":
    main()
