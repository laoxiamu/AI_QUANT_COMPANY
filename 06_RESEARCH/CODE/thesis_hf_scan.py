#!/usr/bin/env python3
"""高频thesis候选扫描器（投研线1个月冲刺工具，2026-07-12建）。
只读扫描：funding/OI、Binance公告、公开解锁日历、脱锚监控 → 候选清单JSON。
不登记、不判定——登记与闸0/闸1裁决仍由Claude人工完成（THESIS_TEMPLATE纪律）。
通道A执行：Mac直连fapi.binance.com，代理unset（RUNBOOK 2026-06-22铁律）。
"""
import argparse
import html
import json
import os
import re
import shlex
import ssl
import subprocess
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

BASE = "https://fapi.binance.com"
BINANCE_CMS = "https://www.binance.com/bapi/composite/v1/public/cms/article/catalog/list/query"
BINANCE_ARTICLE = "https://www.binance.com/bapi/composite/v1/public/cms/article/detail/query"
CRYPTORANK_UNLOCK_URL = "https://cryptorank.io/token-unlock"
CRYPTORANK_API_BASE = "https://api.cryptorank.io/v0"
CRYPTORANK_IMPORTANT_UNLOCKS_URL = (
    f"{CRYPTORANK_API_BASE}/consolidated-vesting/important-upcoming-unlocks?period=7D"
)
COINGECKO_SIMPLE_PRICE = "https://api.coingecko.com/api/v3/simple/price"
COINGECKO_COIN_URL = "https://www.coingecko.com/en/coins"
OUT = Path(__file__).resolve().parent / "output"
CTX = ssl.create_default_context()
USER_AGENT = "aiquant-scan/1.0"
PROXY_ENV_KEYS = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)
DEFAULT_SOURCES = ("funding_oi", "binance_announcements", "token_unlocks", "depeg")
SSH_SG_HOST = "root@43.160.200.224"
SSH_SG_KEY = str(Path.home() / ".ssh" / "id_ed25519_aiquant")
DEFAULT_PEG_ASSETS = (
    {"id": "tether", "symbol": "USDT", "name": "Tether", "peg_usd": 1.0},
    {"id": "usd-coin", "symbol": "USDC", "name": "USD Coin", "peg_usd": 1.0},
    {"id": "dai", "symbol": "DAI", "name": "Dai", "peg_usd": 1.0},
    {"id": "first-digital-usd", "symbol": "FDUSD", "name": "First Digital USD", "peg_usd": 1.0},
    {"id": "true-usd", "symbol": "TUSD", "name": "TrueUSD", "peg_usd": 1.0},
    {"id": "frax", "symbol": "FRAX", "name": "Frax", "peg_usd": 1.0},
    {"id": "usdd", "symbol": "USDD", "name": "USDD", "peg_usd": 1.0},
    {"id": "magic-internet-money", "symbol": "MIM", "name": "Magic Internet Money", "peg_usd": 1.0},
    {"id": "paypal-usd", "symbol": "PYUSD", "name": "PayPal USD", "peg_usd": 1.0},
    {"id": "ethena-usde", "symbol": "USDE", "name": "Ethena USDe", "peg_usd": 1.0},
)
ANNOUNCEMENT_EXCLUDE_WORDS = {
    "AND",
    "BINANCE",
    "COIN",
    "COMPLETED",
    "CONTRACT",
    "CONTRACTS",
    "DELIVER",
    "DELIST",
    "FUTURES",
    "LAUNCH",
    "LAUNCHES",
    "MARGIN",
    "MARGINED",
    "MULTIPLE",
    "NOTICE",
    "PAIR",
    "PAIRS",
    "PERPETUAL",
    "REMOVAL",
    "REMOVE",
    "SPOT",
    "THE",
    "TRADING",
    "TRADFI",
    "UPDATES",
    "WILL",
    "USD",
    "USDM",
    "USDS",
    "USDT",
    "USDC",
}


