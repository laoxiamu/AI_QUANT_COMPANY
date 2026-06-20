#!/usr/bin/env python3
"""
Claude PreToolUse Hook: Holdout Protection
把"禁读Holdout"从软规则变成硬门控。

触发条件：任何Read/Edit/Write工具尝试访问~/.aiquant_sealed/路径时拦截。

部署方式：在Claude Code项目设置中添加PreToolUse hook指向本文件。
配置示例（.claude/settings.json）：
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Read|Edit|Write",
        "hooks": [{"type": "command", "command": "python3 .claude/hooks/protect-holdout.py"}]
      }
    ]
  }
}

Hook协议：
- stdin接收JSON格式的tool_call信息
- 输出非空字符串到stderr = 拦截工具调用并显示错误
- 无输出/空输出 = 放行
"""

import json
import sys
import os

def main():
    try:
        # 读取Claude传来的工具调用信息
        tool_input = json.load(sys.stdin)
    except (json.JSONDecodeError, EOFError):
        # 无法解析则放行（不拦截）
        sys.exit(0)

    tool_name = tool_input.get("tool_name", "")
    tool_input_params = tool_input.get("tool_input", {})

    # 检查文件路径参数
    path_to_check = (
        tool_input_params.get("file_path") or
        tool_input_params.get("path") or
        ""
    )

    # Holdout路径模式
    holdout_patterns = [
        os.path.expanduser("~/.aiquant_sealed"),
        ".aiquant_sealed",
        "aiquant_sealed/carry",
        "aiquant_sealed/holdout",
    ]

    if path_to_check:
        for pattern in holdout_patterns:
            if pattern in path_to_check:
                # 拦截！输出错误信息到stderr
                error_msg = (
                    f"🔴 HOLDOUT PROTECTION TRIGGERED\n"
                    f"工具 '{tool_name}' 尝试访问 Holdout 数据：{path_to_check}\n"
                    f"Holdout 绝对禁读——这是硬门控，任何理由都不能绕过。\n"
                    f"如果你认为需要读取 Holdout，停止，提交给 Founder 决策（D级）。\n"
                    f"来源：CLAUDE.md §关键行为规则 + RESEARCH_PROTOCOL_v1.3 Holdout 条款"
                )
                print(error_msg, file=sys.stderr)
                sys.exit(1)

    # 放行
    sys.exit(0)

if __name__ == "__main__":
    main()
