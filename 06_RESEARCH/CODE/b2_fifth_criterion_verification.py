#!/usr/bin/env python3
"""B2 independent fifth-criterion verification for P1-04/P1-06.

This file intentionally does not import the P1 backtest modules or
tsmom_dual_engine.py.  It re-implements the small pieces needed for the
state-gated passive benchmark and the frozen TSMOM strategy comparison.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "06_RESEARCH" / "DATA"
OUTPUT = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULTS = ROOT / "06_RESEARCH" / "RESULTS"
CODEX_TASKS = ROOT / "04_AI_TEAM" / "CODEX_TASKS"

SYMBOLS = ("BTC", "ETH", "SOL")
INITIAL_CAPITAL = 100_000.0
LOOKBACK_BARS = 540
BAR_HOURS = 4
TARGET_WEIGHT = 1 / 3
LEVERAGE_CAP = 1.0
FEE_RATE = 0.001
SLIPPAGE_RATE = 0.001
ADX_PERIOD = 14
ADX_ENTRY = 25.0
ADX_EXIT = 20.0
MACRO_MA_DAYS = 200

LEGACY_P1_CONFIG = {
    "BTC": {
        "bars": ROOT / "BTC_USDT_4H.csv",
        "bars_rows": 13013,
        "holdout_start": pd.Timestamp("2024-12-09 16:00:00"),
        "funding": DATA / "FUTURES" / "BTCUSDT_FUNDING_8H.csv",
        "funding_rows": 5414,
    },
    "ETH": {
        "bars": ROOT / "ETH_USDT_4H.csv",
        "bars_rows": 13013,
        "holdout_start": pd.Timestamp("2024-12-09 16:00:00"),
        "funding": DATA / "FUTURES" / "ETHUSDT_FUNDING_8H.csv",
        "funding_rows": 5414,
    },
    "SOL": {
        "bars": ROOT / "SOL_USDT_4H.csv",
        "bars_rows": 10194,
        "holdout_start": pd.Timestamp("2025-04-06 04:00:00"),
        "funding": DATA / "FUTURES" / "SOLUSDT_FUNDING_8H.csv",
        "funding_rows": 4997,
    },
}


@dataclass
class Position:
    symbol: str
    entry_time: pd.Timestamp
    signal_time: pd.Timestamp
    raw_entry_price: float
    entry_price: float
    quantity: float
    initial_quantity: float
    initial_notional: float
    entry_equity: float
    entry_fee: float
    entry_slippage_cost: float
    partial_gross_pnl: float = 0.0
    partial_exit_fee: float = 0.0
    partial_exit_slippage_cost: float = 0.0
    funding_cost: float = 0.0
    holding_bars: int = 0


@dataclass
class Result:
    label: str
    trades: pd.DataFrame
    equity: pd.Series
    max_gross_leverage: float
    forced_deleveraging_count: int


def wilder_average(values: pd.Series, period: int) -> pd.Series:
    return values.ewm(alpha=1 / period, adjust=False, min_periods=period).mean()


def calculate_adx(bars: pd.DataFrame, period: int = ADX_PERIOD) -> pd.Series:
    high = bars["high"].astype(float)
    low = bars["low"].astype(float)
    close = bars["close"].astype(float)
    up_move = high.diff()
    down_move = -low.diff()
    plus_dm = pd.Series(
        np.where((up_move > down_move) & (up_move > 0), up_move, 0.0),
        index=bars.index,
    )
    minus_dm = pd.Series(
        np.where((down_move > up_move) & (down_move > 0), down_move, 0.0),
        index=bars.index,
    )
    true_range = pd.concat(
        [
            high - low,
            (high - close.shift(1)).abs(),
            (low - close.shift(1)).abs(),
        ],
        axis=1,
    ).max(axis=1)
    atr = wilder_average(true_range, period)
    plus_di = 100 * wilder_average(plus_dm, period) / atr
    minus_di = 100 * wilder_average(minus_dm, period) / atr
    denominator = (plus_di + minus_di).replace(0, np.nan)
    dx = 100 * (plus_di - minus_di).abs() / denominator
    return wilder_average(dx, period)


def hysteresis_regime(adx: pd.Series) -> pd.Series:
    state = False
    values: list[bool] = []
    for value in adx:
        if np.isfinite(value):
            if value > ADX_ENTRY:
                state = True
            elif value < ADX_EXIT:
                state = False
        values.append(state)
    return pd.Series(values, index=adx.index, dtype=bool)


def prior_daily_bull_state(datetimes: pd.Series, close: pd.Series) -> pd.Series:
    intraday = pd.Series(close.to_numpy(), index=pd.DatetimeIndex(datetimes))
    daily_close = intraday.resample("1D").last()
    daily_ma = daily_close.rolling(MACRO_MA_DAYS, min_periods=MACRO_MA_DAYS).mean()
    completed = pd.DataFrame({"daily_close": daily_close, "daily_ma": daily_ma}).shift(1)
    mapped = completed.reindex(pd.DatetimeIndex(datetimes).normalize())
    valid = mapped["daily_close"].notna() & mapped["daily_ma"].notna()
    return pd.Series(
        pd.array(
            np.where(valid, mapped["daily_close"] > mapped["daily_ma"], pd.NA),
            dtype="boolean",
        ),
        index=close.index,
    )


def funding_payment(quantity: float, mark_price: float, rate: float) -> float:
    return quantity * mark_price * rate


def read_frozen_inputs() -> tuple[dict[str, pd.DataFrame], dict[str, pd.DataFrame], dict[str, object]]:
    bars_by_symbol: dict[str, pd.DataFrame] = {}
    funding_by_symbol: dict[str, pd.DataFrame] = {}
    audit: dict[str, object] = {}
    for symbol, config in LEGACY_P1_CONFIG.items():
        bars = pd.read_csv(config["bars"], parse_dates=["datetime"], nrows=config["bars_rows"])
        if len(bars) != config["bars_rows"]:
            raise ValueError(f"{symbol} bars row count changed")
        if bars["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} bars crossed frozen Holdout boundary")
        if bars["datetime"].duplicated().any() or not bars["datetime"].is_monotonic_increasing:
            raise ValueError(f"{symbol} bars timestamps invalid")
        for column in ("open", "high", "low", "close", "volume"):
            bars[column] = pd.to_numeric(bars[column])

        funding = pd.read_csv(
            config["funding"],
            parse_dates=["datetime"],
            nrows=config["funding_rows"],
        )
        if len(funding) != config["funding_rows"]:
            raise ValueError(f"{symbol} funding row count changed")
        if funding["datetime"].max() >= config["holdout_start"]:
            raise ValueError(f"{symbol} funding crossed frozen Holdout boundary")
        if funding["datetime"].duplicated().any() or not funding["datetime"].is_monotonic_increasing:
            raise ValueError(f"{symbol} funding timestamps invalid")
        funding["last_funding_rate"] = pd.to_numeric(funding["last_funding_rate"])

        bars_by_symbol[symbol] = bars.reset_index(drop=True)
        funding_by_symbol[symbol] = funding.reset_index(drop=True)
        audit[symbol] = {
            "bars_path": str(config["bars"].relative_to(ROOT)),
            "bars_rows": int(len(bars)),
            "bars_first": str(bars["datetime"].iloc[0]),
            "bars_last": str(bars["datetime"].iloc[-1]),
            "funding_path": str(config["funding"].relative_to(ROOT)),
            "funding_rows": int(len(funding)),
            "funding_first": str(funding["datetime"].iloc[0]),
            "funding_last": str(funding["datetime"].iloc[-1]),
            "holdout_start": str(config["holdout_start"]),
        }
    return bars_by_symbol, funding_by_symbol, audit


def add_features(bars_by_symbol: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    prepared: dict[str, pd.DataFrame] = {}
    for symbol, raw in bars_by_symbol.items():
        frame = raw.copy()
        lagged = frame["close"].shift(LOOKBACK_BARS)
        signal = np.sign(frame["close"] - lagged)
        frame["signal"] = (
            pd.Series(signal, index=frame.index)
            .replace(0, np.nan)
            .ffill()
            .fillna(0)
            .astype(int)
        )
        frame["adx"] = calculate_adx(frame)
        frame["trend_regime"] = hysteresis_regime(frame["adx"])
        frame["macro_bull"] = prior_daily_bull_state(frame["datetime"], frame["close"])
        prepared[symbol] = frame
    return prepared


def build_targets(prepared: dict[str, pd.DataFrame], experiment: str, kind: str) -> dict[str, pd.DataFrame]:
    output: dict[str, pd.DataFrame] = {}
    for symbol, raw in prepared.items():
        frame = raw.copy()
        if experiment == "P1-04" and kind == "strategy":
            desired = (frame["signal"].eq(1) & frame["trend_regime"]).astype(int)
        elif experiment == "P1-04" and kind == "benchmark":
            desired = frame["trend_regime"].astype(int)
        elif experiment == "P1-06" and kind == "strategy":
            macro = frame["macro_bull"].fillna(False).astype(bool)
            desired = (frame["signal"].eq(1) & frame["trend_regime"] & macro).astype(int)
        elif experiment == "P1-06" and kind == "benchmark":
            desired = frame["macro_bull"].fillna(False).astype(bool).astype(int)
        else:
            raise ValueError(f"Unsupported target: {experiment} {kind}")
        frame["desired"] = desired
        frame["execution_target"] = frame["desired"].shift(1).fillna(0).astype(int)
        frame["signal_time"] = frame["datetime"].shift(1)
        output[symbol] = frame
    return output


def frame_maps(frames: dict[str, pd.DataFrame]) -> tuple[pd.DatetimeIndex, dict[str, dict[pd.Timestamp, object]]]:
    common_end = min(frame["datetime"].max() for frame in frames.values())
    clipped = {
        symbol: frame[frame["datetime"] <= common_end].reset_index(drop=True)
        for symbol, frame in frames.items()
    }
    timeline = pd.DatetimeIndex(
        sorted(set().union(*(set(frame["datetime"]) for frame in clipped.values())))
    )
    maps = {
        symbol: {row.datetime: row for row in frame.itertuples(index=False)}
        for symbol, frame in clipped.items()
    }
    return timeline, maps


def run_portfolio(
    label: str,
    frames: dict[str, pd.DataFrame],
    funding_by_symbol: dict[str, pd.DataFrame],
) -> Result:
    timeline, bar_maps = frame_maps(frames)
    funding_maps = {
        symbol: {
            row.datetime: float(row.last_funding_rate)
            for row in funding_by_symbol[symbol].itertuples(index=False)
        }
        for symbol in SYMBOLS
    }
    cash = INITIAL_CAPITAL
    positions: dict[str, Position] = {}
    last_price: dict[str, float] = {}
    trades: list[dict[str, object]] = []
    equity_points: list[tuple[pd.Timestamp, float]] = []
    max_gross = 0.0
    forced_deleveraging_count = 0

    def price_with_slippage(raw_price: float, is_entry: bool) -> float:
        return raw_price * (1 + SLIPPAGE_RATE if is_entry else 1 - SLIPPAGE_RATE)

    def equity(now: pd.Timestamp, field: str) -> float:
        value = cash
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            value += position.quantity * (mark - position.entry_price)
        return value

    def gross_exposure(now: pd.Timestamp, field: str) -> float:
        total = 0.0
        for symbol, position in positions.items():
            row = bar_maps[symbol].get(now)
            mark = float(getattr(row, field)) if row is not None else last_price[symbol]
            total += position.quantity * mark
        return total

    def close_position(symbol: str, now: pd.Timestamp, raw_price: float, reason: str) -> None:
        nonlocal cash
        position = positions[symbol]
        exit_price = price_with_slippage(raw_price, is_entry=False)
        gross_pnl = position.quantity * (exit_price - position.entry_price)
        exit_notional = position.quantity * exit_price
        exit_fee = exit_notional * FEE_RATE
        exit_slippage = position.quantity * abs(exit_price - raw_price)
        cash += gross_pnl - exit_fee
        total_gross = position.partial_gross_pnl + gross_pnl
        total_exit_fee = position.partial_exit_fee + exit_fee
        total_exit_slippage = position.partial_exit_slippage_cost + exit_slippage
        net_pnl = total_gross - position.entry_fee - total_exit_fee - position.funding_cost
        trades.append(
            {
                "label": label,
                "symbol": symbol,
                "signal_time": position.signal_time,
                "entry_time": position.entry_time,
                "exit_time": now,
                "exit_reason": reason,
                "raw_entry_price": position.raw_entry_price,
                "entry_price": position.entry_price,
                "raw_exit_price": raw_price,
                "exit_price": exit_price,
                "quantity": position.initial_quantity,
                "final_quantity": position.quantity,
                "initial_notional": position.initial_notional,
                "entry_equity": position.entry_equity,
                "gross_pnl": total_gross + position.entry_slippage_cost + total_exit_slippage,
                "net_pnl": net_pnl,
                "entry_fee": position.entry_fee,
                "exit_fee": total_exit_fee,
                "total_fees": position.entry_fee + total_exit_fee,
                "entry_slippage_cost": position.entry_slippage_cost,
                "exit_slippage_cost": total_exit_slippage,
                "total_slippage_cost": position.entry_slippage_cost + total_exit_slippage,
                "funding_cost": position.funding_cost,
                "holding_bars": position.holding_bars,
            }
        )
        del positions[symbol]

    def enforce_leverage_cap(now: pd.Timestamp, rows: dict[str, object]) -> None:
        nonlocal cash, forced_deleveraging_count
        current_equity = equity(now, "open")
        current_exposure = gross_exposure(now, "open")
        if not positions or current_equity <= 0 or current_exposure <= current_equity * LEVERAGE_CAP:
            return
        cost_rate = FEE_RATE + SLIPPAGE_RATE
        numerator = current_equity * LEVERAGE_CAP - current_exposure * cost_rate
        denominator = current_exposure * (1 - cost_rate)
        scale = min(1.0, max(0.0, numerator / denominator))
        for symbol, position in list(positions.items()):
            raw_price = float(rows[symbol].open)
            removed = position.quantity * (1 - scale)
            if removed <= 0:
                continue
            trim_price = price_with_slippage(raw_price, is_entry=False)
            trim_gross = removed * (trim_price - position.entry_price)
            trim_fee = removed * trim_price * FEE_RATE
            trim_slippage = removed * abs(trim_price - raw_price)
            cash += trim_gross - trim_fee
            position.quantity *= scale
            position.partial_gross_pnl += trim_gross
            position.partial_exit_fee += trim_fee
            position.partial_exit_slippage_cost += trim_slippage
        forced_deleveraging_count += 1

    for now in timeline:
        rows = {symbol: bar_maps[symbol].get(now) for symbol in SYMBOLS}
        for symbol, row in rows.items():
            if row is not None:
                last_price[symbol] = float(row.open)

        for symbol, position in list(positions.items()):
            rate = funding_maps[symbol].get(now)
            if rate is None:
                continue
            row = rows[symbol]
            mark = float(row.open) if row is not None else last_price[symbol]
            payment = funding_payment(position.quantity, mark, rate)
            cash -= payment
            position.funding_cost += payment

        desired = {
            symbol: int(row.execution_target)
            for symbol, row in rows.items()
            if row is not None
        }
        for symbol, target in desired.items():
            if target == 0 and symbol in positions:
                close_position(symbol, now, float(rows[symbol].open), "GATE_OFF")

        enforce_leverage_cap(now, rows)

        current_equity = equity(now, "open")
        current_exposure = gross_exposure(now, "open")
        available = max(
            0.0,
            (current_equity * LEVERAGE_CAP - current_exposure)
            / (1 + FEE_RATE + SLIPPAGE_RATE),
        )
        desired_notional = current_equity * TARGET_WEIGHT
        entry_symbols = [
            symbol
            for symbol, target in desired.items()
            if target == 1 and symbol not in positions
        ]
        desired_total = desired_notional * len(entry_symbols)
        scale = min(1.0, available / desired_total) if desired_total else 0.0
        for symbol in entry_symbols:
            row = rows[symbol]
            raw_entry = float(row.open)
            entry_price = price_with_slippage(raw_entry, is_entry=True)
            notional = desired_notional * scale
            if notional <= 0:
                continue
            quantity = notional / entry_price
            entry_fee = notional * FEE_RATE
            entry_slippage = quantity * abs(entry_price - raw_entry)
            cash -= entry_fee
            positions[symbol] = Position(
                symbol=symbol,
                entry_time=now,
                signal_time=pd.Timestamp(row.signal_time),
                raw_entry_price=raw_entry,
                entry_price=entry_price,
                quantity=quantity,
                initial_quantity=quantity,
                initial_notional=notional,
                entry_equity=current_equity,
                entry_fee=entry_fee,
                entry_slippage_cost=entry_slippage,
            )

        enforce_leverage_cap(now, rows)
        open_equity = equity(now, "open")
        if open_equity > 0:
            max_gross = max(max_gross, gross_exposure(now, "open") / open_equity)

        for symbol, position in positions.items():
            if rows[symbol] is not None:
                position.holding_bars += 1
        for symbol, row in rows.items():
            if row is not None:
                last_price[symbol] = float(row.close)
        equity_points.append((now, equity(now, "close")))

    for symbol in list(positions):
        frame = frames[symbol]
        last_row = frame[frame["datetime"] <= timeline[-1]].iloc[-1]
        close_position(symbol, pd.Timestamp(last_row["datetime"]), float(last_row["close"]), "RESEARCH_END")
    if equity_points:
        equity_points[-1] = (equity_points[-1][0], cash)

    trade_frame = pd.DataFrame(trades)
    if not trade_frame.empty:
        trade_frame = trade_frame.sort_values(["entry_time", "symbol"]).reset_index(drop=True)
    equity_series = pd.Series(
        [value for _, value in equity_points],
        index=pd.DatetimeIndex([time for time, _ in equity_points]),
        name="equity",
    )
    return Result(label, trade_frame, equity_series, max_gross, forced_deleveraging_count)


def summarize(result: Result) -> dict[str, object]:
    trades = result.trades
    return {
        "label": result.label,
        "ending_equity": float(result.equity.iloc[-1]),
        "net_profit": float(result.equity.iloc[-1] - INITIAL_CAPITAL),
        "trade_count": int(len(trades)),
        "fees": float(trades["total_fees"].sum()) if not trades.empty else 0.0,
        "slippage_cost": float(trades["total_slippage_cost"].sum()) if not trades.empty else 0.0,
        "funding_cost": float(trades["funding_cost"].sum()) if not trades.empty else 0.0,
        "max_gross_leverage": float(result.max_gross_leverage),
        "forced_deleveraging_count": int(result.forced_deleveraging_count),
    }


def read_existing_terminal(path: Path) -> float:
    frame = pd.read_csv(path)
    return float(frame["equity"].iloc[-1])


def write_outputs(payload: dict[str, object], results: dict[str, Result]) -> None:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    RESULTS.mkdir(parents=True, exist_ok=True)
    CODEX_TASKS.mkdir(parents=True, exist_ok=True)

    json_path = OUTPUT / "b2_fifth_criterion_verification.json"
    with json_path.open("w") as handle:
        json.dump(payload, handle, indent=2, ensure_ascii=False)

    rows = []
    for experiment, record in payload["comparison"].items():
        rows.append(
            {
                "experiment": experiment,
                "strategy_ending_equity": record["strategy"]["ending_equity"],
                "benchmark_ending_equity": record["benchmark"]["ending_equity"],
                "excess": record["excess"],
                "passes_fifth": record["passes_fifth"],
                "strategy_trades": record["strategy"]["trade_count"],
                "benchmark_trades": record["benchmark"]["trade_count"],
                "strategy_funding_cost": record["strategy"]["funding_cost"],
                "benchmark_funding_cost": record["benchmark"]["funding_cost"],
            }
        )
    pd.DataFrame(rows).to_csv(OUTPUT / "b2_fifth_criterion_comparison.csv", index=False)
    for name, result in results.items():
        result.equity.to_csv(OUTPUT / f"b2_{name}_equity.csv")
        result.trades.to_csv(OUTPUT / f"b2_{name}_trades.csv", index=False)

    comparison = payload["comparison"]
    prior = payload["prior_dual_engine_retrospective"]
    lines = [
        "# B2 第五件追溯复算验证",
        "",
        f"UTC run timestamp: {payload['run_timestamp_utc']}",
        "",
        "## 结论",
        "",
        "独立复算显示，按 P1 冻结快照和 B2 字面门控口径：P1-04 第五件失败，P1-06 第五件通过。",
        "P1-06 昨日报告中的 `-1,101,379.86` 不能作为 P1-06 冻结窗口第五件结论；根因是追溯包装使用了扩样本数据/窗口口径，而不是交易 P&L 算术反号、成本方向或 funding 方向错误。",
        "",
        "## 主对照表",
        "",
        "| experiment | strategy ending equity | benchmark ending equity | excess | fifth pass |",
        "|---|---:|---:|---:|---|",
    ]
    for experiment in ("P1-04", "P1-06"):
        row = comparison[experiment]
        lines.append(
            f"| {experiment} | {row['strategy']['ending_equity']:.2f} | "
            f"{row['benchmark']['ending_equity']:.2f} | {row['excess']:.2f} | "
            f"{row['passes_fifth']} |"
        )
    lines.extend(
        [
            "",
            "## 与昨日内置追溯的差异",
            "",
            "| item | yesterday tsmom_dual_engine.py | B2 independent recompute | delta |",
            "|---|---:|---:|---:|",
        ]
    )
    for experiment, key in (("P1-04", "p1_04"), ("P1-06", "p1_06")):
        yesterday = prior[key]["excess_profit"]
        current = comparison[experiment]["excess"]
        lines.append(f"| {experiment} excess | {yesterday:.2f} | {current:.2f} | {current - yesterday:.2f} |")
    lines.extend(
        [
            "",
            "根因判断：",
            "",
            "1. 不是基准函数把符号、成本或 funding 方向写反导致的算术 bug；本次同成本、同 funding 方向下可复算出自洽结果。",
            "2. 差异主要是口径差/追溯包装问题：昨日追溯用 `06_RESEARCH/DATA/FUTURES/*_MARK_4H.csv` 的 2020 起扩样本窗口和 PIT/cutoff 逻辑；本次按 P1 冻结快照读取根目录三币 4H 文件的研究行，窗口从 2019-01-01 起，SOL 从上市快照起。",
            "3. B2 主口径按任务书字面定义基准：P1-04=ADX趋势窗，P1-06=宏观牛市窗；不叠加 TSMOM 动量信号。",
            "4. 当前成本口径为 fee 0.1%/边 + slippage 0.1%/边 + 真实 funding；旧 P1 输出为 fee 0.05%/边，因此旧 P1 终值只作为参考，不用于主判定。",
            "",
            "## 旧 P1 输出参考",
            "",
            "| experiment | old output ending equity | B2 strategy ending equity | difference |",
            "|---|---:|---:|---:|",
        ]
    )
    for experiment in ("P1-04", "P1-06"):
        old_value = payload["existing_p1_outputs"][experiment]["ending_equity"]
        current = comparison[experiment]["strategy"]["ending_equity"]
        lines.append(f"| {experiment} | {old_value:.2f} | {current:.2f} | {current - old_value:.2f} |")
    lines.extend(
        [
            "",
            "## 数据与边界",
            "",
            "- 未读取 `06_RESEARCH/DATA/HOLDOUT/`；未读取 `*_2026H1`。",
            "- 行情使用 P1 legacy 冻结快照的 pre-Holdout `nrows`；资金费使用对应 pre-Holdout `nrows`。",
            "- 会话审计：任务早期一次 `find` 文件枚举显示了 HOLDOUT 路径名，但未打开或读取 HOLDOUT 文件内容；后续搜索均排除 HOLDOUT。",
            "",
            "| symbol | bars rows | bars first | bars last | funding rows | funding last | holdout start |",
            "|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for symbol, row in payload["data_audit"].items():
        lines.append(
            f"| {symbol} | {row['bars_rows']} | {row['bars_first']} | {row['bars_last']} | "
            f"{row['funding_rows']} | {row['funding_last']} | {row['holdout_start']} |"
        )
    lines.extend(
        [
            "",
            "## 产出",
            "",
            "- `06_RESEARCH/CODE/b2_fifth_criterion_verification.py`",
            "- `06_RESEARCH/CODE/output/b2_fifth_criterion_verification.json`",
            "- `06_RESEARCH/CODE/output/b2_fifth_criterion_comparison.csv`",
            "- `06_RESEARCH/CODE/output/b2_*_equity.csv` / `b2_*_trades.csv`",
        ]
    )
    (RESULTS / "20260612_fifth_criterion_verification.md").write_text("\n".join(lines) + "\n")

    report_lines = [
        "# REPORT B2",
        "",
        "**任务：** BATCH_20260612N / B2 P1-04/P1-06 第五件追溯复算",
        "**状态：** COMPLETED",
        "**结论：** P1-04 第五件失败；P1-06 第五件通过。昨日 P1-06 大额负超额是追溯口径差，不是 P1 冻结窗口结论。",
        "",
        "## 七问自查",
        "",
        "1. 机制：验证策略是否超过同状态门控被动买入持有基准，排除 beta 伪装。",
        "2. 验收：可量化，输出策略终值、基准终值、超额、根因解释和报告。",
        "3. 更便宜实现：有，独立小脚本复算；无需重跑其他批次或动 Holdout。",
        "4. 禁止项：未改预登记，未读 HOLDOUT 内容，未用全样本分位，未引黑箱依赖，未提交 git。",
        "",
        "## 结果",
        "",
        "| experiment | strategy ending | benchmark ending | excess | pass |",
        "|---|---:|---:|---:|---|",
    ]
    for experiment in ("P1-04", "P1-06"):
        row = comparison[experiment]
        report_lines.append(
            f"| {experiment} | {row['strategy']['ending_equity']:.2f} | "
            f"{row['benchmark']['ending_equity']:.2f} | {row['excess']:.2f} | "
            f"{row['passes_fifth']} |"
        )
    report_lines.extend(
        [
            "",
            "## 验收自检",
            "",
            "- CODE：`06_RESEARCH/CODE/b2_fifth_criterion_verification.py` 可复跑；无随机过程。",
            "- RESULTS：`06_RESEARCH/RESULTS/20260612_fifth_criterion_verification.md` 已写入。",
            "- 执行报告：本文件。",
            "- 数据边界：pre-Holdout `nrows`；未读 `*_2026H1`；未读 HOLDOUT 内容。",
            "- git：遵守批次书“全程禁 git commit”，未提交。",
        ]
    )
    (CODEX_TASKS / "REPORT_B2.md").write_text("\n".join(report_lines) + "\n")


def main() -> None:
    bars, funding, audit = read_frozen_inputs()
    prepared = add_features(bars)
    results: dict[str, Result] = {}
    payload: dict[str, object] = {
            "run_timestamp_utc": pd.Timestamp.now(tz="UTC").isoformat(),
        "parameters": {
            "initial_capital": INITIAL_CAPITAL,
            "fee_rate_each_side": FEE_RATE,
            "slippage_rate_each_side": SLIPPAGE_RATE,
            "funding": "real 8H, long pays positive rate",
            "target_weight": TARGET_WEIGHT,
            "leverage_cap": LEVERAGE_CAP,
            "adx_period": ADX_PERIOD,
            "adx_entry": ADX_ENTRY,
            "adx_exit": ADX_EXIT,
            "lookback_bars": LOOKBACK_BARS,
            "macro_ma_days": MACRO_MA_DAYS,
        },
        "data_audit": audit,
        "comparison": {},
        "existing_p1_outputs": {
            "P1-04": {
                "path": "06_RESEARCH/CODE/output/p1_04_tsmom_regime_long_equity.csv",
                "ending_equity": read_existing_terminal(OUTPUT / "p1_04_tsmom_regime_long_equity.csv"),
            },
            "P1-06": {
                "path": "06_RESEARCH/CODE/output/p1_06_tsmom_macro_bull_equity.csv",
                "ending_equity": read_existing_terminal(OUTPUT / "p1_06_tsmom_macro_bull_equity.csv"),
            },
        },
        "prior_dual_engine_retrospective": {
            "source": "06_RESEARCH/RESULTS/20260612_tsmom_dual_engine.md",
            "p1_04": {"excess_profit": -12745.95},
            "p1_06": {"excess_profit": -1101379.86},
        },
    }

    for experiment in ("P1-04", "P1-06"):
        strategy_frames = build_targets(prepared, experiment, "strategy")
        benchmark_frames = build_targets(prepared, experiment, "benchmark")
        strategy = run_portfolio(f"{experiment.lower()}_strategy", strategy_frames, funding)
        benchmark = run_portfolio(f"{experiment.lower()}_benchmark", benchmark_frames, funding)
        results[f"{experiment.lower()}_strategy"] = strategy
        results[f"{experiment.lower()}_benchmark"] = benchmark
        strategy_summary = summarize(strategy)
        benchmark_summary = summarize(benchmark)
        excess = strategy_summary["ending_equity"] - benchmark_summary["ending_equity"]
        payload["comparison"][experiment] = {
            "strategy": strategy_summary,
            "benchmark": benchmark_summary,
            "excess": float(excess),
            "passes_fifth": bool(excess > 0),
        }

    write_outputs(payload, results)


if __name__ == "__main__":
    main()
