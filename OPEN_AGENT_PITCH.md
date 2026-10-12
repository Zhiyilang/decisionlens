# DecisionLens — Open Agent Hackathon 2026 提交备忘

> 主办 GenAI.Works · 报名截止 **北京时间 2026-10-13 早 8:00** · 建造窗口 10-15~10-20 · 提交截止 10-20 23:45 UTC。
> 官方报名页：`hackathon.genai.works/event/open-agent-hackathon-2026`

## 项目
- **名称**：DecisionLens — 溯源决策智能体
- **仓库**：https://github.com/Zhiyilang/decisionlens
- **一句话**：离线的多源证据推理智能体——跨多个 CSV 数据源提问，给出**带逐条证据引用**的结论和可执行的下一步行动；纯标准库、零依赖、100% 离线。

## 建议赛道
- **Track 02「The Agent That Can Explain Why」**（首选）：跨多数据源调查、连接发现、给出有证据支撑的答案——完全契合 DecisionLens 的"每个结论都引用到源文件+行号"。
- **备选 Track 03「Reasoning Architecture」**：把数据+知识+推理变成可靠决策与行动的架构。

## 评分映射（满分100 + 最多30奖励）
| 项 | 分 | DecisionLens 如何拿分 |
|---|---|---|
| Impact 影响力 | 30 | 让小企业运营者把散在销量/库存/反馈表里的数据变成"该补什么货、下一步做什么"的决策 |
| Technical 技术 | 20 | 多源类型化摄取、跨源连接键自动发现、证据溯源推理、技能路由、可复现 eval |
| Innovation 创新 | 15 | **逐 claim 证据引用**（哪条结论依据哪个文件哪几行），可解释而非黑箱 |
| Demo 演示 | 15 | 离线 CLI + 自包含 HTML 报告，一条命令复现（见 README） |
| Product & UX | 10 | 清晰 CLI、轨迹可视化、HTML 报告 |
| Sponsor tech | 10 | 主赛道可不依赖；若走 Tinkerer 需集成 Zetaris/Meterless（可选，暂不做） |
| **Bonus 开源** | +10 | MIT 已开源 |
| **Bonus 评测** | +10 | `eval.py` 8 条断言固定期望行为（`python eval.py` → 8/8） |
| **Bonus 记录失败模式** | +10 | 见下方"已知限制/失败模式" |

## 提交时需要准备
1. 仓库链接 + README（已备，含真实 demo 输出）。
2. 一段 ≤5 分钟演示：跑 `python -m decisionlens.cli ... --question "哪个 SKU 最该补货？为什么？" --html report.html`，展示轨迹/结论/行动/证据表。
3. 简述架构（PERCEIVE→INDEX→RETRIEVE→REASON→EXPLAIN→ACT）与可解释性设计。

## 已知限制 / 失败模式（诚实记录，拿 bonus 也防评委挑刺）
- 确定性规则推理，非神经网络；问题按关键词路由到技能，未覆盖的问法走"概览"兜底。
- 列名按约定识别（units/revenue/on_hand 等），非任意自由文本。
- 连接键依赖列名相同（如都叫 sku）；异名同义列暂不自动对齐。
- 结论质量取决于输入数据完整性；重大决策需人工复核（README 已声明）。

## 待用户（真人）动作
- **10-13 早 8:00 前**在上方官方页注册（必须本人，AI 无法代注册）。
- 注册后告诉我，我按需补充：录演示脚本、按赛道微调 README、可选集成赞助商技术冲 Sponsor 分。
