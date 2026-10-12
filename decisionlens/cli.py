"""DecisionLens 命令行入口。

用法：
  python -m decisionlens.cli --sales examples/sales.csv --inventory examples/inventory.csv \
      --feedback examples/feedback.csv --question "哪个 SKU 最该补货？为什么？" [--html out.html]

数据源用 --<角色> <路径> 传入（角色名会出现在连接键匹配与证据引用里）。
"""

from __future__ import annotations

import argparse
import sys

from .agent import DecisionLensAgent


def main(argv=None) -> int:
    p = argparse.ArgumentParser(prog="decisionlens",
        description="溯源决策智能体：跨多数据源提问，给出带证据引用的结论与下一步行动。")
    p.add_argument("--question", "-q", required=True, help="要回答的问题")
    p.add_argument("--html", metavar="OUT", help="生成 HTML 报告")
    # 动态数据源：--sales a.csv --inventory b.csv ...
    args, extra = p.parse_known_args(argv)

    sources = {}
    i = 0
    while i < len(extra) - 1:
        if extra[i].startswith("--"):
            sources[extra[i][2:]] = extra[i + 1]
            i += 2
        else:
            i += 1
    if not sources:
        print("[错误] 请至少提供一个数据源，如 --sales examples/sales.csv --inventory examples/inventory.csv")
        return 2

    agent = DecisionLensAgent()
    try:
        agent.ingest(sources)
    except OSError as e:
        print(f"[错误] 读取数据源失败：{e}")
        return 2

    d = agent.run(args.question)

    print("=" * 68)
    print(f"DecisionLens · 问题：{d.question}")
    print("=" * 68)
    print("\n[智能体轨迹]")
    for s in d.trace:
        print(f"  · {s.phase:<9} {s.detail}")
    print(f"\n[结论]\n  {d.conclusion}")
    print(f"\n[行动]\n  {d.action}")
    print(f"\n[证据引用]（共 {len(d.evidence)} 条）")
    for e in d.evidence[:20]:
        fields = "，".join(f"{k}={v}" for k, v in e.fields.items())
        print(f"  - {e.source} 第{e.row}行 [{fields}] → {e.claim}")

    if args.html:
        from .report import render_html
        with open(args.html, "w", encoding="utf-8") as f:
            f.write(render_html(d))
        print(f"\nHTML 报告已生成：{args.html}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