def unset_proxy_env():
    for key in PROXY_ENV_KEYS:
        os.environ.pop(key, None)


def get_text(url):
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        return r.read().decode()


def get(url):
    return json.loads(get_text(url))


def build_ssh_curl_command(url):
    remote = "curl -L --compressed -sS --connect-timeout 12 --max-time 30 " + shlex.quote(url)
    return [
        "ssh",
        "-i",
        SSH_SG_KEY,
        "-o",
        "BatchMode=yes",
        "-o",
        "ConnectTimeout=12",
        "-o",
        "StrictHostKeyChecking=accept-new",
        SSH_SG_HOST,
        remote,
    ]


def get_text_via_ssh_sg(url):
    cmd = build_ssh_curl_command(url)
    return subprocess.check_output(cmd, timeout=45).decode()


def get_via_ssh_sg(url):
    return json.loads(get_text_via_ssh_sg(url))


def make_fetchers(fetch_via_ssh_sg=False):
    if fetch_via_ssh_sg:
        return get_via_ssh_sg, get_text_via_ssh_sg
    return get, get_text


def scan_funding_oi(fetch_json=get, sleep_fn=time.sleep):
    prem = fetch_json(f"{BASE}/fapi/v1/premiumIndex")
    tick = {t["symbol"]: t for t in fetch_json(f"{BASE}/fapi/v1/ticker/24hr")}
    rows = []
    for p in prem:
        s = p.get("symbol", "")
        if not s.endswith("USDT"):
            continue
        try:
            fr = float(p.get("lastFundingRate") or 0)
            t = tick.get(s, {})
            chg = float(t.get("priceChangePercent") or 0)
            qv = float(t.get("quoteVolume") or 0)
        except (TypeError, ValueError):
            continue
        # 初筛：funding极端（|8h费率|>=0.3%）或 价格异动（|24h|>=25%且量>=500万USDT）
        if abs(fr) >= 0.003 or (abs(chg) >= 25 and qv >= 5e6):
            rows.append({"symbol": s, "funding_8h": fr, "chg24h_pct": chg, "quote_vol_usdt": qv})
    rows.sort(key=lambda r: abs(r["funding_8h"]), reverse=True)
    # 对前8个候选补OI 24h变化（骤增/骤降是机制核心变量）
    for r in rows[:8]:
        try:
            oi = fetch_json(f"{BASE}/futures/data/openInterestHist?symbol={r['symbol']}&period=1h&limit=25")
            if len(oi) >= 2:
                a, b = float(oi[0]["sumOpenInterestValue"]), float(oi[-1]["sumOpenInterestValue"])
                r["oi_24h_ago_usdt"], r["oi_now_usdt"] = a, b
                r["oi_24h_ratio"] = round(b / a, 3) if a > 0 else None
            sleep_fn(0.3)
        except Exception as e:  # noqa: BLE001 —— 单symbol失败不废全扫描
            r["oi_error"] = str(e)[:80]
    return rows


def build_legacy_funding_output(scan_utc, rows):
    return {"scan_utc": scan_utc, "n_prescreen": len(rows), "candidates": rows[:20]}


def funding_rows_to_candidates(rows):
    candidates = []
    for row in rows[:20]:
        candidate = dict(row)
        candidate.update(
            {
                "source": "funding_oi_squeeze",
                "event_type": "funding_oi_price_anomaly",
                "url": f"{BASE}/fapi/v1/premiumIndex",
                "source_url": f"{BASE}/fapi/v1/ticker/24hr",
                "raw": {
                    "funding_8h": row.get("funding_8h"),
                    "chg24h_pct": row.get("chg24h_pct"),
                    "quote_vol_usdt": row.get("quote_vol_usdt"),
                    "oi_24h_ratio": row.get("oi_24h_ratio"),
                },
            }
        )
        candidates.append(candidate)
    return candidates


