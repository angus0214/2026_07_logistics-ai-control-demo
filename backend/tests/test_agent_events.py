"""SQL Agent 串流事件：執行 SQL 的事件要帶上原始 SQL，供評估判分（ticket 06）。"""
from services.sql_agent_service import action_event


def test_query_action_carries_the_sql_it_ran():
    sql = "SELECT SUM(amount_usd) FROM freight_charges"
    assert action_event("sql_db_query", {"query": sql}) == {"event": "thought", "data": f"執行 SQL 查詢: {sql}", "sql": sql}


def test_query_action_accepts_a_plain_string_input():
    assert action_event("sql_db_query", "SELECT 1")["sql"] == "SELECT 1"


def test_other_tools_are_thoughts_without_sql():
    assert action_event("sql_db_schema", {"table_names": "bills_of_lading"}) == {
        "event": "thought", "data": "正在使用 sql_db_schema 分析資料庫結構...",
    }
