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
from pathlib import Path


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


def self_test() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        bad_root = Path(tmp) / "bad"
        clean_root = Path(tmp) / "clean"
        write_auth_files(
            bad_root,
            current="Phase 1\n最新DEC=DEC-082\n",
            task_plan="Phase 1\n",
            boot="Phase 1\n最新DEC=DEC-082\n月化30%作为研究验收门槛\n",
            decision="[DEC-081]\n[DEC-082]\n",
        )
        write_auth_files(
            clean_root,
            current="Phase 1\n最新DEC=DEC-082\n",
            task_plan="Phase 1\n",
            boot="Phase 1\n最新DEC=DEC-082\n",
            decision="[DEC-081]\n[DEC-082]\nPhase 1\n",
        )
        with contextlib.redirect_stdout(io.StringIO()):
            bad_code = run_check(bad_root)
            clean_code = run_check(clean_root)

    assert bad_code != 0, "含坏串样本必须返回非零"
    assert clean_code == 0, "干净样本必须返回0"
    print("self-test passed: bad sample nonzero, clean sample zero")
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
