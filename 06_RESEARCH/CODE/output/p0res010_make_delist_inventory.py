#!/usr/bin/env python3
"""Build P0-RES-010 Binance delisting/relisting scout inventory.

This is an inventory-only scout artifact. It does not run signal research,
backtests, or touch holdout data.
"""

from __future__ import annotations

import csv
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PANEL_DIR = ROOT / "06_RESEARCH" / "DATA" / "FUTURES_EXPANDED_2026"
OUT_DIR = ROOT / "06_RESEARCH" / "DATA" / "DELIST_EVENTS"
OUT_CSV = OUT_DIR / "binance_delist_event_inventory_p0res010_20260716.csv"


EVENTS = [
    # USDⓈ-M futures delisting events discovered from Binance Support/Square mirrors
    # and indexed secondary mirrors when direct Binance API/curl was unreachable.
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "ANTUSDT",
        "original_listing": "ANTUSDT perpetual",
        "announcement_time_utc": "2024-03-25 05:39:06",
        "delist_settlement_time_utc": "2024-04-01 09:00:00",
        "source_url": "https://www.binance.com/en/square/post/5862637789937",
        "source_note": "Binance Square official-account mirror; BitcoinSistemi indexed announcement time used where official article time was not exposed.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "DGBUSDT",
        "original_listing": "DGBUSDT perpetual",
        "announcement_time_utc": "2024-03-25 05:39:06",
        "delist_settlement_time_utc": "2024-04-01 09:00:00",
        "source_url": "https://www.binance.com/en/square/post/5862637789937",
        "source_note": "Binance Square official-account mirror; BitcoinSistemi indexed announcement time used where official article time was not exposed.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "CTKUSDT",
        "original_listing": "CTKUSDT perpetual",
        "announcement_time_utc": "2024-03-25 05:39:06",
        "delist_settlement_time_utc": "2024-04-01 09:00:00",
        "source_url": "https://www.binance.com/en/square/post/5862637789937",
        "source_note": "Binance Square official-account mirror; BitcoinSistemi indexed announcement time used where official article time was not exposed.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "STPTUSDT",
        "original_listing": "STPTUSDT perpetual",
        "announcement_time_utc": "2024-05-06 06:39:38",
        "delist_settlement_time_utc": "2024-05-13 09:00:00",
        "source_url": "https://coingape.com/binance-futures-set-to-delist-these-cryptos-what-next/",
        "source_note": "Secondary source summarizing Binance announcement; official article inaccessible via direct curl.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "SNTUSDT",
        "original_listing": "SNTUSDT perpetual",
        "announcement_time_utc": "2024-05-06 06:39:38",
        "delist_settlement_time_utc": "2024-05-13 09:00:00",
        "source_url": "https://coingape.com/binance-futures-set-to-delist-these-cryptos-what-next/",
        "source_note": "Secondary source summarizing Binance announcement; official article inaccessible via direct curl.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "MBLUSDT",
        "original_listing": "MBLUSDT perpetual",
        "announcement_time_utc": "2024-05-06 06:39:38",
        "delist_settlement_time_utc": "2024-05-13 09:00:00",
        "source_url": "https://coingape.com/binance-futures-set-to-delist-these-cryptos-what-next/",
        "source_note": "Secondary source summarizing Binance announcement; official article inaccessible via direct curl.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "RADUSDT",
        "original_listing": "RADUSDT perpetual",
        "announcement_time_utc": "2024-05-06 06:39:38",
        "delist_settlement_time_utc": "2024-05-14 09:00:00",
        "source_url": "https://coingape.com/binance-futures-set-to-delist-these-cryptos-what-next/",
        "source_note": "Secondary source summarizing Binance announcement; official article inaccessible via direct curl.",
    },
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "CVXUSDT",
        "original_listing": "CVXUSDT perpetual",
        "announcement_time_utc": "2024-05-06 06:39:38",
        "delist_settlement_time_utc": "2024-05-14 09:00:00",
        "source_url": "https://coingape.com/binance-futures-set-to-delist-these-cryptos-what-next/",
        "source_note": "Secondary source summarizing Binance announcement; official article inaccessible via direct curl.",
    },
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2024-05-08 05:05:39",
            "delist_settlement_time_utc": settlement,
            "source_url": "https://www.binance.com/en/square/post/7809671247033",
            "source_note": "Binance Square official-account mirror; ChainCatcher indexed announcement time used where official article time was not exposed.",
        }
        for symbol, settlement in [
            ("IDEXUSDT", "2024-05-15 09:00:00"),
            ("SLPUSDT", "2024-05-15 09:00:00"),
            ("GLMRUSDT", "2024-05-15 09:00:00"),
            ("MDTUSDT", "2024-05-16 09:00:00"),
            ("AUDIOUSDT", "2024-05-16 09:00:00"),
        ]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2024-12-02 00:00:00",
            "delist_settlement_time_utc": "2024-12-09 09:00:00",
            "source_url": "https://www.coincarp.com/exchange/announcement/binance-cfe97d52a8c840d3ba631835b637e9e7/",
            "source_note": "CoinCarp mirror of Binance announcement; announcement date approximated from indexed historical notice week.",
        }
        for symbol in ["XEMUSDT", "ORBSUSDT", "LOOMUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2024-12-06 03:02:37",
            "delist_settlement_time_utc": "2024-12-16 09:00:00",
            "source_url": "https://www.coincarp.com/exchange/announcement/binance-27eac260521b4f40ab331e1a345887a7/",
            "source_note": "CoinCarp mirror of Binance announcement; PANews index provided announcement timestamp.",
        }
        for symbol in ["MAVIAUSDT", "OMGUSDT", "BONDUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-11-03 06:55:38",
            "delist_settlement_time_utc": settlement,
            "source_url": "https://coinengineer.net/blog/binance-futures-is-delisting-these-altcoins/",
            "source_note": "Secondary source summarizing Binance announcement.",
        }
        for symbol, settlement in [
            ("KDAUSDT", "2025-11-06 09:00:00"),
        ]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-11-12 00:00:00",
            "delist_settlement_time_utc": "2025-11-14 09:00:00",
            "source_url": "https://www.binance.com/en/square/post/32242183911481",
            "source_note": "Binance Square official-account mirror; exact article publish timestamp not exposed in accessible text.",
        }
        for symbol in ["MYROUSDT", "1000XUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-11-18 09:11:17",
            "delist_settlement_time_utc": "2025-11-21 09:00:00",
            "source_url": "https://coinengineer.net/blog/binance-is-delisting-multiple-coins/",
            "source_note": "Secondary source summarizing Binance announcement.",
        }
        for symbol in ["XCNUSDT", "FLMUSDT", "PERPUSDT"]
    ],
    {
        "market": "USDS-M perpetual",
        "event_type": "futures_contract_delist_auto_settlement",
        "symbol": "PORT3USDT",
        "original_listing": "PORT3USDT perpetual",
        "announcement_time_utc": "2025-11-22 00:00:00",
        "delist_settlement_time_utc": "2025-11-23 06:30:00",
        "source_url": "https://www.binance.com/en/square/post/32760980666538",
        "source_note": "Binance Square official-account mirror; author line indicates Nov 23, 2025; timestamp approximated conservatively to prior date because settlement was 06:30 UTC.",
    },
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-11-25 14:25:00",
            "delist_settlement_time_utc": "2025-11-28 09:00:00",
            "source_url": "https://www.tradingview.com/news/u_today:25498cafc094b:0-binance-to-cut-multiple-perpetual-contracts-these-three-crypto-pairs-included/",
            "source_note": "Secondary source links to Binance announcement detail/53998d26b57f47beb97811ec9f5e582b.",
        }
        for symbol in ["PONKEUSDT", "SWELLUSDT", "QUICKUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-12-01 08:58:45",
            "delist_settlement_time_utc": settlement,
            "source_url": "https://xpool.eu/2025/12/01/binance-futures-to-delist-perpetual-contracts-closing-times-measures/",
            "source_note": "Secondary source summarizing Binance announcement.",
        }
        for symbol, settlement in [
            ("SXPUSDT", "2025-12-05 09:00:00"),
            ("MILKUSDT", "2025-12-05 09:00:00"),
            ("OBOLUSDT", "2025-12-05 09:30:00"),
            ("TOKENUSDT", "2025-12-05 09:30:00"),
        ]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2025-12-06 00:44:16",
            "delist_settlement_time_utc": "2025-12-10 09:00:00",
            "source_url": "https://rfq.news/binancecoin/binance-futures-removes-four-usd%e2%93%a2-m-perpetual-contracts-next-week/",
            "source_note": "Secondary source summarizing Binance announcement.",
        }
        for symbol in ["SKATEUSDT", "REIUSDT", "FISUSDT", "VOXELUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-01-15 00:00:00",
            "delist_settlement_time_utc": "2026-01-21 09:00:00",
            "source_url": "https://www.mexc.co/news/497909",
            "source_note": "Secondary source summarizing Binance announcement.",
        }
        for symbol in ["BIDUSDT", "DMCUSDT", "ZRCUSDT", "TANSSIUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-01-28 00:00:00",
            "delist_settlement_time_utc": "2026-01-30 09:00:00",
            "source_url": "https://www.treeofalpha.com/preview_article?id=1769595249706",
            "source_note": "Mirror includes Binance Team date 2026-01-28.",
        }
        for symbol in ["42USDT", "COMMONUSDT", "CUDISUSDT", "EPTUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-03-13 14:51:08",
            "delist_settlement_time_utc": "2026-03-17 09:00:00",
            "source_url": "https://www.binance.info/en/support/announcement/detail/f6ebc17e4dbd451b873d9ef25c801237",
            "source_note": "Binance Support mirror; secondary index supplied announcement date.",
        }
        for symbol in ["VFYUSDT", "1000WHYUSDT", "BDXNUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-04-03 14:39:07",
            "delist_settlement_time_utc": "2026-04-08 09:00:00",
            "source_url": "https://www.binance.info/en/support/announcement/detail/97b4f3a7d02a486c8d412ada2281b907",
            "source_note": "Binance Support mirror; secondary index supplied announcement date.",
        }
        for symbol in ["OLUSDT", "HIPPOUSDT", "RLSUSDT", "PUFFERUSDT"]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-04-23 15:01:00",
            "delist_settlement_time_utc": settlement,
            "source_url": "https://www.binance.com/en/square/post/315659328967362",
            "source_note": "Binance Square official-account mirror; PANews index supplied announcement date.",
        }
        for symbol, settlement in [
            ("B3USDT", "2026-04-28 09:00:00"),
            ("DEGENUSDT", "2026-04-28 09:00:00"),
            ("BOBUSDT", "2026-04-28 09:00:00"),
            ("ZKJUSDT", "2026-04-29 09:00:00"),
            ("IRUSDT", "2026-04-29 09:00:00"),
            ("DAMUSDT", "2026-04-29 09:00:00"),
        ]
    ],
    *[
        {
            "market": "USDS-M perpetual",
            "event_type": "futures_contract_delist_auto_settlement",
            "symbol": symbol,
            "original_listing": f"{symbol} perpetual",
            "announcement_time_utc": "2026-04-24 00:00:00",
            "delist_settlement_time_utc": "2026-04-28 10:00:00",
            "source_url": "https://www.binance.com/en/square/post/315957928905937",
            "source_note": "Binance Square official-account mirror; author line indicates 24 Apr.",
        }
        for symbol in ["VINEUSDT", "AIUSDT"]
    ],
    # Spot pair removals / token delists. These are not futures forced settlement,
    # but are included because the task asked for spot + USDⓈ-M announcements.
    *[
        {
            "market": "spot",
            "event_type": "spot_pair_removal",
            "symbol": pair.split("/")[0] + "USDT",
            "original_listing": pair,
            "announcement_time_utc": "2024-12-28 00:00:00",
            "delist_settlement_time_utc": "2025-01-03 08:00:00",
            "source_url": "https://bitcoinworld.co.in/binance-delisting-spot-trading-pairs/",
            "source_note": "Secondary source summarizing Binance spot pair removal; timestamp date-only.",
        }
        for pair in [
            "AI/BNB",
            "ETC/BNB",
            "FLOW/BTC",
            "LPT/BNB",
            "SFP/BTC",
            "VET/BNB",
            "WCT/FDUSD",
            "WIF/BRL",
            "WLFI/BRL",
        ]
    ],
    *[
        {
            "market": "spot",
            "event_type": "spot_pair_removal",
            "symbol": pair.split("/")[0] + "USDT",
            "original_listing": pair,
            "announcement_time_utc": "2025-01-09 00:00:00",
            "delist_settlement_time_utc": "2025-01-16 03:00:00",
            "source_url": "https://cryptorank.io/news/feed/16461-binance-delisting-spot-trading-pairs-2",
            "source_note": "Secondary source says Binance official notice was published 2025-01-09; timestamp date-only.",
        }
        for pair in [
            "2Z/FDUSD",
            "AAVE/FDUSD",
            "A/BTC",
            "APE/FDUSD",
            "API3/BTC",
            "ARB/FDUSD",
            "EUL/BNB",
            "FET/FDUSD",
            "HMSTR/FDUSD",
            "LAYER/BTC",
            "LAYER/FDUSD",
            "MIRA/BNB",
            "OP/FDUSD",
            "ORDI/FDUSD",
            "PYTH/FDUSD",
            "TRX/FDUSD",
            "WCT/BNB",
            "YB/FDUSD",
            "ZBT/BNB",
            "ZKC/FDUSD",
        ]
    ],
    *[
        {
            "market": "spot",
            "event_type": "spot_pair_removal",
            "symbol": pair.split("/")[0] + "USDT",
            "original_listing": pair,
            "announcement_time_utc": "2025-01-16 00:00:00",
            "delist_settlement_time_utc": "2025-01-23 03:00:00",
            "source_url": "https://coinpulsehq.com/binance-delisting-spot-trading-pairs-5/",
            "source_note": "Secondary source summarizing Binance official notice; timestamp date-only.",
        }
        for pair in [
            "AI/BTC",
            "APE/BTC",
            "AUCTION/BTC",
            "ID/BTC",
            "LDO/BTC",
            "NMR/BTC",
            "PNUT/BTC",
            "PYR/BTC",
            "YFI/BTC",
            "FIL/ETH",
            "LRC/ETH",
            "XVG/ETH",
            "ZIL/ETH",
            "ALLO/BNB",
            "ENA/BNB",
            "KITE/BNB",
            "BOME/FDUSD",
            "DYDX/FDUSD",
            "PENGU/FDUSD",
            "STRK/FDUSD",
        ]
    ],
    *[
        {
            "market": "spot",
            "event_type": "spot_pair_removal",
            "symbol": pair.split("/")[0] + "USDT",
            "original_listing": pair,
            "announcement_time_utc": "2025-12-01 00:00:00",
            "delist_settlement_time_utc": "2025-12-05 03:00:00",
            "source_url": "https://www.mexc.fm/news/219087",
            "source_note": "Secondary source citing CoinOtag/Binance official sources; timestamp date-only.",
        }
        for pair in [
            "ACH/BTC",
            "DENT/ETH",
            "EGLD/FDUSD",
            "HAEDAL/BNB",
            "INIT/FDUSD",
            "PORTAL/BNB",
            "PORTAL/BTC",
            "PROVE/FDUSD",
            "QTUM/BTC",
            "RIF/BTC",
            "SHELL/FDUSD",
            "STRAX/BTC",
            "TREE/FDUSD",
            "WAXP/BTC",
            "W/BTC",
        ]
    ],
]


