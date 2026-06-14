#!/usr/bin/env python3
"""Execute the preregistered A-1 Tier A screen from work episodes only."""

from __future__ import annotations

import csv
import json
import math
import subprocess
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

from a1_tiera_core import (
    BOOTSTRAP_REPLICATIONS,
    CUTOFF_EXCLUSIVE,
    HORIZONS,
    SEED,
    SYMBOLS,
    BootstrapResult,
    assert_not_restricted_path,
    holm_adjust,
    moving_block_mean_test,
    moving_block_spearman_test,
    power_diagnostic,
    sha256_file,
    wf_stability,
)


ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES"
WORK_DIR = ROOT / "06_RESEARCH" / "DATA" / "A1_WORK"
WORK_PATH = WORK_DIR / "work_episodes.csv"
MANIFEST_PATH = WORK_DIR / "A1_HOLDOUT_MANIFEST.json"
PERMTEST_PATH = WORK_DIR / "A1_HOLDOUT_PERMTEST.log"
RESULTS_DIR = ROOT / "06_RESEARCH" / "RESULTS"
REPORT_PATH = RESULTS_DIR / "20260615_a1_tierA_screen.md"
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
JSON_PATH = OUTPUT_DIR / "a1_tiera_screen_results.json"
TASK_INBOX_PATH = (
    ROOT / "04_AI_TEAM" / "TASK_INBOX" / "A1_TIERA_EXEC_DONE.json"
)


def _read_market_before_cutoff(
    path: Path,
    *,
    time_column: str,
    value_column: str,
) -> pd.DataFrame:
    """Stop reading at the cutoff; post-cutoff rows never enter memory."""
    assert_not_restricted_path(path)
    rows: list[dict[str, object]] = []
    with path.open("r", newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        missing = {time_column, value_column} - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path.name} missing columns: {sorted(missing)}")
        for row in reader:
            timestamp = pd.to_datetime(row[time_column], utc=True)
            if timestamp >= CUTOFF_EXCLUSIVE:
                break
            rows.append(
                {
                    "ts": timestamp,
                    "value": pd.to_numeric(row[value_column], errors="coerce"),
                }
            )
    return pd.DataFrame(rows)


def load_work() -> pd.DataFrame:
    assert_not_restricted_path(WORK_PATH)
    work = pd.read_csv(WORK_PATH)
    required = {
        "event_time_utc",
        "symbol",
        "severity_code",
        "a2_overlap",
        "regime",
    }
    missing = required - set(work.columns)
    if missing:
        raise ValueError(f"work episodes missing columns: {sorted(missing)}")
    work["event_time"] = pd.to_datetime(work["event_time_utc"], utc=True)
    if (work["event_time"] >= CUTOFF_EXCLUSIVE).any():
        raise AssertionError("work contains an event at or after cutoff")
    return work.sort_values(["event_time", "symbol"], kind="mergesort").reset_index(
        drop=True
    )


def load_mark(symbol: str) -> pd.DataFrame:
    raw = _read_market_before_cutoff(
        DATA_DIR / f"{symbol}_MARK_1H.csv",
        time_column="datetime",
        value_column="close",
    )
    raw = raw.rename(columns={"ts": "bar_open_time", "value": "mark_close"})
    raw["close_time"] = raw["bar_open_time"] + pd.Timedelta(hours=1)
    if raw["bar_open_time"].duplicated().any():
        raise ValueError(f"{symbol} MARK contains duplicate bar opens")
    return raw.sort_values("close_time").reset_index(drop=True)


def load_funding(symbol: str) -> pd.DataFrame:
    raw = _read_market_before_cutoff(
        DATA_DIR / f"{symbol}_FUNDING_8H.csv",
        time_column="datetime",
        value_column="last_funding_rate",
    )
    return raw.rename(columns={"ts": "funding_time", "value": "funding_rate"})


def _baseline_returns(
    close_map: dict[pd.Timestamp, float],
    event_time: pd.Timestamp,
) -> list[float]:
    returns: list[float] = []
    for offset in range(72, 0, -1):
        end_time = event_time - pd.Timedelta(hours=offset)
        start_time = end_time - pd.Timedelta(hours=1)
        start_close = close_map.get(start_time)
        end_close = close_map.get(end_time)
        if (
            start_close is not None
            and end_close is not None
            and start_close > 0
            and end_close > 0
        ):
            returns.append(math.log(end_close / start_close))
    return returns


