"""評估集題目與標準答案（ticket 06、ADR-0006）。"""
import inspect
from collections import Counter

import pytest

import evaluation.questions as questions_module
from evaluation.questions import HOLDOUT_QUESTIONS, QUESTIONS
from evaluation.scoring import Number, Pairs, Value

TRAPS = {"Credit Note", "多幣別", "客戶別名", "Unmatched", "開航日 vs 發票日", "報價 vs 請款", "提單號正規化"}


def by_id(qid):
    return next(q for q in QUESTIONS if q.qid == qid)


def test_twenty_questions_two_per_trap_plus_six_controls():
    assert len(QUESTIONS) == 20
    assert len({q.qid for q in QUESTIONS}) == 20
    counts = Counter(q.trap for q in QUESTIONS)
    assert counts == {**{trap: 2 for trap in TRAPS}, "對照題": 6}


def test_questions_name_explicit_periods_never_relative_time():
    for q in QUESTIONS:
        assert not any(word in q.text for word in ["上個月", "本月", "今年", "去年", "最近"]), q.text


@pytest.mark.parametrize("qid, gold", [
    ("CT-1", Number(19)),                 # 9 月開航 19 張（ticket 01 已在線上確認）
    ("CN-2", Number(-608.20)),            # 10 月開航的兩筆 USD Credit Note：-279.20 + -329.00
    ("UM-2", Number(7)),                  # 產生器固定 7 筆系統外貨件
    ("QB-1", Value("MSCU34396624")),      # ticket 01 的 4 張異常之一，也是 8 月唯一一張
])
def test_hand_checkable_gold_answers(qid, gold):
    actual = by_id(qid).gold
    assert type(actual) is type(gold)
    if isinstance(gold, Number):
        assert actual.value == pytest.approx(gold.value, abs=0.01)
    else:
        assert actual == gold


def test_per_customer_question_has_one_pair_per_customer_with_october_shipments():
    gold = by_id("PD-2").gold
    assert isinstance(gold, Pairs)
    assert set(gold.values) == {"ASUS Tek", "Apple Inc.", "Foxconn Global", "Nvidia Corp", "Samsung Electronics", "TSMC Export"}


def test_gold_answers_never_come_from_the_cleaned_view():
    source = inspect.getsource(questions_module)
    # 只能讀乾淨原始資料，不能讀 view 或弄髒的匯出檔
    assert "freight_charges" not in source and "freight_ledger_export" not in source


# ---- 驗證題 (ticket 07)：沒用過的多步計算題，用來驗證「最後一句 SQL 單獨回答」規則 ----

def test_holdout_has_six_new_questions_unlike_the_main_set():
    assert len(HOLDOUT_QUESTIONS) == 6
    assert len({q.qid for q in HOLDOUT_QUESTIONS}) == 6
    assert not {q.text for q in HOLDOUT_QUESTIONS} & {q.text for q in QUESTIONS}
    assert not {q.qid for q in HOLDOUT_QUESTIONS} & {q.qid for q in QUESTIONS}


def test_holdout_questions_name_explicit_periods():
    for q in HOLDOUT_QUESTIONS:
        assert not any(word in q.text for word in ["上個月", "本月", "今年", "去年", "最近"]), q.text


def test_highest_quote_question_is_not_the_highest_billed_shipment():
    # 報價最高 (EGLV46945080) 和請款最高 (ONEY83837288) 是不同張，題目才分得出有沒有用對欄位
    assert next(q for q in HOLDOUT_QUESTIONS if q.qid == "H-5").gold == Value("EGLV46945080")
