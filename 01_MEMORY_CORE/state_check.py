#!/usr/bin/env python3
"""state_check.py —— Memory Core 权威状态一致性自检（半自动）

用途：每次状态同步后跑一遍，抓"权威文件状态滞后/互相矛盾"这个反复出现的坑。
它不替代人判断——而是把关键不变量(阶段/失败计数)从各权威文件里抽出来并排显示，
并对已知的"过时坏串"报警。退出码非0=发现疑似滞后。

用法：python3 01_MEMORY_CORE/state_check.py [项目根路径]
默认项目根 = 按脚本位置向上寻找 CLAUDE.md
"""
import contextlib
import io
import re
import sys
import tempfile
from datetime import date, datetime, timedelta
from pathlib import Path

# 巡检留痕检查参数（2026-07-30 加，见 check_patrol_traces）
PATROL_START = date(2026, 7, 16)   # 每日巡检首个正式运行日
PATROL_LOOKBACK_DAYS = 7           # 回看窗；与周监控 7 天分辨率对齐
PATROL_GRACE_HOUR = 12             # 当日 12:00 前不计当日班（cron 10:01 + 执行时长余量）


AUTH_FILES = {
    "CURRENT_STATE":   "01_MEMORY_CORE/CURRENT_STATE.md",
    "TASK_PLAN":       "00_PROJECT_MANAGEMENT/PROJECT_TASK_PLAN.md",
    "BOOT_BRIEF":      "01_MEMORY_CORE/BOOT_BRIEF.md",
    "DECISION_LOG":    "01_MEMORY_CORE/DECISION_LOG.md",
}
# 注：PROJECT_OPERATING_STATE.md 和 PROJECT_MASTER_PLAN_v2.md 已废弃（2026-06-20重组）
# 权威文件路径变更：MASTER_PLAN → TASK_PLAN（PROJECT_TASK_PLAN.md）

# 已知"过时坏串"——出现即报警（随项目演进维护）
STALE_PATTERNS = [
    ("旧失败计数", r"历史实验失败 \*\*8次\*\*"),
    ("旧Alpha计数", r"独立Alpha假设 \*\*4/8\*\*"),
    ("旧阶段", r"Phase 0B — First Validated"),
    ("旧阶段", r"阶段 0A .*进行中"),
    ("旧Codex状态", r"尚未执行任何实际 Codex"),
    ("月化30验收门", r"(月化\s*30%[^\n]{0,30}(研究)?(验收|门槛|硬门|目标)|(验收|门槛|硬门)[^\n]{0,30}月化\s*30%)"),
    ("已验证主线误写", r"唯一已验证主线"),
    ("regime-adaptive误写新主线", r"新主线\s*=\s*regime-adaptive"),
    ("杠杆误作Alpha实验", r"(10[-–]20x\s*杠杆[^\n]{0,30}(实验|Alpha)|(实验|Alpha)[^\n]{0,30}10[-–]20x\s*杠杆)"),
    ("carry活跃主线误写", r"(唯一|当前|active|活动|研究)?主线[^\n]{0,40}carry(?![^\n]{0,20}(Dead|关闭|废弃|已死))"),
    # 2026-07-16 L1审计R4补强：本次审计人工抓到、机器漏报的过时串
    ("P0-C旧执行顺序残留", r"Claude继续P0-C"),
    ("regime-adaptive误作当前主线", r"当前唯一执行主线[^\n]{0,40}regime-adaptive"),
    ("引擎L-Holdout待决策过时", r"最重要待决策[^\n]{0,60}是否消耗Holdout"),
    ("调度器自动拾取协议过时", r"15min调度器自动拾取"),
]

# 关注的不变量（抽出来并排看）
INVARIANT_PATTERNS = {
    "阶段":   r"(Phase\s*[01][AB]?|阶段\s*[01][AB]?)",
    "失败计数": r"(历史(实验)?失败\s*\*?\*?\s*\d+|独立\s*Alpha[^\n]{0,20}\d/8)",
}

OK_CONTEXT_PATTERNS = {
    "月化30验收门": [
        r"不是验收",
        r"非验收",
        r"出研究验收",
        r"不是研究验收",
        r"误当验收",
        r"不再是.*验收",
        r"不能当",
        r"移出研究验收",
        r"修订删除",
        r"纠正",
    ],
    "carry活跃主线误写": [
        r"carry不在active位",
        r"carry\s*(仍)?Dead",
        r"carry.*关闭",
        r"carry.*废弃",
        r"carry.*已死",
    ],
}