def compute_episode_outcomes(
    work: pd.DataFrame,
    marks: dict[str, pd.DataFrame],
    funding: dict[str, pd.DataFrame],
) -> pd.DataFrame:
    """Compute CAR only for work rows; no sealed table is accepted or read."""
    rows: list[dict[str, object]] = []
    for episode in work.itertuples(index=False):
        symbol = str(episode.symbol)
        event_time = pd.Timestamp(episode.event_time)
        prices = marks[symbol]
        close_times = pd.DatetimeIndex(prices["close_time"])
        close_map = {
            pd.Timestamp(row.close_time): float(row.mark_close)
            for row in prices.itertuples(index=False)
            if pd.notna(row.mark_close)
        }
        signal_available = event_time + pd.Timedelta(hours=1)
        align_index = int(close_times.searchsorted(signal_available, side="right"))
        baseline = _baseline_returns(close_map, event_time)
        baseline_mean = float(np.mean(baseline)) if baseline else None
        baseline_variance = (
            float(np.var(baseline, ddof=1)) if len(baseline) >= 2 else None
        )
        row = episode._asdict()
        row["signal_available_time"] = signal_available
        row["baseline_n"] = len(baseline)
        row["baseline_mean"] = baseline_mean
        row["baseline_variance"] = baseline_variance

        if align_index >= len(prices):
            row["align_time"] = pd.NaT
            for horizon in HORIZONS:
                row[f"raw_return_{horizon}h"] = None
                row[f"car_{horizon}h"] = None
            row["holding_funding_48h"] = None
            row["net_car_48h_base"] = None
            row["net_car_48h_slip_030"] = None
            rows.append(row)
            continue

        align_time = pd.Timestamp(prices.iloc[align_index]["close_time"])
        align_close = float(prices.iloc[align_index]["mark_close"])
        row["align_time"] = align_time
        for horizon in HORIZONS:
            end_time = align_time + pd.Timedelta(hours=horizon)
            end_close = close_map.get(end_time)
            if (
                baseline_mean is None
                or end_close is None
                or align_close <= 0
                or end_close <= 0
            ):
                raw_return = None
                car = None
            else:
                raw_return = math.log(end_close / align_close)
                car = raw_return - horizon * baseline_mean
            row[f"raw_return_{horizon}h"] = raw_return
            row[f"car_{horizon}h"] = car

        exit_48h = align_time + pd.Timedelta(hours=48)
        funding_rows = funding[symbol]
        held = funding_rows.loc[
            (funding_rows["funding_time"] > align_time)
            & (funding_rows["funding_time"] <= exit_48h),
            "funding_rate",
        ]
        funding_cost = float(pd.to_numeric(held, errors="coerce").dropna().sum())
        row["holding_funding_48h"] = funding_cost
        if row["car_48h"] is None:
            row["net_car_48h_base"] = None
            row["net_car_48h_slip_030"] = None
        else:
            row["net_car_48h_base"] = float(row["car_48h"]) - 0.004 - funding_cost
            row["net_car_48h_slip_030"] = (
                float(row["car_48h"]) - 0.008 - funding_cost
            )
        rows.append(row)
    return pd.DataFrame(rows)


def _bootstrap_payload(result: BootstrapResult | None) -> dict[str, Any] | None:
    if result is None:
        return None
    return {
        "n": result.n,
        "estimate": result.estimate,
        "raw_p": result.p_value,
        "ci_low": result.ci_low,
        "ci_high": result.ci_high,
        "replications": result.replications,
        "seed": result.seed,
    }


def _mean_test(frame: pd.DataFrame, column: str) -> BootstrapResult | None:
    values = pd.to_numeric(frame[column], errors="coerce")
    valid = values.notna()
    return moving_block_mean_test(
        frame.loc[valid, "event_time"],
        values.loc[valid],
        replications=BOOTSTRAP_REPLICATIONS,
        seed=SEED,
    )


def _gate_status(
    result: BootstrapResult | None,
    adjusted_p: float | None,
) -> str:
    if result is None or adjusted_p is None:
        return "N.A."
    return "PASS" if result.estimate > 0 and adjusted_p <= 0.05 else "FAIL"


def verify_release_boundary() -> tuple[dict[str, Any], str]:
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    permtest = PERMTEST_PATH.read_text(encoding="utf-8")
    if "overall=PASS" not in permtest:
        raise PermissionError("negative permission test did not pass")
    if sha256_file(WORK_PATH) != manifest["work_plaintext_sha256"]:
        raise AssertionError("work file SHA-256 differs from manifest")
    current_head = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=True,
        capture_output=True,
        text=True,
    ).stdout.strip()
    if current_head != manifest["git_hash"]:
        raise AssertionError("current git hash differs from custodian manifest")
    for filename, expected_hash in manifest["generation_code_sha256"].items():
        if sha256_file(Path(__file__).with_name(filename)) != expected_hash:
            raise AssertionError(f"generation code hash differs: {filename}")
    return manifest, permtest