def article_catalog_url(catalog_id, page_size):
    return f"{BINANCE_CMS}?catalogId={catalog_id}&pageNo=1&pageSize={page_size}"


def article_detail_url(code):
    return f"{BINANCE_ARTICLE}?articleCode={code}"


def classify_announcement(title, catalog_id):
    lower = title.lower()
    if "futures will launch" in lower and "perpetual" in lower:
        return "new_perp_listing"
    if "futures" in lower and "delist" in lower and "perpetual" in lower:
        return "futures_delist"
    if "contract size" in lower and "perpetual" in lower:
        return "futures_contract_size_adjustment"
    if catalog_id == 161 and any(word in lower for word in ("delist", "remove", "removal")):
        return "binance_removal_notice"
    return None


def extract_announcement_symbols(title):
    normalized = (
        title.replace("USDⓈ", "USD")
        .replace("USD-M", "USDM")
        .replace("USDⓈ-M", "USDM")
        .replace("&", " ")
        .replace("/", " ")
    )
    symbols = []
    for token in re.findall(r"\b[A-Z][A-Z0-9]{1,15}\b", normalized):
        if token in ANNOUNCEMENT_EXCLUDE_WORDS:
            continue
        if re.fullmatch(r"20\d{2}", token):
            continue
        if token not in symbols:
            symbols.append(token)
    return symbols


def extract_first_date(text):
    match = re.search(r"20\d{2}-\d{2}-\d{2}", text)
    return match.group(0) if match else None


def scan_binance_announcements(fetch_json=get, catalog_ids=(48, 49, 161), page_size=50):
    candidates = []
    for catalog_id in catalog_ids:
        source_url = article_catalog_url(catalog_id, page_size)
        payload = fetch_json(source_url)
        for article in (payload.get("data") or {}).get("articles") or []:
            title = article.get("title") or ""
            event_type = classify_announcement(title, catalog_id)
            if not event_type:
                continue
            code = article.get("code")
            candidates.append(
                {
                    "source": "binance_announcement",
                    "event_type": event_type,
                    "symbol": ",".join(extract_announcement_symbols(title)),
                    "symbols": extract_announcement_symbols(title),
                    "title": title,
                    "event_date": extract_first_date(title),
                    "article_id": article.get("id"),
                    "article_code": code,
                    "catalog_id": catalog_id,
                    "url": article_detail_url(code) if code else source_url,
                    "source_url": source_url,
                    "raw": {
                        "id": article.get("id"),
                        "code": code,
                        "title": title,
                        "catalog_id": catalog_id,
                    },
                }
            )
    return candidates


def _json_from_next_data(html_text):
    match = re.search(
        r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>',
        html_text,
        flags=re.S,
    )
    if not match:
        raise ValueError("__NEXT_DATA__ not found")
    return json.loads(html.unescape(match.group(1)))


def _parse_iso_utc(value):
    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def _safe_float(value):
    try:
        if value is None:
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _cryptorank_vesting_url(key, fallback_url):
    return f"https://cryptorank.io/price/{key}/vesting" if key else fallback_url


def _passes_unlock_thresholds(unlock_usd, unlock_market_cap_pct, min_unlock_usd, min_unlock_market_cap_pct):
    if unlock_usd is None or unlock_usd < min_unlock_usd:
        return False
    if unlock_market_cap_pct is not None and unlock_market_cap_pct < min_unlock_market_cap_pct:
        return False
    return True


def _days_until(event_dt, now_dt, max_days):
    if not event_dt:
        return None
    days_until = (event_dt.date() - now_dt.date()).days
    if days_until < 0 or days_until > max_days:
        return None
    return days_until


def _sort_unlock_candidates(candidates):
    candidates.sort(key=lambda r: (r["days_until_unlock"], -(r.get("unlock_market_cap_pct") or 0)))
    return candidates


