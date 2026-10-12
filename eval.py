"""DecisionLens 评测脚本 —— 对示例场景做断言，证明结论可复现、可回归。

运行：python eval.py
用途：黑客松评分项 "shipping evals" —— 用可执行断言固定智能体的期望行为，
     改动推理逻辑后若结论漂移，这里会立刻失败。
"""

from __future__ import annotations

from decisionlens import DecisionLensAgent


def build_agent() -> DecisionLensAgent:
    return DecisionLensAgent().ingest({
        "sales": "examples/sales.csv",
        "inventory": "examples/inventory.csv",
        "feedback": "examples/feedback.csv",
    })


def run() -> int:
    d = build_agent().run("哪个 SKU 最该补货？为什么？")
    checks = []

    def check(name, cond):
        checks.append((name, bool(cond)))

    ranked = d.metrics.get("ranked", [])
    check("结论指向 SKU-C（最该补货）", "SKU-C" in d.conclusion)
    check("SKU-C 排在第一", ranked and ranked[0][0] == "SKU-C")
    check("SKU-C 覆盖天数≈6.3 天", ranked and abs(ranked[0][1] - 6.3) < 0.2)
    check("SKU-C 标记为断货风险", ranked and ranked[0][2] is True)
    check("行动给出补货量建议", "下单补货" in d.action and "300" in d.action)
    check("证据引用来自 3 个数据源",
          {e.source for e in d.evidence} >= {"sales", "inventory", "feedback"})
    check("每条证据都带行号", all(e.row >= 1 for e in d.evidence))
    check("轨迹包含 感知→行动 全阶段",
          [s.phase for s in d.trace] == ["PERCEIVE", "INDEX", "RETRIEVE", "REASON", "EXPLAIN", "ACT"])

    passed = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(f"  [{'PASS' if ok else 'FAIL'}] {name}")
    print(f"\n{passed}/{len(checks)} 通过")
    return 0 if passed == len(checks) else 1


if __name__ == "__main__":
    raise SystemExit(run())
