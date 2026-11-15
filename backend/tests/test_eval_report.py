"""評估報告的彙總：整體答對率、穩定答對題數、依陷阱分列。"""
from evaluation.run_eval import Record, summarize


def rec(arm, qid, trap, run, correct):
    return Record(arm=arm, qid=qid, trap=trap, run=run, correct=correct,
                  reason="correct" if correct else "wrong_result", sql=None, answer=None)


RECORDS = [
    # View + Dictionary：CN-1 三次全對、CT-1 對兩次
    *[rec("View + Dictionary", "CN-1", "Credit Note", r, True) for r in (1, 2, 3)],
    *[rec("View + Dictionary", "CT-1", "對照題", r, r != 2) for r in (1, 2, 3)],
    # Raw：CN-1 全錯、CT-1 全對
    *[rec("Raw", "CN-1", "Credit Note", r, False) for r in (1, 2, 3)],
    *[rec("Raw", "CT-1", "對照題", r, True) for r in (1, 2, 3)],
]


def test_accuracy_counts_every_run():
    summary = summarize(RECORDS)
    assert summary["View + Dictionary"]["correct"] == 5
    assert summary["View + Dictionary"]["total"] == 6
    assert summary["Raw"]["correct"] == 3


def test_stable_questions_need_all_runs_correct():
    summary = summarize(RECORDS)
    assert summary["View + Dictionary"]["stable"] == 1   # 只有 CN-1 三次全對
    assert summary["Raw"]["stable"] == 1                 # 只有 CT-1


def test_breaks_down_by_trap():
    by_trap = summarize(RECORDS)["View + Dictionary"]["by_trap"]
    assert by_trap["Credit Note"] == (3, 3)
    assert by_trap["對照題"] == (2, 3)