def _scan_cryptorank_important_unlocks(
    fetch_text,
    now_dt,
    min_unlock_usd,
    min_unlock_market_cap_pct,
    max_days,
    source_url=CRYPTORANK_IMPORTANT_UNLOCKS_URL,
):
    payload = json.loads(fetch_text(source_url))
    if not isinstance(payload, list):
        raise ValueError(f"{source_url} returned {type(payload).__name__}, expected list")

    candidates = []
    for row in payload:
        if not isinstance(row, dict):
            continue
        key = row.get("key")
        symbol = row.get("symbol")
        if row.get("isHidden") or not key or not symbol:
            continue
        event_dt = _parse_iso_utc(row.get("unlockDate"))
        days_until = _days_until(event_dt, now_dt, max_days)
        if days_until is None:
            continue
        unlock_usd = _safe_float(row.get("unlockUsd"))
        unlock_market_cap_pct = _safe_float(row.get("tokensPercent"))
        if not _passes_unlock_thresholds(
            unlock_usd,
            unlock_market_cap_pct,
            min_unlock_usd,
            min_unlock_market_cap_pct,
        ):
            continue
        candidates.append(
            {
                "source": "token_unlock_cryptorank",
                "event_type": "upcoming_unlock",
                "key": key,
                "symbol": symbol,
                "name": row.get("name"),
                "unlock_date": event_dt.date().isoformat(),
                "days_until_unlock": days_until,
                "price_usd": None,
                "unlock_tokens": None,
                "unlock_usd": round(unlock_usd, 2),
                "unlock_market_cap_pct": unlock_market_cap_pct,
                "market_cap_usd": None,
                "allocations": [],
                "url": _cryptorank_vesting_url(key, source_url),
                "source_url": source_url,
                "raw": {
                    "key": key,
                    "isHidden": row.get("isHidden"),
                    "source_shape": "important_upcoming_unlocks",
                },
            }
        )
    return _sort_unlock_candidates(candidates)


def _scan_cryptorank_next_data_unlocks(
    fetch_text,
    now_dt,
    min_unlock_usd,
    min_unlock_market_cap_pct,
    max_days,
    url,
):
    page = fetch_text(url)
    data = _json_from_next_data(page)
    rows = ((data.get("props") or {}).get("pageProps") or {}).get("fallbackData", {}).get("data") or []
    candidates = []
    for row in rows:
        event_dt = _parse_iso_utc(row.get("date"))
        days_until = _days_until(event_dt, now_dt, max_days)
        if days_until is None:
            continue
        price = _safe_float(row.get("price")) or 0.0
        allocations = []
        unlock_tokens = 0.0
        for item in row.get("nextUnlocks") or []:
            tokens = _safe_float(item.get("tokens")) or 0.0
            unlock_tokens += tokens
            allocations.append(
                {
                    "name": item.get("allocationName"),
                    "tokens": tokens,
                    "date": item.get("date"),
                }
            )
        unlock_usd = unlock_tokens * price
        unlock_market_cap_pct = _safe_float(row.get("nextUnlockPercent"))
        if not _passes_unlock_thresholds(
            unlock_usd,
            unlock_market_cap_pct,
            min_unlock_usd,
            min_unlock_market_cap_pct,
        ):
            continue
        key = row.get("key")
        candidates.append(
            {
                "source": "token_unlock_cryptorank",
                "event_type": "upcoming_unlock",
                "key": key,
                "symbol": row.get("symbol"),
                "name": row.get("name"),
                "unlock_date": event_dt.date().isoformat(),
                "days_until_unlock": days_until,
                "price_usd": price,
                "unlock_tokens": unlock_tokens,
                "unlock_usd": round(unlock_usd, 2),
                "unlock_market_cap_pct": unlock_market_cap_pct,
                "market_cap_usd": _safe_float(row.get("marketCap")),
                "allocations": allocations[:5],
                "url": _cryptorank_vesting_url(key, url),
                "source_url": url,
                "raw": {"id": row.get("id"), "key": key, "chg24h": row.get("chg24h")},
            }
        )
    return _sort_unlock_candidates(candidates)


