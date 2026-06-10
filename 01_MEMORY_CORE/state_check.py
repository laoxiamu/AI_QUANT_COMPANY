#!/usr/bin/env python3
"""state_check.py —— Memory Core 权威状态一致性自检（半自动）

用途：每次状态同步后跑一遍，抓"权威文件状态滞后/互相矛盾"这个反复出现的坑。
它不替代人判断——而是把关键不变量(阶段/失败计数)从各权威文件里抽出来并排显示，
并对已知的"过时坏串"报警。退出码非0=发现疑似滞后。

用法：python3 01_MEMORY_CORE/state_check.py [项目根路径]
默认项目根 = /Users/yaomingyu/Documents/AI_QUANT_COMPANY
"""
import os, re, sys

ROOT = sys.argv[1] if len(sys.argv) > 1 else "/Users/yaomingyu/Documents/AI_QUANT_COMPANY"

AUTH_FILES = {
    "CURRENT_STATE":   "01_MEMORY_CORE/CURRENT_STATE.md",
    "OPERATING_STATE": "00_PROJECT_MANAGEMENT/PROJECT_OPERATING_STATE.md",
    "MASTER_PLAN":     "00_PROJECT_MANAGEMENT/PROJECT_MASTER_PLAN_v2.md",
    "BOOT_BRIEF":      "01_MEMORY_CORE/BOOT_BRIEF.md",
}

# 已知"过时坏串"——出现即报警（随项目演进维护）
STALE_PATTERNS = [
    r"历史实验失败 \*\*8次\*\*",
    r"独立Alpha假设 \*\*4/8\*\*",
    r"Phase 0B — First Validated",
    r"阶段 0A .*进行中",
    r"尚未执行任何实际 Codex",
]

# 关注的不变量（抽出来并排看）
INVARIANT_PATTERNS = {
    "阶段":   r"(Phase\s*[01][AB]?|阶段\s*[01][AB]?)",
    "失败计数": r"(历史(实验)?失败\s*\*?\*?\s*\d+|独立\s*Alpha[^\n]{0,20}\d/8)",
}

def read(path):
    full = os.path.join(ROOT, path)
    if not os.path.exists(full):
        return None
    with open(full, encoding="utf-8") as f:
        return f.read()

def main():
    problems = 0
    print(f"== state_check @ {ROOT} ==\n")
    contents = {}
    for name, rel in AUTH_FILES.items():
        c = read(rel)
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
        for pat in STALE_PATTERNS:
            for m in re.finditer(pat, c):
                line = c[:m.start()].count("\n") + 1
                print(f"  [滞后告警] {name} L{line}: 命中 /{pat}/")
                problems += 1
                found_stale = True
    if not found_stale:
        print("  无已知坏串 ✓")
    print()

    # 2) 不变量并排（人工/AI 眼检一致性）
    for inv, pat in INVARIANT_PATTERNS.items():
        print(f"-- {inv}（各权威文件首个命中）--")
        for name, c in contents.items():
            if not c:
                continue
            m = re.search(pat, c)
            print(f"  {name:15}: {m.group(0).strip() if m else '（未命中）'}")
        print()

    print("== 结论: %s ==" % ("发现 %d 项疑似滞后，请同步" % problems if problems else "无已知滞后 ✓"))
    return 1 if problems else 0

if __name__ == "__main__":
    sys.exit(main())