def analyze(outcomes: pd.DataFrame) -> dict[str, Any]:
    horizon_tests = {
        horizon: _mean_test(outcomes, f"car_{horizon}h") for horizon in HORIZONS
    }
    valid_48 = outcomes["car_48h"].notna()
    monotonicity = moving_block_spearman_test(
        outcomes.loc[valid_48, "event_time"],
        pd.to_numeric(outcomes.loc[valid_48, "severity_code"], errors="coerce"),
        pd.to_numeric(outcomes.loc[valid_48, "car_48h"], errors="coerce"),
        replications=BOOTSTRAP_REPLICATIONS,
        seed=SEED,
    )
    nonoverlap = outcomes.loc[
        pd.to_numeric(outcomes["a2_overlap"], errors="coerce") == 0
    ].copy()
    overlap = outcomes.loc[
        pd.to_numeric(outcomes["a2_overlap"], errors="coerce") == 1
    ].copy()
    nonoverlap_test = _mean_test(nonoverlap, "car_48h")
    overlap_test = _mean_test(overlap, "car_48h")

    raw_family = {
        "car_48h": (
            None if horizon_tests[48] is None else horizon_tests[48].p_value
        ),
        "car_24h": (
            None if horizon_tests[24] is None else horizon_tests[24].p_value
        ),
        "monotonicity": None if monotonicity is None else monotonicity.p_value,
        "nonoverlap_48h": (
            None if nonoverlap_test is None else nonoverlap_test.p_value
        ),
    }
    adjusted = holm_adjust(raw_family)
    gates = {
        "car_48h": _gate_status(horizon_tests[48], adjusted["car_48h"]),
        "car_24h": _gate_status(horizon_tests[24], adjusted["car_24h"]),
        "monotonicity": _gate_status(monotonicity, adjusted["monotonicity"]),
        "nonoverlap_48h": _gate_status(
            nonoverlap_test, adjusted["nonoverlap_48h"]
        ),
    }
    wf = wf_stability(outcomes)
    required = [
        gates["car_48h"],
        gates["monotonicity"],
        gates["nonoverlap_48h"],
        str(wf["status"]),
    ]
    verdict = "PASS" if all(item == "PASS" for item in required) else "FAILED"

    p_overlap_denominator = int(outcomes["a2_overlap"].notna().sum())
    p_overlap = (
        float(pd.to_numeric(outcomes["a2_overlap"], errors="coerce").sum())
        / p_overlap_denominator
        if p_overlap_denominator
        else None
    )
    power = {
        str(horizon): power_diagnostic(outcomes, horizon=horizon)
        for horizon in HORIZONS
    }
    power["nonoverlap_48h"] = power_diagnostic(nonoverlap, horizon=48)
    group_diagnostics = []
    for (symbol, regime), group in outcomes.groupby(["symbol", "regime"], dropna=False):
        values = pd.to_numeric(group["car_48h"], errors="coerce").dropna()
        group_diagnostics.append(
            {
                "symbol": str(symbol),
                "regime": str(regime),
                "n_48h": int(len(values)),
                "mean_car_48h": float(values.mean()) if len(values) else None,
            }
        )
    return {
        "verdict": verdict,
        "horizons": {
            str(horizon): _bootstrap_payload(horizon_tests[horizon])
            for horizon in HORIZONS
        },
        "monotonicity": _bootstrap_payload(monotonicity),
        "nonoverlap_48h": _bootstrap_payload(nonoverlap_test),
        "overlap_48h": _bootstrap_payload(overlap_test),
        "holm_adjusted_p": adjusted,
        "gates": gates,
        "wf": wf,
        "p_overlap": p_overlap,
        "overlap_rows": int(len(overlap)),
        "nonoverlap_rows": int(len(nonoverlap)),
        "power": power,
        "cost_diagnostic": {
            "n_48h": int(outcomes["net_car_48h_base"].notna().sum()),
            "mean_net_car_48h_base": (
                float(outcomes["net_car_48h_base"].mean())
                if outcomes["net_car_48h_base"].notna().any()
                else None
            ),
            "mean_net_car_48h_slip_030": (
                float(outcomes["net_car_48h_slip_030"].mean())
                if outcomes["net_car_48h_slip_030"].notna().any()
                else None
            ),
            "mean_holding_funding_48h": (
                float(outcomes["holding_funding_48h"].mean())
                if outcomes["holding_funding_48h"].notna().any()
                else None
            ),
        },
        "symbol_regime_diagnostic": group_diagnostics,
    }


