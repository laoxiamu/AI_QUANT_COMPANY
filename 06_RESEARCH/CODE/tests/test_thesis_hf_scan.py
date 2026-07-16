import json
from datetime import datetime, timezone

import pytest

from thesis_hf_scan import (
    build_legacy_funding_output,
    build_ssh_curl_command,
    extract_announcement_symbols,
    scan_binance_announcements,
    scan_depeg_assets,
    scan_funding_oi,
    scan_token_unlocks,
)


def test_funding_oi_scan_keeps_legacy_prescreen_and_oi_fields() -> None:
    fixtures = {
        "premiumIndex": [
            {"symbol": "AAAUSDT", "lastFundingRate": "0.004"},
            {"symbol": "BBBUSDT", "lastFundingRate": "0.001"},
            {"symbol": "CCCBTC", "lastFundingRate": "0.010"},
        ],
        "ticker": [
            {"symbol": "AAAUSDT", "priceChangePercent": "4.0", "quoteVolume": "1000000"},
            {"symbol": "BBBUSDT", "priceChangePercent": "-30.0", "quoteVolume": "6000000"},
        ],
        "openInterestHist?symbol=AAAUSDT": [
            {"sumOpenInterestValue": "100"},
            {"sumOpenInterestValue": "200"},
        ],
        "openInterestHist?symbol=BBBUSDT": [
            {"sumOpenInterestValue": "50"},
            {"sumOpenInterestValue": "25"},
        ],
    }

    def fake_fetch(url: str):
        if "premiumIndex" in url:
            return fixtures["premiumIndex"]
        if "ticker/24hr" in url:
            return fixtures["ticker"]
        if "openInterestHist?symbol=AAAUSDT" in url:
            return fixtures["openInterestHist?symbol=AAAUSDT"]
        if "openInterestHist?symbol=BBBUSDT" in url:
            return fixtures["openInterestHist?symbol=BBBUSDT"]
        raise AssertionError(url)

    rows = scan_funding_oi(fetch_json=fake_fetch, sleep_fn=lambda _: None)

    assert rows == [
        {
            "symbol": "AAAUSDT",
            "funding_8h": 0.004,
            "chg24h_pct": 4.0,
            "quote_vol_usdt": 1000000.0,
            "oi_24h_ago_usdt": 100.0,
            "oi_now_usdt": 200.0,
            "oi_24h_ratio": 2.0,
        },
        {
            "symbol": "BBBUSDT",
            "funding_8h": 0.001,
            "chg24h_pct": -30.0,
            "quote_vol_usdt": 6000000.0,
            "oi_24h_ago_usdt": 50.0,
            "oi_now_usdt": 25.0,
            "oi_24h_ratio": 0.5,
        },
    ]
    assert build_legacy_funding_output("20260716_0000", rows) == {
        "scan_utc": "20260716_0000",
        "n_prescreen": 2,
        "candidates": rows,
    }


def test_binance_announcement_scan_labels_new_perp_and_delist_events() -> None:
    catalog_48 = {
        "data": {
            "articles": [
                {
                    "id": 1,
                    "code": "launch-code",
                    "title": "Binance Futures Will Launch USDⓈ-Margined DATAIPUSDT and DATAIPUSDC Perpetual Contracts (2026-07-03)",
                }
            ]
        }
    }
    catalog_161 = {
        "data": {
            "articles": [
                {
                    "id": 2,
                    "code": "delist-code",
                    "title": "Binance Futures Will Delist USDⓈ-Margined IPUSDT and IPUSDC Perpetual Contracts (2026-06-28)",
                }
            ]
        }
    }

    def fake_fetch(url: str):
        if "catalogId=48" in url:
            return catalog_48
        if "catalogId=161" in url:
            return catalog_161
        return {"data": {"articles": []}}

    candidates = scan_binance_announcements(fetch_json=fake_fetch, catalog_ids=(48, 161))

    assert [c["event_type"] for c in candidates] == [
        "new_perp_listing",
        "futures_delist",
    ]
    assert candidates[0]["source"] == "binance_announcement"
    assert candidates[0]["symbols"] == ["DATAIPUSDT", "DATAIPUSDC"]
    assert candidates[0]["event_date"] == "2026-07-03"
    assert candidates[0]["url"].endswith("articleCode=launch-code")
    assert candidates[1]["symbols"] == ["IPUSDT", "IPUSDC"]
    assert candidates[1]["raw"]["catalog_id"] == 161


