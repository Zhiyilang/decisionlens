"""自包含 HTML 报告（轨迹 + 结论 + 证据引用表）。"""

from __future__ import annotations

import html as _html

from .agent import Decision


def _esc(s) -> str:
    return _html.escape(str(s))


_PHASE_COLOR = {
    "PERCEIVE": "#6366f1", "INDEX": "#0ea5e9", "RETRIEVE": "#14b8a6",
    "REASON": "#f59e0b", "EXPLAIN": "#ec4899", "ACT": "#16a34a",
}


def render_html(d: Decision) -> str:
    trace = "".join(
        f'<div class="step"><span class="phase" style="background:{_PHASE_COLOR.get(s.phase,"#334155")}">'
        f'{s.phase}</span><span>{_esc(s.detail)}</span></div>' for s in d.trace)
    ev = "".join(
        f'<tr><td>{_esc(e.source)}</td><td>{e.row}</td>'
        f'<td>{_esc("，".join(f"{k}={v}" for k,v in e.fields.items()))}</td>'
        f'<td>{_esc(e.claim)}</td></tr>' for e in d.evidence)
    return f"""<!DOCTYPE html>
<html lang="zh-CN"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>DecisionLens 决策报告</title>
<style>
 body{{font-family:-apple-system,"Segoe UI","Microsoft YaHei",sans-serif;margin:0;background:#f1f5f9;color:#0f172a}}
 .wrap{{max-width:900px;margin:0 auto;padding:28px 20px 60px}}
 h1{{font-size:23px;margin:0 0 4px}} .q{{color:#475569;font-size:15px;margin-bottom:20px}}
 .box{{background:#fff;border-radius:12px;padding:18px 20px;box-shadow:0 1px 3px rgba(0,0,0,.08);margin-bottom:16px}}
 .box h2{{font-size:15px;margin:0 0 10px;color:#334155}}
 .conclusion{{font-size:15px;line-height:1.6}}
 .action{{background:#f0fdf4;border-left:4px solid #16a34a;padding:12px 14px;border-radius:8px;font-size:15px;line-height:1.6}}
 .step{{display:flex;gap:10px;align-items:flex-start;margin:7px 0;font-size:14px}}
 .phase{{color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:6px;min-width:74px;text-align:center}}
 table{{width:100%;border-collapse:collapse;font-size:13px}}
 th,td{{padding:7px 9px;text-align:left;border-bottom:1px solid #e2e8f0;vertical-align:top}}
 th{{background:#e2e8f0;font-weight:600}}
 .foot{{margin-top:24px;color:#94a3b8;font-size:12px}}
</style></head><body><div class="wrap">
 <h1>DecisionLens 决策报告</h1>
 <div class="q">问题：{_esc(d.question)}</div>
 <div class="box"><h2>智能体轨迹</h2>{trace}</div>
 <div class="box"><h2>结论</h2><div class="conclusion">{_esc(d.conclusion)}</div></div>
 <div class="box"><h2>下一步行动</h2><div class="action">{_esc(d.action)}</div></div>
 <div class="box"><h2>证据引用（{len(d.evidence)}）</h2>
   <table><thead><tr><th>来源</th><th>行</th><th>字段</th><th>支撑的判断</th></tr></thead>
   <tbody>{ev}</tbody></table></div>
 <div class="foot">由 DecisionLens 生成 · github.com/Zhiyilang/decisionlens · MIT · 结论基于所提供数据，重大决策请人工复核</div>
</div></body></html>"""
