#!/usr/bin/env python3
"""Record the v5 negative permission test from the formal executor identity."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

import pandas as pd


ROOT = Path(__file__).resolve().parents[2]
WORK_DIR = ROOT / "06_RESEARCH" / "DATA" / "A1_WORK"
MANIFEST_PATH = WORK_DIR / "A1_HOLDOUT_MANIFEST.json"
SEALED_PATH = WORK_DIR / "sealed_holdout.enc"
LOG_PATH = WORK_DIR / "A1_HOLDOUT_PERMTEST.log"
KEY_PATH = Path.home() / ".aiquant_sealed" / "a1" / "a1_key.bin"
EXPECTED_KEY_DENIED_EXIT = 17
BOUNDARY_FAILURE_EXIT = 18


def decrypt_probe() -> int:
    """Fail before decryption when the executor cannot open the key."""
    if not SEALED_PATH.is_file():
        print(f"sealed ciphertext missing: {SEALED_PATH}", file=sys.stderr)
        return 19
    try:
        handle = KEY_PATH.open("rb")
    except OSError as exc:
        print(
            f"key file inaccessible; decryption not attempted: "
            f"{type(exc).__name__}: {exc}",
            file=sys.stderr,
        )
        return EXPECTED_KEY_DENIED_EXIT
    else:
        handle.close()
        print(
            "permission boundary failure: executor can open the key; "
            "sealed ciphertext was not decrypted",
            file=sys.stderr,
        )
        return BOUNDARY_FAILURE_EXIT


def run_test() -> int:
    manifest_command = [
        sys.executable,
        "-c",
        f"import json; json.load(open({str(MANIFEST_PATH)!r}))",
    ]
    manifest_probe = subprocess.run(manifest_command, capture_output=True, text=True)
    manifest_exit = manifest_probe.returncode
    try:
        manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
        manifest_reason = (
            f"manifest readable; work_rows={manifest['work_rows']}; "
            f"sealed_rows={manifest['sealed_rows']}"
        )
    except Exception as exc:
        manifest_reason = f"{type(exc).__name__}: {exc}"

    probe_command = [
        sys.executable,
        str(Path(__file__).resolve()),
        "--decrypt-probe",
    ]
    probe = subprocess.run(probe_command, capture_output=True, text=True)
    log = "\n".join(
        [
            "A1 HOLDOUT NEGATIVE PERMISSION TEST",
            f"tested_at_utc={pd.Timestamp.now(tz='UTC').strftime('%Y-%m-%dT%H:%M:%SZ')}",
            f"manifest_command={' '.join(manifest_command)}",
            f"manifest_exit_code={manifest_exit}",
            f"manifest_evidence={manifest_reason}",
            f"manifest_stderr={manifest_probe.stderr.strip()}",
            f"decrypt_command={' '.join(probe_command)}",
            f"decrypt_exit_code={probe.returncode}",
            f"decrypt_stdout={probe.stdout.strip()}",
            f"decrypt_stderr={probe.stderr.strip()}",
            (
                "overall=PASS"
                if manifest_exit == 0
                and probe.returncode == EXPECTED_KEY_DENIED_EXIT
                else "overall=FAIL"
            ),
            "",
        ]
    )
    LOG_PATH.write_text(log, encoding="utf-8")
    if manifest_exit != 0:
        return 1
    if probe.returncode != EXPECTED_KEY_DENIED_EXIT:
        return 2
    return 0


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--decrypt-probe", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    raise SystemExit(decrypt_probe() if args.decrypt_probe else run_test())


if __name__ == "__main__":
    main()
