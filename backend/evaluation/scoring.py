"""評估集判分（ADR-0006）：拿 Agent 最後一句 SQL 的執行結果比對標準答案。

確定性、可重現；不用 LLM 評審。數字容許 ±0.01，集合比對不看順序。
"""
from dataclasses import dataclass
from typing import Union

TOLERANCE = 0.01


@dataclass(frozen=True)
class Number:
    """一個數字：結果只有一列，且其中某一格在容許誤差內。"""
    value: float


@dataclass(frozen=True)
class Value:
    """一個值（如提單號、港口）：結果的第一列含有它，允許多帶欄位或多列排名。"""
    value: str


@dataclass(frozen=True)
class Pairs:
    """一組 (鍵 → 數字) 對應：每列與標準答案逐一配對，不看順序、不多不少。"""
    values: dict[str, float]


Gold = Union[Number, Value, Pairs]


def _numbers(row: tuple) -> list[float]:
    return [cell for cell in row if isinstance(cell, (int, float)) and not isinstance(cell, bool)]


def _close(a: float, b: float) -> bool:
    return abs(a - b) <= TOLERANCE


def score(rows: list[tuple], gold: Gold) -> bool:
    if isinstance(gold, Number):
        # 多列裡剛好有一列對到不算，避免把「列出一堆數字」誤判成答對
        return len(rows) == 1 and any(_close(n, gold.value) for n in _numbers(rows[0]))
    if isinstance(gold, Value):
        return bool(rows) and gold.value in rows[0]
    if isinstance(gold, Pairs):
        if len(rows) != len(gold.values):
            return False
        unmatched = dict(gold.values)
        for row in rows:
            key = next((cell for cell in row if cell in unmatched), None)
            if key is None or not any(_close(n, unmatched[key]) for n in _numbers(row)):
                return False
            del unmatched[key]
        return not unmatched
    raise TypeError(f"未知的標準答案型態：{gold!r}")
