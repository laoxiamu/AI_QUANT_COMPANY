import subprocess
from datetime import date, timedelta
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT = REPO_ROOT / "01_MEMORY_CORE" / "state_check.py"


def patrol_traces(days: int = 8) -> str:
    """近 N 天巡检留痕，供合成样本使用（2026-07-30 起 state_check 会查留痕）。"""
    today = date.today()
    return "\n".join(
        f"**{(today - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：测试样本"
        for k in range(days)
    )


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
        current=f"Phase 1\n最新DEC=DEC-082\n{patrol_traces()}\n",
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
        current=f"Phase 1\n最新DEC=DEC-082\n{patrol_traces()}\n",
        task_plan="Phase 1\n",
        boot="Phase 1\n最新DEC=DEC-082\n",
        decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode == 0, result.stdout + result.stderr


def test_latest_dec_mismatch_returns_nonzero(tmp_path: Path) -> None:
    write_auth_files(
        tmp_path,
        current=f"Phase 1\n最新DEC=DEC-081\n{patrol_traces()}\n",
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
        current=f"Phase 1\n最新DEC=DEC-082\n{patrol_traces()}\n",
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


def test_missing_patrol_trace_returns_nonzero(tmp_path: Path) -> None:
    """外部不变量：巡检班在 §1c 无留痕即告警。

    这是 2026-07-24~26「跑了≠落盘」5 班事故后补的独立防线——
    此前的修补写在巡检自己的提示词里，与失效模式同源，不构成检查。
    """
    # 昨天缺一班
    today = date.today()
    traces = "\n".join(
        f"**{(today - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：测试样本"
        for k in range(8)
        if k != 1
    )
    write_auth_files(
        tmp_path,
        current=f"Phase 1\n最新DEC=DEC-082\n{traces}\n",
        task_plan="Phase 1\n",
        boot="Phase 1\n最新DEC=DEC-082\n",
        decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
    )

    result = run_state_check(str(tmp_path))

    assert result.returncode != 0
    assert "留痕缺失" in result.stdout
    assert (today - timedelta(days=1)).isoformat() in result.stdout
