"""DecisionLens — 溯源决策智能体。

一个离线的多源证据推理智能体： ingest 多个数据源 → 建立跨源索引 →
按问题检索证据 → 推理（趋势/排名/相关性/断货风险）→ 给出**带证据引用**的结论
与可执行的下一步行动。每个结论都标注它依据哪个文件的哪几行，可解释、可复核。

智能体循环（Trace 会记录每一步）：
  PERCEIVE  感知：加载并类型化各数据源
  INDEX     索引：发现跨源连接键（如 sku/week/channel）
  RETRIEVE  检索：按问题取回相关证据
  REASON    推理：在证据上运行分析
  EXPLAIN   解释：生成带引用的结论
  ACT       行动：给出下一步建议
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .table import Table, load_csv, find_join_keys


@dataclass
class Step:
    phase: str
    detail: str


@dataclass
class Evidence:
    source: str
    row: int          # 1-based 数据行号（不含表头）
    fields: dict
    claim: str


@dataclass
class Decision:
    question: str
    trace: list = field(default_factory=list)
    evidence: list = field(default_factory=list)
    conclusion: str = ""
    action: str = ""
    metrics: dict = field(default_factory=dict)


class DecisionLensAgent:
    def __init__(self):
        self.tables: list[Table] = []
        self.join_keys: list[str] = []

    # ---- PERCEIVE + INDEX -------------------------------------------------
    def ingest(self, sources: dict[str, str]):
        """sources: {显示名: csv路径}"""
        for name, path in sources.items():
            self.tables.append(load_csv(path, name=name))
        self.join_keys = find_join_keys(self.tables)
        return self

    def _table(self, keyword: str) -> Table | None:
        for t in self.tables:
            if keyword in t.name.lower():
                return t
        return None

    # ---- 主入口 -----------------------------------------------------------
    def run(self, question: str) -> Decision:
        d = Decision(question=question)
        d.trace.append(Step("PERCEIVE", f"加载 {len(self.tables)} 个数据源："
                            + "、".join(f"{t.name}({len(t)}行)" for t in self.tables)))
        d.trace.append(Step("INDEX", f"发现跨源连接键：{self.join_keys or '无'}"))

        q = question.lower()
        if any(k in q for k in ("补货", "断货", "库存", "reorder", "stock", "stockout")):
            self._restock(d)
        elif any(k in q for k in ("渠道", "channel", "获客")):
            self._channel(d)
        elif any(k in question for k in ("为什么", "为啥", "why", "原因", "暴涨", "下降", "涨", "跌")):
            self._trend(d)
        else:
            self._summary(d)
        return d

    # ---- 技能：断货风险（跨 sales+inventory+feedback） ---------------------
    def _restock(self, d: Decision):
        sales = self._table("sales")
        inv = self._table("inventory") or self._table("inv")
        fb = self._table("feedback") or self._table("review")
        if not sales or not inv:
            d.conclusion = "断货分析需要 sales 与 inventory 两个数据源。"
            d.action = "请提供包含销量与库存的数据源。"
            return

        sku_col = "sku"
        units_col = next((c for c in sales.numeric_cols if c in ("units", "qty", "quantity")), None)
        week_col = next((c for c in sales.columns if c.lower() in ("week", "date", "week_start")), None)
        if units_col is None:
            d.conclusion = "sales 中未找到销量数值列（units/qty/quantity）。"
            return

        d.trace.append(Step("RETRIEVE", f"从 {sales.name} 取销量、{inv.name} 取库存"
                            + (f"、{fb.name} 取评价" if fb else "")))

        # 最近两周销量 → 周均速度
        weeks = sorted({r[week_col] for r in sales.rows}) if week_col else []
        recent = weeks[-2:] if len(weeks) >= 2 else weeks
        vel: dict[str, list] = {}
        for r in sales.rows:
            if week_col and r[week_col] not in recent:
                continue
            vel.setdefault(r[sku_col], []).append((sales.rows.index(r) + 1, float(r[units_col])))
        velocity = {s: sum(u for _, u in v) / max(1, len(recent)) for s, v in vel.items()}
        for s, v in vel.items():
            for ridx, u in v:
                d.evidence.append(Evidence(sales.name, ridx,
                    {"week": sales.rows[ridx-1].get(week_col, ""), "units": u},
                    f"{s} 近期周销量约 {u:g} 件"))

        # 库存 → 可覆盖天数、交货期
        onhand = {r[sku_col]: r for r in inv.rows}
        rows = []
        for s, v in velocity.items():
            if s not in onhand:
                continue
            ir = onhand[s]
            oh = float(ir.get("on_hand", 0) or 0)
            lead = float(ir.get("lead_time_days", 0) or 0)
            rop = float(ir.get("reorder_point", 0) or 0)
            cover = (oh / v * 7) if v > 0 else 999
            rows.append({"sku": s, "velocity": v, "on_hand": oh, "lead": lead,
                         "reorder_point": rop, "cover_days": cover,
                         "short": cover < lead or oh < rop})
            d.evidence.append(Evidence(inv.name, inv.rows.index(ir) + 1,
                {"on_hand": oh, "lead_time_days": lead, "reorder_point": rop},
                f"{s} 库存 {oh:g}、交货期 {lead:g} 天、补货点 {rop:g}"))

        # 反馈（可选，佐证）
        fb_notes = {}
        if fb:
            for r in fb.rows:
                if sku_col in r:
                    fb_notes.setdefault(r[sku_col], []).append(r)
            for s, rs in fb_notes.items():
                for r in rs:
                    d.evidence.append(Evidence(fb.name, fb.rows.index(r) + 1,
                        {"rating": r.get("rating", ""), "note": r.get("note", "")},
                        f"{s} 用户反馈：{r.get('note', '')}（评分 {r.get('rating','')}）"))

        d.trace.append(Step("REASON", "计算各 SKU 周均销量、库存可覆盖天数，"
                            "判定 覆盖天数<交货期 或 库存<补货点 即为断货风险"))
        rows.sort(key=lambda x: (not x["short"], x["cover_days"]))
        top = rows[0] if rows else None
        d.metrics = {"ranked": [(r["sku"], round(r["cover_days"], 1), r["short"]) for r in rows]}

        if not top:
            d.conclusion = "未找到可评估的 SKU。"
            return
        if not top["short"]:
            d.conclusion = (f"各 SKU 库存充足，暂无断货风险。覆盖天数最短的是 "
                            f"{top['sku']}（约 {top['cover_days']:.1f} 天，交货期 {top['lead']:g} 天）。")
            d.action = "维持现有补货节奏即可。"
            return

        note = ""
        if fb and top["sku"] in fb_notes and fb_notes[top["sku"]]:
            note = f"；用户反馈也印证（{fb_notes[top['sku']][-1].get('note','')}）"
        d.trace.append(Step("EXPLAIN", f"为 {top['sku']} 汇总销量/库存/反馈三类证据"))
        d.conclusion = (
            f"最该立即补货的是 **{top['sku']}**：周销约 {top['velocity']:g} 件，"
            f"现有库存 {top['on_hand']:g} 仅够约 {top['cover_days']:.1f} 天，"
            f"而交货期要 {top['lead']:g} 天（覆盖天数<交货期=会断货）{note}。")
        order_qty = round(top["velocity"] * (top["lead"] / 7 + 1))
        d.trace.append(Step("ACT", "给出补货数量建议"))
        d.action = (f"立即为 {top['sku']} 下单补货，建议订 ≥ {order_qty} 件"
                    f"（覆盖 {top['lead']:g} 天交货期 + 一周安全库存），并上调其补货点。")

    # ---- 技能：渠道对比 ---------------------------------------------------
    def _channel(self, d: Decision):
        sales = self._table("sales")
        if not sales:
            d.conclusion = "渠道分析需要 sales 数据源。"
            return
        ch = next((c for c in sales.columns if c.lower() in ("channel", "source", "渠道")), None)
        rev = next((c for c in sales.numeric_cols if c in ("revenue", "amount", "gmv")), None)
        if not ch or not rev:
            d.conclusion = "sales 中未找到渠道列或营收列。"
            return
        d.trace.append(Step("RETRIEVE", f"从 {sales.name} 按 {ch} 聚合 {rev}"))
        agg: dict[str, float] = {}
        for r in sales.rows:
            agg[r[ch]] = agg.get(r[ch], 0.0) + float(r[rev])
            d.evidence.append(Evidence(sales.name, sales.rows.index(r) + 1,
                {ch: r[ch], rev: r[rev]}, f"{r[ch]} 贡献营收 {float(r[rev]):g}"))
        ranked = sorted(agg.items(), key=lambda x: -x[1])
        d.metrics = {"by_channel": ranked}
        d.trace.append(Step("REASON", "按营收排名各渠道"))
        best = ranked[0]
        d.conclusion = f"营收最高的是 **{best[0]}**（{best[1]:g}），是次高渠道的 " \
                       f"{(best[1]/ranked[1][1]):.1f} 倍。" if len(ranked) > 1 else f"{best[0]} 营收 {best[1]:g}。"
        d.action = f"下周把更多预算/精力投向 {best[0]}，并复盘为何它转化更好。"

    # ---- 技能：趋势归因 ---------------------------------------------------
    def _trend(self, d: Decision):
        sales = self._table("sales")
        if not sales:
            d.conclusion = "趋势分析需要 sales 数据源。"
            return
        week = next((c for c in sales.columns if c.lower() in ("week", "date")), None)
        metric = next((c for c in sales.numeric_cols if c in ("units", "revenue")), None)
        if not week or not metric:
            d.conclusion = "sales 中未找到时间列或指标列。"
            return
        d.trace.append(Step("RETRIEVE", f"从 {sales.name} 按 {week} 聚合 {metric}"))
        series: dict[str, float] = {}
        for r in sales.rows:
            series[r[week]] = series.get(r[week], 0.0) + float(r[metric])
        ws = sorted(series)
        if len(ws) < 2:
            d.conclusion = "数据点不足，无法判断趋势。"
            return
        first, last = series[ws[0]], series[ws[-1]]
        change = (last - first) / first * 100 if first else 0
        d.metrics = {"series": series}
        d.trace.append(Step("REASON", f"对比 {ws[0]} 与 {ws[-1]} 的 {metric}"))
        d.conclusion = (f"{metric} 从 {ws[0]} 的 {first:g} 变为 {ws[-1]} 的 {last:g}，"
                        f"{'上升' if change>=0 else '下降'} {abs(change):.0f}%。")
        d.action = ("增长来自需求上行，考虑加大备货与投放。" if change >= 0
                    else "需排查是需求下滑还是渠道/供给问题，再决定是否收缩。")

    # ---- 默认：概览 -------------------------------------------------------
    def _summary(self, d: Decision):
        d.trace.append(Step("RETRIEVE", "汇总各数据源规模"))
        parts = [f"{t.name}: {len(t)} 行，列 {', '.join(t.columns)}" for t in self.tables]
        d.conclusion = "已加载数据源概览——" + "；".join(parts) + \
                       "。可问我：哪个 SKU 最该补货？哪个渠道最值得投入？某指标为什么变化？"
        d.action = "用具体问题提问，例如「哪个 SKU 最该补货？为什么？」"
