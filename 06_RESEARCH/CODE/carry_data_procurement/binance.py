"""Small official Binance REST/data.vision client."""

from __future__ import annotations

import csv
import hashlib
import hmac
import io
import os
import time
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any
from urllib.parse import urlencode

import requests

from carry_data_procurement.schemas import normalize_kline_rows


@dataclass(frozen=True)
class BinanceConfig:
    spot_api: str = "https://api.binance.com"
    futures_api: str = "https://fapi.binance.com"
    data_vision: str = "https://data.binance.vision"
    timeout_s: int = 30
    no_proxy: bool = False


class BinanceClient:
    def __init__(self, config: BinanceConfig | None = None) -> None:
        self.config = config or BinanceConfig()
        self.session = requests.Session()
        if self.config.no_proxy:
            self.session.trust_env = False

    def get_json(
        self,
        base_url: str,
        path: str,
        params: dict[str, Any] | None = None,
        *,
        signed: bool = False,
    ) -> Any:
        query = dict(params or {})
        headers: dict[str, str] = {}
        if signed:
            api_key = os.environ.get("BINANCE_API_KEY")
            secret = os.environ.get("BINANCE_API_SECRET")
            if not api_key or not secret:
                raise RuntimeError("signed endpoint requires BINANCE_API_KEY and BINANCE_API_SECRET")
            query["timestamp"] = int(time.time() * 1000)
            query.setdefault("recvWindow", 5000)
            encoded = urlencode(query)
            query["signature"] = hmac.new(
                secret.encode("utf-8"),
                encoded.encode("utf-8"),
                hashlib.sha256,
            ).hexdigest()
            headers["X-MBX-APIKEY"] = api_key

        response = self.session.get(
            f"{base_url}{path}",
            params=query,
            headers=headers,
            timeout=self.config.timeout_s,
        )
        response.raise_for_status()
        return response.json()

    def download_data_vision_spot_month(self, symbol: str, year: int, month: int):
        file_name = f"{symbol}-1h-{year:04d}-{month:02d}.zip"
        url = (
            f"{self.config.data_vision}/data/spot/monthly/klines/"
            f"{symbol}/1h/{file_name}"
        )
        response = self.session.get(url, timeout=self.config.timeout_s)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            csv_name = archive.namelist()[0]
            with archive.open(csv_name) as handle:
                text = io.TextIOWrapper(handle, encoding="utf-8")
                rows = list(csv.reader(text))
        return normalize_kline_rows(rows)

    def paginated_klines(
        self,
        *,
        base_url: str,
        path: str,
        symbol: str,
        start_ms: int,
        end_ms: int,
        limit: int = 1500,
        symbol_key: str = "symbol",
    ) -> list[list[Any]]:
        rows: list[list[Any]] = []
        cursor = start_ms
        while cursor < end_ms:
            batch = self.get_json(
                base_url,
                path,
                {
                    symbol_key: symbol,
                    "interval": "1h",
                    "startTime": cursor,
                    "endTime": end_ms - 1,
                    "limit": limit,
                },
            )
            if not batch:
                break
            rows.extend(batch)
            next_cursor = int(batch[-1][0]) + 60 * 60 * 1000
            if next_cursor <= cursor:
                raise RuntimeError("Binance pagination did not advance")
            cursor = next_cursor
        return rows

    def download_data_vision_funding_month(self, symbol: str, year: int, month: int) -> "pd.DataFrame":
        """Download monthly funding rate zip from data.binance.vision."""
        import pandas as pd
        file_name = f"{symbol}-fundingRate-{year:04d}-{month:02d}.zip"
        url = (
            f"{self.config.data_vision}/data/futures/um/monthly/fundingRate/"
            f"{symbol}/{file_name}"
        )
        response = self.session.get(url, timeout=self.config.timeout_s)
        response.raise_for_status()
        with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
            csv_name = archive.namelist()[0]
            with archive.open(csv_name) as handle:
                text = io.TextIOWrapper(handle, encoding="utf-8")
                rows = list(csv.reader(text))
        # Drop header if present
        if rows and not str(rows[0][0]).lstrip("-").isdigit():
            rows = rows[1:]
        frame = pd.DataFrame(rows, columns=["calc_time", "funding_interval_hours", "last_funding_rate"])
        frame["calc_time"] = pd.to_datetime(pd.to_numeric(frame["calc_time"], errors="coerce"), unit="ms", utc=True)
        frame["funding_interval_hours"] = pd.to_numeric(frame["funding_interval_hours"], errors="coerce")
        frame["last_funding_rate"] = pd.to_numeric(frame["last_funding_rate"], errors="coerce")
        return frame.dropna(subset=["calc_time"]).sort_values("calc_time").reset_index(drop=True)

    def fetch_leverage_brackets(self, symbol: str) -> Any:
        return self.get_json(
            self.config.futures_api,
            "/fapi/v1/leverageBracket",
            {"symbol": symbol},
            signed=True,
        )

    def fetch_adl_quantile(self, symbol: str) -> Any:
        return self.get_json(
            self.config.futures_api,
            "/fapi/v1/adlQuantile",
            {"symbol": symbol},
            signed=True,
        )


def month_range(start_year: int, start_month: int, end_year: int, end_month: int):
    year, month = start_year, start_month
    while (year, month) <= (end_year, end_month):
        yield year, month
        month += 1
        if month == 13:
            year += 1
            month = 1


def repo_root_from_code_file(file: str) -> Path:
    return Path(file).resolve().parents[2]
