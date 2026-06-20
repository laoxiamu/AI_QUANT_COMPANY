import subprocess
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "01_MEMORY_CORE" / "state_check.py"


def write_auth_files(root: Path, *, current: str, task_plan: str, boot: str, decision: str) -> None:
    (root / "CLAUDE.md").write_text("# marker\n", encoding="utf-8")
    (root / "01_MEMORY_CORE").mkdir(parents=True)
    (root / "00_PROJECT_MANAGEMENT").mkdir(parents=True)
    (root / "01_MEMORY_CORE" / "CURRENT_STATE.md").write_text(current, encoding="utf-8")
    (root / "00_PROJECT_MANAGEMENT" / "PROJECT_TASK_PLAN.md").write_text(task_plan, encoding="utf-8")
    (root / "01_MEMORY_CORE" / "BOOT_BRIEF.md").write_text(boot, encoding="utf-8")
    (root / "01_MEMORY_CORE" / "DECISION_LOG.md").write_text(decision, encoding="utf-8")


def run_state_check(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(SCRIPT), *args],
        cwd=cwd,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )


def test_bad_string_sample_returns_nonzero(tmp_path: Path) -> None:
    write_auth_files(
        tmp_path,
        current="Phase 1\n最新DEC=DEC-082\n",
        task_plan="Phase 1\n",
        boot="Phase 1\n最新DEC=DEC-082\n月化30%作为研究验收门槛\n",
        decision="[DEC-081]\n[DEC-082]\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode != 0
    assert "坏串" in result.stdout or "滞后告警" in result.stdout


def test_clean_sample_returns_zero(tmp_path: Path) -> None:
    write_auth_files(
        tmp_path,
        current="Phase 1\n最新DEC=DEC-082\n",
        task_plan="Phase 1\n",
        boot="Phase 1\n最新DEC=DEC-082\n",
        decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr


def test_latest_dec_mismatch_returns_nonzero(tmp_path: Path) -> None:
    write_auth_files(
        tmp_path,
        current="Phase 1\n最新DEC=DEC-081\n",
        task_plan="Phase 1\n",
        boot="Phase 1\n最新DEC=DEC-081\n",
        decision="[DEC-081]\n[DEC-082]\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode != 0
    assert "最新DEC" in result.stdout


def test_authority_conflict_returns_nonzero(tmp_path: Path) -> None:
    write_auth_files(
        tmp_path,
        current="Phase 1\n最新DEC=DEC-082\n",
        task_plan="Phase 0\n",
        boot="Phase 1\n最新DEC=DEC-082\n",
        decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode != 0
    assert "权威冲突" in result.stdout


def test_script_discovers_repo_root_from_any_cwd(tmp_path: Path) -> None:
    result = run_state_check(cwd=tmp_path)

    assert "[缺失]" not in result.stdout
    assert "AI_QUANT_COMPANY" in result.stdout


def test_builtin_self_test_passes() -> None:
    result = run_state_check("--self-test")

    assert result.returncode == 0, result.stdout + result.stderr
    assert "self-test" in result.stdout