def discover_project_root(start: Path) -> Path:
    for candidate in [start, *start.parents]:
        if (candidate / "CLAUDE.md").exists() and (candidate / "01_MEMORY_CORE").exists():
            return candidate
    raise FileNotFoundError(f"无法从 {start} 向上定位项目根（需 CLAUDE.md + 01_MEMORY_CORE/）")


def read(root: Path, path: str):
    full = root / path
    if not full.exists():
        return None
    with full.open(encoding="utf-8") as f:
        return f.read()


def line_is_allowed(label: str, line: str) -> bool:
    return any(re.search(pat, line, re.I) for pat in OK_CONTEXT_PATTERNS.get(label, []))


def extract_latest_dec_pointer(text: str) -> int | None:
    direct = re.search(r"(最新\s*DEC|最新)\s*[=:=：]?\s*DEC-(\d{3})", text, re.I)
    if direct:
        return int(direct.group(2))

    header = "\n".join(text.splitlines()[:20])
    header_decisions = [
        int(match.group(1))
        for match in re.finditer(r"DEC-(\d{3})", header)
        if re.search(r"(版本|最后更新|更新|同步|顶层)", header[max(0, match.start() - 40):match.end() + 40])
    ]
    return max(header_decisions) if header_decisions else None


def max_decision_number(decision_log: str) -> int | None:
    nums = [int(match.group(1)) for match in re.finditer(r"DEC-(\d{3})", decision_log)]
    return max(nums) if nums else None


def extract_phase(name: str, text: str) -> str | None:
    if name == "CURRENT_STATE":
        for line in text.splitlines():
            if "阶段" in line:
                match = re.search(r"Phase\s*([0-9][AB]?)", line, re.I)
                if match:
                    return f"Phase {match.group(1)}"

    if name == "BOOT_BRIEF":
        for line in text.splitlines()[:15]:
            match = re.search(r"\bPhase\s*([0-9][AB]?)\b", line, re.I)
            if match:
                return f"Phase {match.group(1)}"

    if name == "TASK_PLAN":
        lines = text.splitlines()
        focus_lines = []
        used_focus_section = False
        for idx, line in enumerate(lines):
            if "当前焦点" in line:
                used_focus_section = True
                for focus_line in lines[idx + 1:]:
                    if focus_line.startswith("## "):
                        break
                    focus_lines.append(focus_line)
                break
        scan_lines = focus_lines if focus_lines else lines[:50]
        for line in scan_lines:
            if re.search(r"Phase\s*[0-9]\s*[-~—]\s*[0-9]", line, re.I):
                continue
            if re.match(r"#+\s*Phase\s+[0-9]", line, re.I):
                continue
            match = re.search(r"\bPhase\s*([0-9][AB]?)\b", line, re.I)
            if match:
                return f"Phase {match.group(1)}"
        if used_focus_section:
            return None

    match = re.search(r"\bPhase\s*([0-9][AB]?)\b|阶段\s*([0-9][AB]?)", text, re.I)
    if match:
        return f"Phase {match.group(1) or match.group(2)}"
    return None


def check_latest_dec(contents: dict[str, str | None]) -> int:
    decision_log = contents.get("DECISION_LOG")
    if not decision_log:
        return 0

    actual = max_decision_number(decision_log)
    if actual is None:
        print("  [权威冲突] DECISION_LOG 未找到 DEC-XXX 编号")
        return 1

    problems = 0
    for name in ("BOOT_BRIEF", "CURRENT_STATE"):
        text = contents.get(name)
        if not text:
            continue
        pointer = extract_latest_dec_pointer(text)
        if pointer is None:
            print(f"  [权威冲突] {name}: 未找到最新DEC指针，DECISION_LOG最大=DEC-{actual:03d}")
            problems += 1
        elif pointer != actual:
            print(f"  [权威冲突] {name}: 最新DEC指针=DEC-{pointer:03d}，DECISION_LOG最大=DEC-{actual:03d}")
            problems += 1
    return problems


