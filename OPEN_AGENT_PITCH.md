# DecisionLens — Open Agent Hackathon 2026 提交备忘

> ## 🔴 状态：降级为备胎（2026-10-17 官方页资格复核）
>
> **官方页逐字原文（2026-10-17 抓取）**：
> > **Bonus track — Wildcard [Tinkerer]: Bring Your Own Project** — "Bring an existing project, prototype or concept and extend it using sponsor technology such as Meterless and Zetaris. Entries are judged on the same criteria as the other tracks, **must integrate Zetaris and Meterless**, and are **scored on the new work rather than prior development**."
>
> 主页面另有 "**Pick one track. Build for it.**" 与 "Over a six-day build sprint"（建造窗 10-22 00:00 UTC 开启）。
>
> **推论**：官方为「既有项目」专设了 Wildcard 赛道（且必须集成 Zetaris+Meterless、只按新工作计分）→ 主赛道（01/02/03）隐含要求建窗内新建。DecisionLens 的公开仓建于建窗之前（2026-10 上旬即公开），**进主赛道有资格风险**；Wildcard 无 Zetaris/Meterless Key 是死路。
>
> **决策变更**：Open Agent 主投 **QuorumPilot → Track 02**（公开仓按计划 10-26 建窗内创建，资格安全；带证据引用的裁决同样是 "explain why" 字面命中）。详见 `quorumpilot/SUBMISSION_CHECKLIST.md`。
> **本文件保留理由**：① 若注册后平台明确允许一队多项目，DecisionLens 可作第二枪补 Track 01「Solving Fragmented Intelligence」（多源碎片数据）② 若拿到 Zetaris/Meterless Key，可转 Wildcard ③ 评分映射/演示命令/失败模式记录是高质量可复用资产。
>
> 主办 GenAI.Works · **报名截止 2026-10-22 23:59 UTC（北京 10-23 07:59，硬截止）** · 建造窗 10-22 00:00 UTC ~ 10-27 · **提交截止 10-27 23:45 UTC（北京 10-28 07:45，硬截止）** · 结果公布 11-06 16:00 UTC。
> 官方报名页：`hackathon.genai.works/event/open-agent-hackathon-2026`（2026-10-17 官方页逐字核实，此前稿"10-13 报名截止/10-20 提交"为过时口径，已废弃）

## 项目
- **名称**：DecisionLens — 溯源决策智能体
- **仓库**：https://github.com/Zhiyilang/decisionlens
- **一句话**：离线的多源证据推理智能体——跨多个 CSV 数据源提问，给出**带逐条证据引用**的结论和可执行的下一步行动；纯标准库、零依赖、100% 离线。

## 建议赛道
- **Track 02「The Agent That Can Explain Why」**（首选）：跨多数据源调查、连接发现、给出有证据支撑的答案——完全契合 DecisionLens 的"每个结论都引用到源文件+行号"。
- **备选 Track 03「Reasoning Architecture」**：把数据+知识+推理变成可靠决策与行动的架构。

## 评分映射（官方六项共 100 分，无 bonus 分——此前稿"开源/评测/失败模式各 +10"系臆造，已删）
| 项 | 分 | DecisionLens 如何拿分 |
|---|---|---|
| Impact 影响力 | 30 | 让小企业运营者把散在销量/库存/反馈表里的数据变成"该补什么货、下一步做什么"的决策 |
| Technical 技术 | 20 | 多源类型化摄取、跨源连接键自动发现、证据溯源推理、技能路由、可复现 eval（8/8） |
| Innovation 创新 | 15 | **逐 claim 证据引用**（哪条结论依据哪个文件哪几行），可解释而非黑箱 |
| Demo 演示 | 15 | 离线 CLI + 自包含 HTML 报告，一条命令复现（见 README） |
| Product & UX | 10 | 清晰 CLI、轨迹可视化、HTML 报告 |
| Sponsor tech | 10 | 主赛道可选；若冲实物奖需集成 Nemotron API（见下） |

**奖金结构（官方）**：Track 02 池 $3,700（1st $1,600 / 2nd $1,200 / 3rd $900）；Track 03 池 $3,600（1st $1,500）。
**两个独立实物奖（可叠加）**：① Best use of NVIDIA Nemotron = **NVIDIA DGX Spark AI Supercomputer（值 $4,699）**；② Best use of Cursor-built product = SpaceX Cursor API credits（值 $2,301）。
**打法**：主投 Track 02（DecisionLens 逐条证据引用 = "explain why" 字面命中）；Nemotron 实物奖需要把某个环节改成调用 Nemotron API（如证据摘要生成），零依赖架构加一个可选 API 后端即可，建造窗内 1 天可完成——**值得冲**（DGX Spark 价值远超 Track 现金奖）。

## 提交时需要准备
1. 仓库链接 + README（已备，含真实 demo 输出）。
2. 一段 ≤5 分钟演示：跑 `python -m decisionlens.cli ... --question "哪个 SKU 最该补货？为什么？" --html report.html`，展示轨迹/结论/行动/证据表。
3. 简述架构（PERCEIVE→INDEX→RETRIEVE→REASON→EXPLAIN→ACT）与可解释性设计。

## 时间线策略（按官方口径，北京时间为准）
- **10-23 07:59 前**：用户注册（必须本人；官方页倒计时确认 10-22 23:59 UTC 硬截止）。
- **10-22 00:00 UTC ~ 10-27**：建造窗。仓已就绪，窗内增量 = ① 录 ≤5min demo 视频 ② 按六项评分表逐项补强 README ③（可选冲刺）Nemotron API 后端冲 DGX Spark 实物奖 ④ 提交前最后跑一次 eval 确认 8/8。
- **10-28 07:45 前**：Devpost/平台提交（硬截止，提前 1 天交，不卡点）。
- **11-06 16:00 UTC**：结果公布。
- ⚠️ Wildcard 赛道强制集成 Zetaris + Meterless 且只按新工作计分——DecisionLens 现成仓直接打 Wildcard 会吃"prior development 不计分"的亏，故主投 Track 02，不碰 Wildcard。

## 已知限制 / 失败模式（诚实记录，拿 bonus 也防评委挑刺）
- 确定性规则推理，非神经网络；问题按关键词路由到技能，未覆盖的问法走"概览"兜底。
- 列名按约定识别（units/revenue/on_hand 等），非任意自由文本。
- 连接键依赖列名相同（如都叫 sku）；异名同义列暂不自动对齐。
- 结论质量取决于输入数据完整性；重大决策需人工复核（README 已声明）。

## 待用户（真人）动作
- **10-23 07:59 前**在上方官方页注册（必须本人，AI 无法代注册）——注册本身仍要做（资格锁定，且注册后才能在平台确认"一队能否交多个项目"）。
- 注册后告诉我，我将：① 查平台是否允许多项目提交——若允许，DecisionLens 作第二枪补 Track 01；若不允许，本仓正式退出本赛，QuorumPilot 单投 ② 若你搞到了 Zetaris/Meterless Key（不太可能），评估转 Wildcard。
- ⚠️ **不要在未确认平台多项目规则前，把 DecisionLens 设为 Open Agent 主投**——资格风险见顶部横幅。