def test_token_unlock_scan_parses_cryptorank_next_data() -> None:
    next_data = {
        "props": {
            "pageProps": {
                "fallbackData": {
                    "data": [
                        {
                            "id": 10,
                            "date": "2026-07-20T00:00:00.000Z",
                            "price": 2.0,
                            "nextUnlockPercent": 3.2,
                            "nextUnlocks": [
                                {
                                    "date": "2026-07-20T00:00:00.000Z",
                                    "allocationName": "Team",
                                    "tokens": 600000,
                                }
                            ],
                            "key": "sample-token",
                            "symbol": "SMP",
                            "name": "Sample Token",
                            "marketCap": "10000000",
                            "chg24h": -4.5,
                        }
                    ]
                }
            }
        }
    }
    html = (
        '<html><script id="__NEXT_DATA__" type="application/json">'
        + json.dumps(next_data)
        + "</script></html>"
    )

    candidates = scan_token_unlocks(
        fetch_text=lambda _: html,
        now_dt=datetime(2026, 7, 16, tzinfo=timezone.utc),
        min_unlock_usd=100000,
    )

    assert candidates == [
        {
            "source": "token_unlock_cryptorank",
            "event_type": "upcoming_unlock",
            "symbol": "SMP",
            "name": "Sample Token",
            "unlock_date": "2026-07-20",
            "days_until_unlock": 4,
            "price_usd": 2.0,
            "unlock_tokens": 600000.0,
            "unlock_usd": 1200000.0,
            "unlock_market_cap_pct": 3.2,
            "market_cap_usd": 10000000.0,
            "allocations": [
                {
                    "name": "Team",
                    "tokens": 600000.0,
                    "date": "2026-07-20T00:00:00.000Z",
                }
            ],
            "url": "https://cryptorank.io/price/sample-token/vesting",
            "source_url": "https://cryptorank.io/token-unlock",
            "raw": {"id": 10, "key": "sample-token", "chg24h": -4.5},
        }
    ]


def test_depeg_scan_flags_assets_more_than_threshold_from_peg() -> None:
    payload = {
        "magic-internet-money": {
            "usd": 0.137553,
            "usd_24h_change": 4.63,
            "last_updated_at": 1784181043,
        },
        "dai": {"usd": 0.9996, "usd_24h_change": -0.01, "last_updated_at": 1784181038},
    }

    candidates = scan_depeg_assets(fetch_json=lambda _: payload, threshold=0.02)

    assert len(candidates) == 1
    assert candidates[0]["source"] == "depeg_coingecko"
    assert candidates[0]["event_type"] == "peg_deviation"
    assert candidates[0]["symbol"] == "MIM"
    assert candidates[0]["price_usd"] == 0.137553
    assert candidates[0]["deviation_pct"] == pytest.approx(-86.2447)
    assert candidates[0]["url"] == "https://www.coingecko.com/en/coins/magic-internet-money"


def test_ssh_fetch_command_has_remote_curl_timeouts_and_quotes_url() -> None:
    cmd = build_ssh_curl_command("https://example.com/a path?q=1&x=2")

    assert cmd[:2] == ["ssh", "-i"]
    assert "--connect-timeout 12" in cmd[-1]
    assert "--max-time 30" in cmd[-1]
    assert "'https://example.com/a path?q=1&x=2'" in cmd[-1]


def test_announcement_symbol_extraction_does_not_emit_usdm_as_symbol() -> None:
    symbols = extract_announcement_symbols(
        "Binance Futures Will Delist USDⓈ-M Multiple Perpetual Contracts (2026-04-28)"
    )

    assert symbols == []
