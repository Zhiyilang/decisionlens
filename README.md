# DecisionLens 🔎 — 溯源决策智能体

一个**离线的多源证据推理智能体**。给它多个数据源（CSV）和一个问题，它会：
跨源连接 → 检索证据 → 推理（趋势/排名/断货风险）→ 给出**带证据引用**的结论和**可执行的下一步行动**。

关键差异：**每个结论都标注它依据哪个文件的哪几行**（可解释、可复核），而不是甩一个黑箱答案。纯标准库、**零依赖、100% 离线**——商业数据不出本机。

> 面向真实小企业运营者：把散在销量表、库存表、反馈表里的数据，变成一个能回答"为什么"和"下一步做什么"的智能体。

## 快速开始

无需 `pip install`，Python 3.8+：

```bash
python -m decisionlens.cli \
  --sales examples/sales.csv \
  --inventory examples/inventory.csv \
  --feedback examples/feedback.csv \
  --question "哪个 SKU 最该补货？为什么？" \
  --html report.html
```

## 真实 demo 输出（示例数据）

```
[智能体轨迹]
  · PERCEIVE 加载 3 个数据源：sales(9行)、inventory(3行)、feedback(9行)
  · INDEX    发现跨源连接键：['sku']
  · RETRIEVE 从 sales 取销量、inventory 取库存、feedback 取评价
  · REASON   计算各 SKU 周均销量、库存可覆盖天数，判定 覆盖天数<交货期 或 库存<补货点 即为断货风险
  · EXPLAIN  为 SKU-C 汇总销量/库存/反馈三类证据
  · ACT      给出补货数量建议

[结论]
  最该立即补货的是 SKU-C：周销约 100 件，现有库存 90 仅够约 6.3 天，
  而交货期要 14 天（覆盖天数<交货期=会断货）；用户反馈也印证（又断货了，赶紧补）。

[行动]
  立即为 SKU-C 下单补货，建议订 ≥ 300 件（覆盖 14 天交货期 + 一周安全库存），并上调其补货点。

[证据引用]（共 18 条）
  - sales 第8行 [week=2026-W38, units=140] → SKU-C 近期周销量约 140 件
  - inventory 第3行 [on_hand=90, lead_time_days=14, reorder_point=120] → SKU-C 库存 90、交货期 14 天、补货点 120
  - feedback 第9行 [rating=4.8, note=又断货了，赶紧补] → SKU-C 用户反馈：又断货了，赶紧补（评分 4.8）
  ...
```

## 智能体循环

| 阶段 | 做什么 |
|---|---|
| PERCEIVE 感知 | 加载各 CSV，自动推断数值列 |
| INDEX 索引 | 发现跨源连接键（如 `sku`/`week`/`channel`） |
| RETRIEVE 检索 | 按问题取回相关证据行 |
| REASON 推理 | 运行分析（周均速度、覆盖天数、排名、相关性） |
| EXPLAIN 解释 | 生成结论，每条判断挂到具体源+行 |
| ACT 行动 | 给出可执行的下一步与量化依据 |

## 内置技能（按问题关键词路由）

- **断货/补货分析**：跨 sales+inventory(+feedback)，算周均销量、库存可覆盖天数，标出会断货的 SKU 并给补货量建议。
- **渠道对比**：按营收排名各渠道，指出最该投入的方向。
- **趋势归因**：对比指标首尾变化，给出增长/下滑判断与应对。
- **概览**：汇总数据源，提示可问的问题。

## 作为库调用

```python
from decisionlens import DecisionLensAgent

agent = DecisionLensAgent().ingest({
    "sales": "examples/sales.csv",
    "inventory": "examples/inventory.csv",
    "feedback": "examples/feedback.csv",
})
d = agent.run("哪个 SKU 最该补货？为什么？")
print(d.conclusion)
print(d.action)
for e in d.evidence:
    print(e.source, e.row, e.claim)
```

## 数据格式

任意 CSV。列名按约定识别：销量 `units/qty/quantity`、营收 `revenue/amount`、
库存 `on_hand/lead_time_days/reorder_point`、连接键如 `sku/week/channel`。
数值列自动推断。

## 设计取舍

- **确定性推理、可解释优先**：不用黑箱模型，每一步都可复算、可追溯到源行——运营决策要能说清"为什么"。
- **离线优先**：商业数据（销量/成本）最敏感，全程本地，不联网不上传。
- **可扩展**：技能是独立方法，按问题关键词路由；加新技能=加一个 `_skill` 方法。

## 适用场景

小店主的每周经营问答、代运营的数据归因、教学里的"可解释 AI + 多源检索"最小样例。

## 免责声明

DecisionLens 的结论基于所提供数据，仅供辅助决策，重大经营决策请人工复核。

## License

MIT · [github.com/Zhiyilang/decisionlens](https://github.com/Zhiyilang/decisionlens)