def scan_token_unlocks(
    fetch_text=get_text,
    now_dt=None,
    min_unlock_usd=100000,
    min_unlock_market_cap_pct=0.5,
    max_days=14,
    url=CRYPTORANK_UNLOCK_URL,
):
    now_dt = now_dt or datetime.now(timezone.utc)
    errors = []
    try:
        return _scan_cryptorank_important_unlocks(
            fetch_text,
            now_dt,
            min_unlock_usd,
            min_unlock_market_cap_pct,
            max_days,
        )
    except Exception as e:  # noqa: BLE001 —— CryptoRank结构漂移时降级到SSR兜底
        errors.append(f"{CRYPTORANK_IMPORTANT_UNLOCKS_URL}: {e}")

    try:
        return _scan_cryptorank_next_data_unlocks(
            fetch_text,
            now_dt,
            min_unlock_usd,
            min_unlock_market_cap_pct,
            max_days,
            url,
        )
    except Exception as e:  # noqa: BLE001 —— 让run_scan记录source_errors，不废全局扫描
        errors.append(f"{url}: {e}")

    raise ValueError("CryptoRank token_unlock sources failed: " + "; ".join(errors))


def coingecko_price_url(assets):
    ids = ",".join(asset["id"] for asset in assets)
    return (
        f"{COINGECKO_SIMPLE_PRICE}?ids={ids}"
        "&vs_currencies=usd&include_24hr_change=true&include_last_updated_at=true"
    )


def scan_depeg_assets(fetch_json=get, assets=DEFAULT_PEG_ASSETS, threshold=0.02):
    source_url = coingecko_price_url(assets)
    payload = fetch_json(source_url)
    candidates = []
    for asset in assets:
        coin_id = asset["id"]
        row = payload.get(coin_id) or {}
        price = _safe_float(row.get("usd"))
        if price is None:
            continue
        peg = float(asset.get("peg_usd", 1.0))
        deviation = price / peg - 1.0
        if abs(deviation) < threshold:
            continue
        candidates.append(
            {
                "source": "depeg_coingecko",
                "event_type": "peg_deviation",
                "symbol": asset["symbol"],
                "name": asset["name"],
                "coingecko_id": coin_id,
                "peg_usd": peg,
                "price_usd": price,
                "deviation_pct": deviation * 100,
                "usd_24h_change_pct": row.get("usd_24h_change"),
                "last_updated_at": row.get("last_updated_at"),
                "url": f"{COINGECKO_COIN_URL}/{coin_id}",
                "source_url": source_url,
                "raw": row,
            }
        )
    candidates.sort(key=lambda r: abs(r["deviation_pct"]), reverse=True)
    return candidates


def parse_sources(sources_text, skip_text=""):
    requested = [s.strip() for s in sources_text.split(",") if s.strip()]
    skipped = {s.strip() for s in skip_text.split(",") if s.strip()}
    unknown = (set(requested) | skipped) - set(DEFAULT_SOURCES)
    if unknown:
        raise ValueError(f"unknown source(s): {', '.join(sorted(unknown))}")
    return [s for s in requested if s not in skipped]


def run_scan(fetch_json=get, fetch_text=get_text, sources=DEFAULT_SOURCES):
    candidates = []
    errors = []
    legacy_funding = None
    funding_rows = []
    for source in sources:
        try:
            if source == "funding_oi":
                funding_rows = scan_funding_oi(fetch_json=fetch_json)
                legacy_funding = build_legacy_funding_output("", funding_rows)
                candidates.extend(funding_rows_to_candidates(funding_rows))
            elif source == "binance_announcements":
                candidates.extend(scan_binance_announcements(fetch_json=fetch_json))
            elif source == "token_unlocks":
                candidates.extend(scan_token_unlocks(fetch_text=fetch_text))
            elif source == "depeg":
                candidates.extend(scan_depeg_assets(fetch_json=fetch_json))
        except Exception as e:  # noqa: BLE001 —— 单源失败不废全扫描
            errors.append({"source": source, "error": str(e)[:240]})
    return candidates, errors, legacy_funding, funding_rows