def check_patrol_traces(
    contents: dict[str, str | None],
    *,
    today: "date | None" = None,
    now_hour: int | None = None,
    days: int = PATROL_LOOKBACK_DAYS,
) -> int:
    """外部不变量：每日巡检班是否在 §1c 留痕。

    背景（2026-07-30 加，周监控 2026-07-27 发现1）：项目有一个反复三次的同族缺陷——
    `已派≠已执行`(7/06) → `进程在≠任务在跑`(7/20) → `跑了≠落盘`(7/24-26)，
    三次全部靠 Founder 追问或人工核查发现，无一次由系统自动检出。
    2026-07-27 的修补（把落盘纪律写进巡检自己的提示词）与失效模式同源——
    "agent 不遵守自己的收尾指令"正是该次失败本身——故不构成独立防线。

    本检查是那条缺失的**外部**防线：不问巡检"你写了吗"，直接查权威文件里有没有它的痕迹。
    判定=对每个应跑日，CURRENT_STATE 中是否存在 `YYYY-MM-DD…巡检班` 标记；缺失即告警。
    lastRunAt 存在应用内部状态、不可靠落盘，故改用留痕本身作凭据（缺痕即等价于"没跑或没写"，
    两者都要人看一眼——这正是我们要的告警语义）。
    """
    text = contents.get("CURRENT_STATE")
    if not text:
        return 0

    today = today or date.today()
    now_hour = now_hour if now_hour is not None else datetime.now().hour

    missing: list[str] = []
    for back in range(days):
        d = today - timedelta(days=back)
        if d < PATROL_START:
            continue
        # 当日班次未到执行时刻则不计
        if d == today and now_hour < PATROL_GRACE_HOUR:
            continue
        ds = d.isoformat()
        if not re.search(rf"{re.escape(ds)}[^\n|]{{0,24}}巡检班", text):
            missing.append(ds)

    if not missing:
        return 0

    print(f"  [留痕缺失] 以下应跑日在 CURRENT_STATE 无巡检班痕迹: {', '.join(sorted(missing))}")
    print("             → 含义=该班次未跑 或 跑了未落盘（两者都需人工确认，勿默认已跑）")
    return len(missing)


def check_phase_conflict(contents: dict[str, str | None]) -> int:
    phases = {}
    for name in ("CURRENT_STATE", "TASK_PLAN", "BOOT_BRIEF"):
        text = contents.get(name)
        if text:
            phase = extract_phase(name, text)
            if phase:
                phases[name] = phase

    unique = set(phases.values())
    if len(unique) <= 1:
        return 0

    detail = "；".join(f"{name}={phase}" for name, phase in phases.items())
    print(f"  [权威冲突] 阶段不一致: {detail}")
    return 1


def run_check(root: Path) -> int:
    problems = 0
    print(f"== state_check @ {root} ==\n")
    contents = {}
    for name, rel in AUTH_FILES.items():
        c = read(root, rel)
        contents[name] = c
        if c is None:
            print(f"[缺失] {name}: {rel}")
            problems += 1
    print()

    # 1) 已知坏串
    print("-- 过时坏串扫描 --")
    found_stale = False
    for name, c in contents.items():
        if not c:
            continue
        lines = c.splitlines()
        for line_no, line_text in enumerate(lines, start=1):
            context = "\n".join(lines[max(0, line_no - 3): min(len(lines), line_no + 2)])
            for label, pat in STALE_PATTERNS:
                if not re.search(pat, line_text, re.I):
                    continue
                if line_is_allowed(label, context):
                    continue
                print(f"  [滞后告警] {name} L{line_no}: {label} 命中 /{pat}/")
                problems += 1
                found_stale = True
    if not found_stale:
        print("  无已知坏串 ✓")
    print()

    # 2) 最新 DEC 指针
    print("-- 最新DEC一致性 --")
    before = problems
    problems += check_latest_dec(contents)
    if problems == before:
        print("  BOOT_BRIEF/CURRENT_STATE 最新DEC指针一致 ✓")
    print()

    # 3) 不变量并排（人工/AI 眼检一致性）
    for inv, pat in INVARIANT_PATTERNS.items():
        print(f"-- {inv}（各权威文件首个命中）--")
        for name, c in contents.items():
            if not c:
                continue
            m = re.search(pat, c)
            print(f"  {name:15}: {m.group(0).strip() if m else '（未命中）'}")
        print()

    print("-- 权威冲突检查 --")
    before = problems
    problems += check_phase_conflict(contents)
    if problems == before:
        print("  无机器可判定权威冲突 ✓")
    print()

    # 4) 巡检留痕（外部不变量，不依赖被检者自觉）
    print(f"-- 巡检班留痕（近{PATROL_LOOKBACK_DAYS}天）--")
    before = problems
    problems += check_patrol_traces(contents)
    if problems == before:
        print("  每个应跑日均有巡检班痕迹 ✓")
    print()

    print("== 结论: %s ==" % ("发现 %d 项疑似滞后，请同步" % problems if problems else "无已知滞后 ✓"))
    return 1 if problems else 0