def parse_dt(value: str) -> datetime:
    return datetime.strptime(value, "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)


def panel_ranges() -> dict[str, tuple[datetime, datetime, int]]:
    ranges: dict[str, tuple[datetime, datetime, int]] = {}
    for path in sorted(PANEL_DIR.glob("*_4H.csv")):
        symbol = path.name.removesuffix("_4H.csv")
        with path.open(newline="") as f:
            reader = csv.DictReader(f)
            first = None
            last = None
            rows = 0
            for row in reader:
                ts = datetime.strptime(row["datetime"], "%Y-%m-%d %H:%M:%S").replace(tzinfo=timezone.utc)
                if first is None:
                    first = ts
                last = ts
                rows += 1
        if first is not None and last is not None:
            ranges[symbol] = (first, last, rows)
    return ranges


def main() -> None:
    panels = panel_ranges()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    fields = [
        "market",
        "event_type",
        "symbol",
        "original_listing",
        "announcement_time_utc",
        "delist_settlement_time_utc",
        "announcement_to_delist_hours",
        "source_url",
        "source_note",
        "local_panel_symbol",
        "in_local_panel_symbol_set",
        "announcement_in_panel_coverage",
        "local_panel_start_utc",
        "local_panel_end_utc",
        "local_panel_rows",
    ]

    out_rows = []
    for event in EVENTS:
        ann = parse_dt(event["announcement_time_utc"])
        settle = parse_dt(event["delist_settlement_time_utc"])
        symbol = event["symbol"]
        panel = panels.get(symbol)
        in_panel = panel is not None
        in_coverage = False
        panel_start = ""
        panel_end = ""
        panel_rows = ""
        if panel:
            first, last, rows = panel
            in_coverage = first <= ann <= last
            panel_start = first.strftime("%Y-%m-%d %H:%M:%S")
            panel_end = last.strftime("%Y-%m-%d %H:%M:%S")
            panel_rows = str(rows)
        row = dict(event)
        row.update(
            {
                "announcement_to_delist_hours": round((settle - ann).total_seconds() / 3600, 2),
                "local_panel_symbol": symbol if in_panel else "",
                "in_local_panel_symbol_set": in_panel,
                "announcement_in_panel_coverage": in_coverage,
                "local_panel_start_utc": panel_start,
                "local_panel_end_utc": panel_end,
                "local_panel_rows": panel_rows,
            }
        )
        out_rows.append(row)

    with OUT_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(out_rows)

    aligned = [r for r in out_rows if r["announcement_in_panel_coverage"]]
    futures_aligned = [r for r in aligned if r["market"] == "USDS-M perpetual"]
    spot_aligned = [r for r in aligned if r["market"] == "spot"]
    print(f"wrote={OUT_CSV}")
    print(f"panel_symbols={len(panels)}")
    print(f"inventory_rows={len(out_rows)}")
    print(f"aligned_rows={len(aligned)}")
    print(f"aligned_futures_rows={len(futures_aligned)}")
    print(f"aligned_spot_rows={len(spot_aligned)}")
    print("aligned_symbols=" + ",".join(r["symbol"] for r in aligned))


if __name__ == "__main__":
    main()
