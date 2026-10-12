# DecisionLens — An Offline Multi-Source Evidence-Reasoning Agent

DecisionLens is an **offline, multi-source evidence-reasoning agent**. Give it several data sources (CSV files) and a question, and it will: join across sources → retrieve evidence → reason (trends, rankings, stockout risk) → deliver an **evidence-cited conclusion** plus a **concrete next action**.

The key differentiator: **every claim is annotated with the exact file and rows it is based on** (explainable and auditable), instead of a black-box answer. Pure Python standard library — **zero dependencies, 100% offline**. Your business data never leaves the machine.

> Built for real small-business operators: turn scattered sales, inventory, and feedback sheets into an agent that can answer "why" and "what next".

## Built for Open Agent Hackathon 2026 — Track 02: "The Agent That Can Explain Why"

- **Impact**: answers questions that span multiple data sources with actionable, quantified recommendations.
- **Technical**: deterministic, auditable reasoning pipeline; `eval.py` runs 8 reproducible assertions.
- **Innovation**: every conclusion carries row-level citations (`file → row → fields → claim`), making agent output reviewable by a human in seconds.
- **Demo**: one CLI command produces the full agent trace, conclusion, action, and an HTML report.

## Quick Start

No `pip install` needed. Python 3.8+:

```bash
python -m decisionlens.cli \
  --sales examples/sales.csv \
  --inventory examples/inventory.csv \
  --feedback examples/feedback.csv \
  --question "Which SKU should I restock first, and why?" \
  --html report.html
```

## Real Demo Output (bundled example data)

```
[AGENT TRACE]
  - PERCEIVE loaded 3 sources: sales(9 rows), inventory(3 rows), feedback(9 rows)
  - INDEX    found cross-source join keys: ['sku']
  - RETRIEVE pulled sales velocity, stock on hand, and user feedback per SKU
  - REASON   computed weekly velocity and days-of-cover; flags stockout risk when days-of-cover < lead time
  - EXPLAIN  assembled 3 evidence types for SKU-C
  - ACT      produced a quantified restock recommendation

[CONCLUSION]
  Restock SKU-C immediately: ~100 units/week sold, only 90 on hand (~6.3 days of cover)
  vs a 14-day lead time (cover < lead time = stockout guaranteed); user feedback confirms
  ("out of stock again, please restock").

[ACTION]
  Order >= 300 units of SKU-C now (covers the 14-day lead time + one week of safety stock)
  and raise its reorder point.

[EVIDENCE CITATIONS] (18 total)
  - sales row 8 [week=2026-W38, units=140] -> SKU-C recent weekly sales ~140 units
  - inventory row 3 [on_hand=90, lead_time_days=14, reorder_point=120] -> SKU-C: 90 on hand, 14-day lead time, reorder point 120
  - feedback row 9 [rating=4.8, note=out of stock again, please restock] -> SKU-C user feedback: out of stock again (rating 4.8)
  ...
```

## The Agent Loop

| Stage | What it does |
|---|---|
| PERCEIVE | Loads each CSV, auto-infers numeric columns |
| INDEX | Discovers cross-source join keys (e.g. `sku` / `week` / `channel`) |
| RETRIEVE | Fetches the evidence rows relevant to the question |
| REASON | Runs analysis (weekly velocity, days-of-cover, rankings, correlation) |
| EXPLAIN | Generates the conclusion, attaching each judgment to a specific source + row |
| ACT | Emits an executable next step with quantified backing |

## Built-in Skills (routed by question keywords)

- **Stockout / restock analysis**: joins sales + inventory (+ feedback), computes weekly velocity and days-of-cover, flags SKUs that will stock out, and recommends restock quantities.
- **Channel comparison**: ranks channels by revenue, points to where to invest.
- **Trend attribution**: compares first vs. last periods, gives a growth/decline verdict and a response.
- **Overview**: summarizes the sources and suggests questions to ask.

## Use as a Library

```python
from decisionlens import DecisionLensAgent

agent = DecisionLensAgent().ingest({
    "sales": "examples/sales.csv",
    "inventory": "examples/inventory.csv",
    "feedback": "examples/feedback.csv",
})
d = agent.run("Which SKU should I restock first, and why?")
print(d.conclusion)
print(d.action)
for e in d.evidence:
    print(e.source, e.row, e.claim)
```

## Data Format

Any CSV. Columns are recognized by convention: sales `units/qty/quantity`, revenue `revenue/amount`, inventory `on_hand/lead_time_days/reorder_point`, join keys like `sku/week/channel`. Numeric columns are inferred automatically.

## Design Trade-offs

- **Deterministic reasoning, explainability first**: no black-box model — every step is recomputable and traceable to a source row, because operational decisions must be able to say "why".
- **Offline first**: business data (sales, costs) is the most sensitive data there is; everything runs locally, nothing is uploaded.
- **Extensible**: skills are independent methods routed by question keywords; adding a skill = adding one `_skill_*` method.

## Use Cases

Weekly business Q&A for small shop owners, data attribution for agency operators, and a minimal teaching example of "explainable AI + multi-source retrieval".

## Disclaimer

DecisionLens conclusions are based on the provided data and are decision support only. Please review important business decisions manually.

## License

MIT · [github.com/Zhiyilang/decisionlens](https://github.com/Zhiyilang/decisionlens)

中文说明见 [README.zh.md](README.zh.md)。