def write_auth_files(root: Path, *, current: str, task_plan: str, boot: str, decision: str) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "CLAUDE.md").write_text("# marker\n", encoding="utf-8")
    (root / "01_MEMORY_CORE").mkdir(parents=True)
    (root / "00_PROJECT_MANAGEMENT").mkdir(parents=True)
    (root / "01_MEMORY_CORE" / "CURRENT_STATE.md").write_text(current, encoding="utf-8")
    (root / "00_PROJECT_MANAGEMENT" / "PROJECT_TASK_PLAN.md").write_text(task_plan, encoding="utf-8")
    (root / "01_MEMORY_CORE" / "BOOT_BRIEF.md").write_text(boot, encoding="utf-8")
    (root / "01_MEMORY_CORE" / "DECISION_LOG.md").write_text(decision, encoding="utf-8")


def _patrol_trace_block(today: "date | None" = None) -> str:
    """给自测样本生成"近7天巡检痕迹"，使 run_check 的留痕检查不误报合成样本。"""
    today = today or date.today()
    return "\n".join(
        f"**{(today - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：自测样本"
        for k in range(PATROL_LOOKBACK_DAYS + 1)
    )


def self_test() -> int:
    traces = _patrol_trace_block()
    with tempfile.TemporaryDirectory() as tmp:
        bad_root = Path(tmp) / "bad"
        clean_root = Path(tmp) / "clean"
        write_auth_files(
            bad_root,
            current=f"Phase 1\n最新DEC=DEC-082\n{traces}\n",
            task_plan="Phase 1\n",
            boot="Phase 1\n最新DEC=DEC-082\n月化30%作为研究验收门槛\n",
            decision="[DEC-081]\n[DEC-082]\n",
        )
        write_auth_files(
            clean_root,
            current=f"Phase 1\n最新DEC=DEC-082\n{traces}\n",
            task_plan="Phase 1\n",
            boot="Phase 1\n最新DEC=DEC-082\n",
            decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
        )
        with contextlib.redirect_stdout(io.StringIO()):
            bad_code = run_check(bad_root)
            clean_code = run_check(clean_root)

    assert bad_code != 0, "含坏串样本必须返回非零"
    assert clean_code == 0, "干净样本必须返回0"

    # 巡检留痕检查自测（2026-07-30）
    t = date(2026, 8, 1)
    full = {"CURRENT_STATE": "\n".join(
        f"**{(t - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：无信号" for k in range(7)
    )}
    assert check_patrol_traces(full, today=t, now_hour=18) == 0, "留痕齐全须返回0"

    gap = {"CURRENT_STATE": "\n".join(
        f"**{(t - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：无信号"
        for k in range(7) if k != 2
    )}
    with contextlib.redirect_stdout(io.StringIO()) as buf:
        n = check_patrol_traces(gap, today=t, now_hour=18)
    assert n == 1, f"缺1天须返回1，实际{n}"
    assert "2026-07-30" in buf.getvalue(), "须点名缺失日期"

    # 当日未到执行时刻不得误报
    today_missing = {"CURRENT_STATE": "\n".join(
        f"**{(t - timedelta(days=k)).isoformat()} 10:01巡检班（完成）**：无信号" for k in range(1, 7)
    )}
    assert check_patrol_traces(today_missing, today=t, now_hour=9) == 0, "当日9点不得计当日班"
    assert check_patrol_traces(today_missing, today=t, now_hour=18) == 1, "当日18点须计当日班"

    # 起算日之前不得回溯误报
    early = {"CURRENT_STATE": ""}
    assert check_patrol_traces(early, today=date(2026, 7, 17), now_hour=18) <= 2, "不得回溯到起算日之前"

    print("self-test passed: bad sample nonzero, clean sample zero, patrol-trace 5 cases ok")
    return 0


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if args and args[0] == "--self-test":
        return self_test()

    if args:
        root = Path(args[0]).expanduser().resolve()
    else:
        root = discover_project_root(Path(__file__).resolve().parent)
    return run_check(root)

if __name__ == "__main__":
    sys.exit(main())
