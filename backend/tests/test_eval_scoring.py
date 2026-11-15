"""評估集判分：拿 Agent 最後一句 SQL 的執行結果比對標準答案（ADR-0006）。"""
import pytest

from evaluation.scoring import Number, Pairs, Value, score


# ---- 一個數字：結果只有一列，且其中某一格在 ±0.01 內 ----

def test_number_matches_a_single_cell_within_a_cent():
    assert score([(93808.1349,)], Number(93808.13))
    assert not score([(93808.15,)], Number(93808.13))


def test_number_may_sit_in_any_column_of_the_single_row():
    assert score([("Tesla Logistics", 20921.52, 9)], Number(20921.52))


def test_number_needs_exactly_one_row():
    # 多列裡剛好有一列對到不算：避免把「列出一堆數字」誤判成答對
    assert not score([(1.0,), (20921.52,)], Number(20921.52))
    assert not score([], Number(0))


def test_number_ignores_text_cells_and_nulls():
    assert not score([("20921.52", None)], Number(20921.52))
    assert score([(None, 7)], Number(7))


# ---- 一個值：第一列含有這個值 ----

def test_value_must_be_in_the_first_row():
    assert score([("MSCU34396624", 4978.97, 1987.33), ("EGLV01670704", 3516.59, 1250.99)], Value("MSCU34396624"))
    assert not score([("EGLV01670704",), ("MSCU34396624",)], Value("MSCU34396624"))
    assert not score([], Value("MSCU34396624"))


# ---- 一組對應：每列 (鍵, 數字) 與標準答案逐一配對，不看順序 ----

GOLD_PAIRS = Pairs({"ASUS Tek": 900.49, "Apple Inc.": 12520.5})


def test_pairs_match_regardless_of_row_order_and_extra_columns():
    assert score([("Apple Inc.", 12520.504, 8), ("ASUS Tek", 900.49, 2)], GOLD_PAIRS)


def test_pairs_fail_on_a_missing_extra_or_wrong_row():
    assert not score([("ASUS Tek", 900.49)], GOLD_PAIRS)
    assert not score([("ASUS Tek", 900.49), ("Apple Inc.", 12520.5), ("TSMC Export", 1.0)], GOLD_PAIRS)
    assert not score([("ASUS Tek", 900.49), ("Apple Inc.", 12071.09)], GOLD_PAIRS)
