"""送給 SQL Agent 的輸入：依對照組 (Arm) 注入資料字典（ticket 04）。"""
from services.data_dictionary import load_dictionary
from services.sql_agent_service import build_agent_input


def test_agent_input_carries_the_whole_dictionary_after_the_question():
    dictionary = load_dictionary("view")
    agent_input = build_agent_input("2026 年 9 月的運費是多少？", "2026-11-15", dictionary)
    assert agent_input.startswith("2026 年 9 月的運費是多少？")
    assert "[資料字典]\n" + dictionary in agent_input
    assert "2026-11-15" in agent_input


def test_agent_input_has_no_dictionary_section_when_the_arm_has_none():
    assert "[資料字典]" not in build_agent_input("總運費是多少？", "2026-11-15", None)


def test_agent_is_told_its_last_sql_must_answer_the_whole_question():
    # 使用者看到的「查詢依據」就是最後一句 SQL 的結果；分多句查再自己算，表格會和摘要對不起來
    agent_input = build_agent_input("提單 X 的請款比報價多多少？", "2026-11-15", None)
    assert "最後執行的那一句 SQL 必須單獨就能回答整個問題" in agent_input
