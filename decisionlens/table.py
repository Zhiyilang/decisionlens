"""DecisionLens — 数据表加载与类型推断（纯标准库）。"""

from __future__ import annotations

import csv
from dataclasses import dataclass, field


@dataclass
class Table:
    name: str
    columns: list
    rows: list              # list[dict]
    numeric_cols: set = field(default_factory=set)

    def col(self, name: str):
        return [r.get(name) for r in self.rows]

    def num(self, name: str):
        return [float(r[name]) for r in self.rows if r.get(name) not in (None, "")]

    def __len__(self):
        return len(self.rows)


def _is_number(s: str) -> bool:
    if s is None:
        return False
    s = s.strip()
    if s == "":
        return False
    try:
        float(s)
        return True
    except ValueError:
        return False


def load_csv(path: str, name: str | None = None) -> Table:
    name = name or path.replace("\\", "/").split("/")[-1]
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        columns = reader.fieldnames or []
        rows = [dict(r) for r in reader]
    # 推断数值列：非空值都能解析为数字
    numeric = set()
    for c in columns:
        vals = [r.get(c, "") for r in rows if (r.get(c) or "").strip() != ""]
        if vals and all(_is_number(v) for v in vals):
            numeric.add(c)
    return Table(name=name, columns=list(columns), rows=rows, numeric_cols=numeric)


def find_join_keys(tables: list[Table]) -> list[str]:
    """找出多张表共有的列名（潜在连接键，如 sku / week / channel）。"""
    common = None
    for t in tables:
        s = set(c.lower() for c in t.columns)
        common = s if common is None else (common & s)
    return sorted(common or [])
