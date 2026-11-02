"""Overdue and upcoming items in results/todo.md."""

import datetime as dt
import re

from .. import config
from ..util import read_text


def collect(cfg):
    text = read_text(config.TODO)
    if text is None:
        return None
    today = dt.date.today()
    overdue, soon = [], []
    for l in text.splitlines():
        m = re.match(r"\|\s*(\d{4}-\d{2}-\d{2})\s*\|\s*(.+?)\s*\|", l)
        if not m:
            continue
        due = dt.date.fromisoformat(m.group(1))
        item = f"{m.group(1)} {m.group(2)[:80]}"
        if due < today:
            overdue.append(item)
        elif (due - today).days <= 7:
            soon.append(item)
    return {"overdue": overdue, "due_within_7_days": soon}
