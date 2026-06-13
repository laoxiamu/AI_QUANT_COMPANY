#!/usr/bin/env python3
"""B5 collector data-plane isolation diagnostic.

The script tests whether Binance USDT-M futures aggTrade WebSocket data frames
arrive through several independent client/proxy paths. It intentionally records
only transport metadata, never raw trade payloads or prices.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
OUTPUT_DIR = ROOT / "06_RESEARCH" / "CODE" / "output"
RESULTS_DIR = ROOT / "06_RESEARCH" / "RESULTS"

WS_PATH_URL = "wss://fstream.binance.com/ws/btcusdt@aggTrade"
STREAM_URL = "wss://fstream.binance.com/stream?streams=btcusdt@aggTrade"
STREAM_EXPLICIT_443_URL = "wss://fstream.binance.com:443/stream?streams=btcusdt@aggTrade"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def frame_metadata(message: Any) -> dict[str, Any]:
    if isinstance(message, bytes):
        return {"kind": "bytes", "bytes": len(message)}
    text = str(message)
    meta: dict[str, Any] = {"kind": "text", "bytes": len(text.encode("utf-8"))}
    try:
        parsed = json.loads(text)
        meta["json_type"] = type(parsed).__name__
        if isinstance(parsed, dict):
            meta["top_keys"] = sorted(parsed.keys())
            event_type = parsed.get("e")
            if event_type is None and isinstance(parsed.get("data"), dict):
                event_type = parsed["data"].get("e")
            if event_type is not None:
                meta["event_type"] = event_type
    except json.JSONDecodeError:
        meta["json_type"] = "invalid"
    return meta


def base_result(name: str, client: str, proxy: str, url: str, duration_s: float) -> dict[str, Any]:
    return {
        "name": name,
        "client": client,
        "proxy": proxy,
        "url": url,
        "duration_s": duration_s,
        "started_at_utc": utc_now(),
        "handshake_ok": False,
        "frames": 0,
        "bytes": 0,
        "first_frame_latency_s": None,
        "first_frame_meta": None,
        "elapsed_s": 0.0,
        "error": None,
    }


def test_websocket_client(
    name: str,
    url: str,
    duration_s: float,
    proxy_host: str,
    proxy_port: int,
    proxy_type: str,
) -> dict[str, Any]:
    import websocket

    result = base_result(name, "websocket-client", f"{proxy_type}://{proxy_host}:{proxy_port}", url, duration_s)
    start = time.monotonic()
    ws = None
    try:
        ws = websocket.create_connection(
            url,
            timeout=10,
            http_proxy_host=proxy_host,
            http_proxy_port=proxy_port,
            proxy_type=proxy_type,
        )
        result["handshake_ok"] = True
        ws.settimeout(1.0)
        deadline = start + duration_s
        while time.monotonic() < deadline:
            try:
                message = ws.recv()
            except websocket.WebSocketTimeoutException:
                continue
            if message is None:
                continue
            meta = frame_metadata(message)
            result["frames"] += 1
            result["bytes"] += int(meta["bytes"])
            if result["first_frame_latency_s"] is None:
                result["first_frame_latency_s"] = round(time.monotonic() - start, 3)
                result["first_frame_meta"] = meta
    except Exception as exc:  # noqa: BLE001 - diagnostic must preserve failure class
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        if ws is not None:
            try:
                ws.close()
            except Exception:
                pass
        result["elapsed_s"] = round(time.monotonic() - start, 3)
        result["ended_at_utc"] = utc_now()
    return result


async def test_websockets(
    name: str,
    url: str,
    duration_s: float,
    proxy_url: str,
) -> dict[str, Any]:
    import websockets

    result = base_result(name, "websockets", proxy_url, url, duration_s)
    start = time.monotonic()
    try:
        async with websockets.connect(
            url,
            proxy=proxy_url,
            open_timeout=10,
            ping_interval=20,
            ping_timeout=10,
            close_timeout=5,
        ) as ws:
            result["handshake_ok"] = True
            deadline = start + duration_s
            while time.monotonic() < deadline:
                timeout = max(0.05, min(1.0, deadline - time.monotonic()))
                try:
                    message = await asyncio.wait_for(ws.recv(), timeout=timeout)
                except asyncio.TimeoutError:
                    continue
                meta = frame_metadata(message)
                result["frames"] += 1
                result["bytes"] += int(meta["bytes"])
                if result["first_frame_latency_s"] is None:
                    result["first_frame_latency_s"] = round(time.monotonic() - start, 3)
                    result["first_frame_meta"] = meta
    except Exception as exc:  # noqa: BLE001 - diagnostic must preserve failure class
        result["error"] = f"{type(exc).__name__}: {exc}"
    finally:
        result["elapsed_s"] = round(time.monotonic() - start, 3)
        result["ended_at_utc"] = utc_now()
    return result


def tool_inventory() -> dict[str, Any]:
    curl_path = shutil.which("curl")
    curl_protocols: list[str] = []
    if curl_path:
        try:
            proc = subprocess.run(
                [curl_path, "--version"],
                check=False,
                capture_output=True,
                text=True,
                timeout=5,
            )
            for line in proc.stdout.splitlines():
                if line.startswith("Protocols:"):
                    curl_protocols = line.split(":", 1)[1].strip().split()
                    break
        except Exception:
            curl_protocols = []
    return {
        "curl": {
            "path": curl_path,
            "supports_ws": "ws" in curl_protocols or "wss" in curl_protocols,
            "protocols": curl_protocols,
        },
        "websocat": {"path": shutil.which("websocat")},
    }


def verdict_for_row(row: dict[str, Any]) -> str:
    if row["frames"] > 0:
        return "DATA"
    if row["handshake_ok"]:
        return "HANDSHAKE_ONLY_ZERO_FRAMES"
    return "CONNECT_FAIL"


def infer_layer(results: list[dict[str, Any]]) -> str:
    tested = [r for r in results if r.get("tested", True)]
    handshake_paths = [r for r in tested if r["handshake_ok"]]
    any_data = any(r["frames"] > 0 for r in tested)
    all_handshake_zero = tested and all(r["handshake_ok"] and r["frames"] == 0 for r in tested)
    any_connect_fail = any((not r["handshake_ok"]) for r in tested)
    if any_data:
        winners = ", ".join(r["name"] for r in tested if r["frames"] > 0)
        return (
            "At least one Mac-side path receives aggTrade frames. The break is not the Binance "
            f"stream itself; collector should be switched toward the working path(s): {winners}."
        )
    if all_handshake_zero:
        return (
            "All tested Mac-side paths completed WebSocket handshake but received zero aggTrade "
            "frames for the full window. This points below the Python library layer, most likely "
            "Clash/upstream VM forwarding or provider data-plane filtering. Mac-side collector "
            "changes are not sufficient; run on the VM directly."
        )
    if len(handshake_paths) >= 3 and all(r["frames"] == 0 for r in handshake_paths):
        failed = ", ".join(r["name"] for r in tested if not r["handshake_ok"]) or "none"
        return (
            "All handshake-capable Mac-side paths received zero aggTrade frames for the full "
            "60s windows across independent client/proxy/URL combinations. This rules out a "
            "single Python library failure and points below the library layer, most likely "
            "Clash/upstream VM forwarding or provider data-plane filtering. Mac-side collector "
            f"changes are not sufficient; run on the VM directly. Non-handshake variants: {failed}."
        )
    if any_connect_fail:
        return (
            "No path received data frames and at least one path could not complete handshake. "
            "This is inconclusive between local proxy availability and upstream forwarding; inspect "
            "the connection errors before changing collector logic."
        )
    return "No conclusive result."


def markdown_report(payload: dict[str, Any]) -> str:
    rows = []
    for r in payload["tests"]:
        rows.append(
            "| {name} | {client} | {proxy} | {url} | {handshake} | {frames} | {latency} | {elapsed} | {verdict} | {error} |".format(
                name=r["name"],
                client=r["client"],
                proxy=r["proxy"],
                url=r["url"],
                handshake="YES" if r["handshake_ok"] else "NO",
                frames=r["frames"],
                latency="" if r["first_frame_latency_s"] is None else r["first_frame_latency_s"],
                elapsed=r["elapsed_s"],
                verdict=verdict_for_row(r),
                error=(r["error"] or "").replace("|", "/"),
            )
        )

    tool = payload["tool_inventory"]
    curl_note = (
        f"`{tool['curl']['path']}` supports ws/wss"
        if tool["curl"]["supports_ws"]
        else f"`{tool['curl']['path']}` does not advertise ws/wss protocol support"
    )
    websocat_note = f"`{tool['websocat']['path']}`" if tool["websocat"]["path"] else "not installed"

    return "\n".join(
        [
            "# 20260612 Collector Data-Plane Diagnostic",
            "",
            "## Scope",
            "",
            "- Task: B5 only; test Binance USDT-M `btcusdt@aggTrade` WebSocket data frames through independent Mac-side paths.",
            "- Payload discipline: raw trade frames and prices were not persisted; only transport metadata was written.",
            f"- Run timestamp UTC: `{payload['run_started_at_utc']}`.",
            f"- Per-path target window: `{payload['duration_s']}s`.",
            "",
            "## Tool Availability",
            "",
            f"- curl: {curl_note}.",
            f"- websocat: {websocat_note}.",
            "",
            "## 判定矩阵",
            "",
            "| Path | Client | Proxy | URL | Handshake | Frames | First frame s | Elapsed s | Verdict | Error |",
            "|---|---|---|---|---:|---:|---:|---:|---|---|",
            *rows,
            "",
            "## Layer Diagnosis",
            "",
            payload["layer_diagnosis"],
            "",
            "## Collector Patch Recommendation",
            "",
            payload["patch_recommendation"],
            "",
            "## Reproducibility",
            "",
            "```bash",
            "PYTHONPATH=/private/tmp/ai_quant_b5_deps python3 06_RESEARCH/CODE/collector_dataplane_diag.py --duration 60",
            "```",
            "",
            f"JSON output: `{payload['json_output']}`",
            "",
            "## Protocol Notes",
            "",
            "- No HOLDOUT path was read.",
            "- The diagnostic script does not read `06_RESEARCH/DATA/`.",
            "- During initial repository search, a broad `rg` command accidentally printed post-cutoff market rows because the text pattern matched numeric values. Those rows were not used in this diagnostic or conclusion.",
        ]
    )


def patch_recommendation(results: list[dict[str, Any]]) -> str:
    winners = [r for r in results if r["frames"] > 0]
    if not winners:
        return '全部测试路径 60s 零数据帧；按任务书口径，结论为 "Mac 侧无解，须 VM 直跑"。不建议在 Mac 采集器上继续打补丁。'
    best = max(winners, key=lambda r: r["frames"])
    if best["client"] == "websockets":
        return (
            "建议采集器改为 asyncio `websockets.connect(..., proxy='socks5://127.0.0.1:7897')`，"
            "并使用本次可收帧 URL；保留现有 JSONL 落盘和心跳逻辑。"
        )
    return (
        "建议采集器继续使用 `websocket-client`，但切换到本次可收帧路径的 URL/proxy 组合；"
        "同时把 60s 零帧作为健康检查失败条件并触发重连。"
    )


async def run(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "run_started_at_utc": utc_now(),
        "duration_s": args.duration,
        "proxy_host": args.proxy_host,
        "proxy_port": args.proxy_port,
        "tool_inventory": tool_inventory(),
        "tests": [],
    }

    payload["tests"].append(
        test_websocket_client(
            "websocket_client_http_ws",
            WS_PATH_URL,
            args.duration,
            args.proxy_host,
            args.proxy_port,
            "http",
        )
    )
    payload["tests"].append(
        await test_websockets(
            "websockets_socks_ws",
            WS_PATH_URL,
            args.duration,
            f"socks5://{args.proxy_host}:{args.proxy_port}",
        )
    )
    payload["tests"].append(
        test_websocket_client(
            "websocket_client_http_stream",
            STREAM_URL,
            args.duration,
            args.proxy_host,
            args.proxy_port,
            "http",
        )
    )
    payload["tests"].append(
        await test_websockets(
            "websockets_socks_stream",
            STREAM_URL,
            args.duration,
            f"socks5://{args.proxy_host}:{args.proxy_port}",
        )
    )
    payload["tests"].append(
        test_websocket_client(
            "websocket_client_http_stream_explicit_443",
            STREAM_EXPLICIT_443_URL,
            args.duration,
            args.proxy_host,
            args.proxy_port,
            "http",
        )
    )
    payload["tests"].append(
        await test_websockets(
            "websockets_socks_stream_explicit_443",
            STREAM_EXPLICIT_443_URL,
            args.duration,
            f"socks5://{args.proxy_host}:{args.proxy_port}",
        )
    )

    payload["layer_diagnosis"] = infer_layer(payload["tests"])
    payload["patch_recommendation"] = patch_recommendation(payload["tests"])
    payload["run_ended_at_utc"] = utc_now()
    return payload


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--duration", type=float, default=60.0)
    parser.add_argument("--proxy-host", default="127.0.0.1")
    parser.add_argument("--proxy-port", type=int, default=7897)
    parser.add_argument("--json-output", default=str(OUTPUT_DIR / "collector_dataplane_diag.json"))
    parser.add_argument("--md-output", default=str(RESULTS_DIR / "20260612_collector_dataplane.md"))
    args = parser.parse_args()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    payload = asyncio.run(run(args))
    json_path = Path(args.json_output)
    md_path = Path(args.md_output)
    payload["json_output"] = str(json_path)
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(markdown_report(payload) + "\n", encoding="utf-8")
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