def _pct(value: float | None) -> str:
    return "N.A." if value is None else f"{100 * value:.4f}%"


def _num(value: float | None, digits: int = 6) -> str:
    return "N.A." if value is None else f"{value:.{digits}f}"


def _test_cells(
    payload: dict[str, Any] | None,
    adjusted_p: float | None,
) -> tuple[str, str, str, str]:
    if payload is None:
        return "N.A.", "N.A.", "N.A.", "N.A."
    return (
        _pct(payload["estimate"]),
        _num(payload["raw_p"]),
        _num(adjusted_p),
        f"[{_pct(payload['ci_low'])}, {_pct(payload['ci_high'])}]",
    )


def render_report(
    analysis: dict[str, Any],
    manifest: dict[str, Any],
    manifest_sha: str,
    outcomes: pd.DataFrame,
) -> str:
    verdict = analysis["verdict"]
    if verdict == "PASS":
        top = "Tier A PASS（可观测条件回弹关联成立，探索级）"
        cto = "对 CTO 的提示：本结果支持继续投路径B 确证机制"
    else:
        top = "Tier A FAILED"
        cto = "对 CTO 的提示：本结果不支持继续投路径B 确证机制"

    h48 = analysis["horizons"]["48"]
    h24 = analysis["horizons"]["24"]
    h72 = analysis["horizons"]["72"]
    mono = analysis["monotonicity"]
    nonoverlap = analysis["nonoverlap_48h"]

    def reference_neff(label: str) -> str:
        entries = analysis["power"].get(label, [])
        reference = next(
            (item for item in entries if math.isclose(item["icc"], 0.5)),
            None,
        )
        return "N.A." if reference is None else f"{reference['n_eff']:.2f}"

    rows = [
        (
            "48h CAR（硬门）",
            analysis["gates"]["car_48h"],
            *_test_cells(h48, analysis["holm_adjusted_p"]["car_48h"]),
            "-" if h48 is None else str(h48["n"]),
            reference_neff("48"),
        ),
        (
            "24h CAR（family 次项，非独立硬门）",
            analysis["gates"]["car_24h"],
            *_test_cells(h24, analysis["holm_adjusted_p"]["car_24h"]),
            "-" if h24 is None else str(h24["n"]),
            reference_neff("24"),
        ),
        (
            "48h severity Spearman（硬门）",
            analysis["gates"]["monotonicity"],
            *_test_cells(mono, analysis["holm_adjusted_p"]["monotonicity"]),
            "-" if mono is None else str(mono["n"]),
            "N.A.",
        ),
        (
            "A-2 non-overlap 48h（硬门）",
            analysis["gates"]["nonoverlap_48h"],
            *_test_cells(
                nonoverlap, analysis["holm_adjusted_p"]["nonoverlap_48h"]
            ),
            "-" if nonoverlap is None else str(nonoverlap["n"]),
            reference_neff("nonoverlap_48h"),
        ),
        (
            "WF 稳定性（硬门）",
            analysis["wf"]["status"],
            f"{analysis['wf']['positive_segments']}/3 正",
            "N.A.",
            "N.A.",
            "N.A.",
            "/".join(str(item["n_car"]) for item in analysis["wf"]["segments"]),
            "N.A.",
        ),
        (
            "权限/口径完整性（硬门）",
            "PASS",
            "SHA 与负向测试通过",
            "N.A.",
            "N.A.",
            "N.A.",
            str(len(outcomes)),
            "N.A.",
        ),
    ]
    table = [
        "| 项目 | 判决 | 估计/数值 | raw p | Holm p | basic 95% CI | n | n_eff (ICC=0.5) |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    table.extend("| " + " | ".join(row) + " |" for row in rows)

    power_lines = [
        "| 样本 | ICC | n | n_eff | sigma_pre_h | 80% MDE |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for label, entries in analysis["power"].items():
        for item in entries:
            power_lines.append(
                "| "
                + " | ".join(
                    [
                        label,
                        f"{item['icc']:.1f}",
                        str(item["n"]),
                        f"{item['n_eff']:.2f}",
                        _pct(item["sigma_pre_h"]),
                        _pct(item["mde_80"]),
                    ]
                )
                + " |"
            )

    wf_lines = [
        "| 段 | purge 前 n | purge n | CAR n | 48h 裸均值 |",
        "|---:|---:|---:|---:|---:|",
    ]
    for item in analysis["wf"]["segments"]:
        wf_lines.append(
            f"| {item['segment']} | {item['n_before_purge']} | "
            f"{item['n_purged']} | {item['n_car']} | "
            f"{_pct(item['mean_car_48h'])} |"
        )

    cost = analysis["cost_diagnostic"]
    overlap = analysis["overlap_48h"]
    return "\n".join(
        [
            top,
            "",
            "# A-1 Tier A 历史关联快筛",
            "",
            "## §11 Decision Table",
            "",
            *table,
            "",
            f"- 最终判决：**{verdict}**。",
            f"- 72h 探索项：mean={_pct(None if h72 is None else h72['estimate'])}, "
            f"raw p={_num(None if h72 is None else h72['raw_p'])}, "
            f"n={0 if h72 is None else h72['n']}；不参与判决。",
            "",
            "## A-2 重叠诊断",
            "",
            f"- p_overlap={_pct(analysis['p_overlap'])}；"
            f"overlap rows={analysis['overlap_rows']}；"
            f"non-overlap rows={analysis['nonoverlap_rows']}。",
            f"- overlap 48h：mean={_pct(None if overlap is None else overlap['estimate'])}, "
            f"raw p={_num(None if overlap is None else overlap['raw_p'])}, "
            f"n={0 if overlap is None else overlap['n']}。",
            "",
            "## WF",
            "",
            *wf_lines,
            "",
            "## 功效诊断",
            "",
            *power_lines,
            "",
            "## 成本诊断",
            "",
            f"- 48h base net CAR mean={_pct(cost['mean_net_car_48h_base'])}。",
            f"- 48h 0.30%/边滑点 net CAR mean="
            f"{_pct(cost['mean_net_car_48h_slip_030'])}。",
            f"- 48h 实际 funding cost mean="
            f"{_pct(cost['mean_holding_funding_48h'])}。",
            "",
            "## 封存审计",
            "",
            f"- work rows={manifest['work_rows']}；sealed rows={manifest['sealed_rows']}。",
            f"- manifest SHA-256=`{manifest_sha}`。",
            "- 负向权限测试：PASS（manifest 可读；执行身份无法打开密钥，解密未发生）。",
            "- work episodes 由 custodian 按 v5 生成：使用名义 OI、6h 有效观测谓词、"
            "纯方向 MARK 条件与 24h refractory；executor 未重建或修改触发。",
            "- 事件后 CAR 仅由 work 文件计算；市场文件读取在 "
            "`2024-12-10T00:00:00Z` 前停止。",
            "",
            cto,
            "",
        ]
    )


def main() -> None:
    manifest, _ = verify_release_boundary()
    work = load_work()
    if len(work) != int(manifest["work_rows"]):
        raise AssertionError("work row count differs from manifest")
    marks = {symbol: load_mark(symbol) for symbol in SYMBOLS}
    funding = {symbol: load_funding(symbol) for symbol in SYMBOLS}
    outcomes = compute_episode_outcomes(work, marks, funding)
    analysis = analyze(outcomes)
    analysis["metadata"] = {
        "task_id": "A1_TIERA_EXEC",
        "generated_at_utc": pd.Timestamp.now(tz="UTC").strftime(
            "%Y-%m-%dT%H:%M:%SZ"
        ),
        "seed": SEED,
        "bootstrap_replications": BOOTSTRAP_REPLICATIONS,
        "work_rows": int(len(work)),
        "manifest_sha256": sha256_file(MANIFEST_PATH),
    }
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    JSON_PATH.write_text(
        json.dumps(analysis, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    REPORT_PATH.write_text(
        render_report(
            analysis,
            manifest,
            sha256_file(MANIFEST_PATH),
            outcomes,
        ),
        encoding="utf-8",
    )
    h48 = analysis["horizons"]["48"]
    inbox = {
        "task_id": "A1_TIERA_EXEC",
        "completed_at": pd.Timestamp.now(tz="UTC").isoformat().replace("+00:00", "Z"),
        "status": "completed",
        "verdict": analysis["verdict"],
        "output_file": str(REPORT_PATH.relative_to(ROOT)),
        "next_task": None,
        "notes": (
            f"48h mean={None if h48 is None else h48['estimate']}; "
            f"Holm p={analysis['holm_adjusted_p']['car_48h']}; "
            f"判断={'支持' if analysis['verdict'] == 'PASS' else '不支持'}"
            "继续投路径B前向确证。"
        ),
    }
    TASK_INBOX_PATH.parent.mkdir(parents=True, exist_ok=True)
    TASK_INBOX_PATH.write_text(
        json.dumps(inbox, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(analysis["metadata"] | {"verdict": analysis["verdict"]}, indent=2))


if __name__ == "__main__":
    main()