def candidate_sort_key(candidate):
    source_rank = {
        "depeg_coingecko": 0,
        "binance_announcement": 1,
        "token_unlock_cryptorank": 2,
        "funding_oi_squeeze": 3,
    }
    return (
        source_rank.get(candidate.get("source"), 9),
        candidate.get("days_until_unlock", 999),
        -abs(float(candidate.get("funding_8h") or 0)),
        -abs(float(candidate.get("deviation_pct") or 0)),
    )


def table_value(candidate):
    if candidate.get("source") == "funding_oi_squeeze":
        return "fund %.4f%% chg %.1f%%" % (
            candidate.get("funding_8h", 0) * 100,
            candidate.get("chg24h_pct", 0),
        )
    if candidate.get("source") == "depeg_coingecko":
        return "dev %.2f%% px %.6g" % (candidate.get("deviation_pct", 0), candidate.get("price_usd", 0))
    if candidate.get("source") == "token_unlock_cryptorank":
        return "unlock $%.2f %.2f%%" % (
            candidate.get("unlock_usd", 0),
            candidate.get("unlock_market_cap_pct") or 0,
        )
    return candidate.get("title", "")[:55]


def print_candidate_table(candidates, limit=30):
    print("SOURCE                 SYMBOLS                  EVENT                         VALUE")
    print("-" * 96)
    for item in candidates[:limit]:
        symbol = item.get("symbol") or ",".join(item.get("symbols") or [])
        print(
            "%-22s %-24s %-29s %s"
            % (
                str(item.get("source", ""))[:22],
                str(symbol or "")[:24],
                str(item.get("event_type", ""))[:29],
                table_value(item),
            )
        )


def build_output(scan_utc, sources, candidates, errors, legacy_funding, funding_rows):
    legacy = legacy_funding or {"scan_utc": scan_utc, "n_prescreen": 0, "candidates": []}
    legacy["scan_utc"] = scan_utc
    return {
        "schema_version": "P0-RES-016",
        "scan_utc": scan_utc,
        "sources_requested": list(sources),
        "n_prescreen": len(funding_rows),
        "legacy_funding_oi": legacy,
        "source_errors": errors,
        "candidates": candidates,
    }


def parse_args():
    parser = argparse.ArgumentParser(description="只读高频thesis候选扫描器")
    parser.add_argument("--sources", default=",".join(DEFAULT_SOURCES), help="逗号分隔源名")
    parser.add_argument("--skip-sources", default="", help="逗号分隔要跳过的源名")
    parser.add_argument("--fetch-via-ssh-sg", action="store_true", help="通道B：经SG SSH读取公开接口")
    parser.add_argument("--output-dir", default=str(OUT))
    parser.add_argument("--table-limit", type=int, default=30)
    return parser.parse_args()

def main():
    args = parse_args()
    unset_proxy_env()
    now = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M")
    sources = parse_sources(args.sources, args.skip_sources)
    fetch_json, fetch_text = make_fetchers(fetch_via_ssh_sg=args.fetch_via_ssh_sg)
    candidates, errors, legacy_funding, funding_rows = run_scan(
        fetch_json=fetch_json,
        fetch_text=fetch_text,
        sources=sources,
    )
    candidates = sorted(candidates, key=candidate_sort_key)
    out = build_output(now, sources, candidates, errors, legacy_funding, funding_rows)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(exist_ok=True)
    f = output_dir / f"thesis_hf_scan_{now}.json"
    f.write_text(json.dumps(out, indent=1, ensure_ascii=False))
    print("WROTE", f)
    if errors:
        print("SOURCE_ERRORS", json.dumps(errors, ensure_ascii=False))
    print_candidate_table(candidates, limit=args.table_limit)

if __name__ == "__main__":
    main()
