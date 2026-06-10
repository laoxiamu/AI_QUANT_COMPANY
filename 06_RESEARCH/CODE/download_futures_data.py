"""Download Binance USD-M mark-price klines and funding-rate history."""

import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
from io import BytesIO
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen
from zipfile import ZipFile

import pandas as pd


SYMBOL_START = {
    "BTCUSDT": "2020-01",
    "ETHUSDT": "2020-01",
    "SOLUSDT": "2020-09",
}
END_MONTH = "2026-05"
DEFAULT_TIMEFRAME = "4h"
BASE_URL = "https://data.binance.vision/data/futures/um/monthly"
PROJECT_ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = PROJECT_ROOT / "06_RESEARCH/DATA/FUTURES"


def archive_url(
    symbol: str, month: str, dataset: str, timeframe: str
) -> str:
    if dataset == "mark":
        return (
            f"{BASE_URL}/markPriceKlines/{symbol}/{timeframe}/"
            f"{symbol}-{timeframe}-{month}.zip"
        )
    return (
        f"{BASE_URL}/fundingRate/{symbol}/"
        f"{symbol}-fundingRate-{month}.zip"
    )


def download_archive(
    symbol: str, month: str, dataset: str, timeframe: str
) -> tuple[str, str, str, bytes]:
    url = archive_url(symbol, month, dataset, timeframe)
    try:
        payload = urlopen(url, timeout=30).read()
    except HTTPError as exc:
        raise RuntimeError(f"HTTP {exc.code}: {url}") from exc
    return symbol, month, dataset, payload


def parse_archive(payload: bytes, dataset: str) -> pd.DataFrame:
    with ZipFile(BytesIO(payload)) as archive:
        member = archive.namelist()[0]
        raw_bytes = archive.read(member)
    frame = pd.read_csv(BytesIO(raw_bytes))
    if dataset == "mark":
        if "open_time" not in frame.columns:
            frame = pd.read_csv(
                BytesIO(raw_bytes),
                header=None,
                names=[
                    "open_time",
                    "open",
                    "high",
                    "low",
                    "close",
                    "volume",
                    "close_time",
                    "quote_volume",
                    "count",
                    "taker_buy_volume",
                    "taker_buy_quote_volume",
                    "ignore",
                ],
            )
        return frame[
            ["open_time", "open", "high", "low", "close", "volume"]
        ]
    if "calc_time" not in frame.columns:
        frame = pd.read_csv(
            BytesIO(raw_bytes),
            header=None,
            names=[
                "calc_time",
                "funding_interval_hours",
                "last_funding_rate",
            ],
        )
    return frame[
        ["calc_time", "funding_interval_hours", "last_funding_rate"]
    ]


def parse_mixed_epoch(values: pd.Series) -> pd.Series:
    milliseconds = values < 10**15
    parsed = pd.Series(pd.NaT, index=values.index, dtype="datetime64[ns]")
    parsed.loc[milliseconds] = pd.to_datetime(
        values.loc[milliseconds], unit="ms"
    ).to_numpy()
    parsed.loc[~milliseconds] = pd.to_datetime(
        values.loc[~milliseconds], unit="us"
    ).to_numpy()
    return parsed


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--timeframe", default=DEFAULT_TIMEFRAME)
    parser.add_argument(
        "--mark-only",
        action="store_true",
        help="Download mark-price klines without re-downloading funding.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    timeframe = args.timeframe.lower()
    timeframe_hours = int(timeframe.removesuffix("h"))
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    jobs: list[tuple[str, str, str, str]] = []
    for symbol, start_month in SYMBOL_START.items():
        for month in pd.period_range(start_month, END_MONTH, freq="M"):
            month_text = str(month)
            jobs.append((symbol, month_text, "mark", timeframe))
            if not args.mark_only:
                jobs.append((symbol, month_text, "funding", timeframe))

    collected: dict[tuple[str, str], list[pd.DataFrame]] = {}
    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {
            executor.submit(download_archive, *job): job for job in jobs
        }
        for count, future in enumerate(as_completed(futures), start=1):
            symbol, month, dataset, payload = future.result()
            collected.setdefault((symbol, dataset), []).append(
                parse_archive(payload, dataset)
            )
            if count % 50 == 0 or count == len(jobs):
                print(f"Downloaded {count}/{len(jobs)} archives", flush=True)

    for symbol in SYMBOL_START:
        mark = pd.concat(collected[(symbol, "mark")], ignore_index=True)
        mark["datetime"] = parse_mixed_epoch(mark["open_time"])
        mark = (
            mark[["datetime", "open", "high", "low", "close", "volume"]]
            .sort_values("datetime")
            .drop_duplicates("datetime")
            .reset_index(drop=True)
        )
        mark_path = OUTPUT_DIR / f"{symbol}_MARK_{timeframe.upper()}.csv"
        mark.to_csv(mark_path, index=False, date_format="%Y-%m-%d %H:%M:%S")

        mark_gaps = (
            mark["datetime"].diff().dropna()
            != pd.Timedelta(hours=timeframe_hours)
        ).sum()
        if args.mark_only:
            print(
                f"{symbol}: mark={len(mark)} "
                f"({mark.datetime.iloc[0]} ~ {mark.datetime.iloc[-1]}), "
                f"mark_gaps={mark_gaps}"
            )
            continue

        funding = pd.concat(collected[(symbol, "funding")], ignore_index=True)
        funding["datetime"] = parse_mixed_epoch(funding["calc_time"])
        funding["datetime"] = funding["datetime"].dt.floor("s")
        funding = (
            funding[
                ["datetime", "funding_interval_hours", "last_funding_rate"]
            ]
            .sort_values("datetime")
            .drop_duplicates("datetime")
            .reset_index(drop=True)
        )
        funding_path = OUTPUT_DIR / f"{symbol}_FUNDING_8H.csv"
        funding.to_csv(
            funding_path, index=False, date_format="%Y-%m-%d %H:%M:%S"
        )

        funding_gaps = (
            funding["datetime"].diff().dropna() != pd.Timedelta(hours=8)
        ).sum()
        print(
            f"{symbol}: mark={len(mark)} "
            f"({mark.datetime.iloc[0]} ~ {mark.datetime.iloc[-1]}), "
            f"mark_gaps={mark_gaps}; funding={len(funding)} "
            f"({funding.datetime.iloc[0]} ~ {funding.datetime.iloc[-1]}), "
            f"funding_gaps={funding_gaps}"
        )


if __name__ == "__main__":
    main()
