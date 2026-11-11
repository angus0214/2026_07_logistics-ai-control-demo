"""SQL Agent 執行期防護的測試 (ADR-0005)。不呼叫 LLM。"""
import sqlite3

import pytest
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from db.database import create_readonly_engine
from services.sql_guard import (
    GuardedSQLDatabase,
    UnsafeQueryError,
    run_guarded_query,
    validate_sql,
)

ALLOWED = ["bills_of_lading"]


@pytest.fixture
def db_path(tmp_path):
    path = tmp_path / "test.db"
    conn = sqlite3.connect(path)
    conn.executescript(
        """
        CREATE TABLE bills_of_lading (id INTEGER PRIMARY KEY, bl_number TEXT, freight_cost REAL);
        CREATE TABLE bad_cases (id INTEGER PRIMARY KEY, image_base64 TEXT);
        INSERT INTO bad_cases (image_base64) VALUES ('secret');
        """
    )
    conn.executemany(
        "INSERT INTO bills_of_lading (bl_number, freight_cost) VALUES (?, ?)",
        [(f"BL{i:04d}", float(i)) for i in range(250)],
    )
    conn.commit()
    conn.close()
    return path


@pytest.fixture
def ro_engine(db_path):
    engine = create_readonly_engine(str(db_path))
    yield engine
    engine.dispose()


# --- 解析防線：允許的查詢 ---

@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM bills_of_lading",
        "select sum(freight_cost) from BILLS_OF_LADING;",
        "WITH t AS (SELECT * FROM bills_of_lading) SELECT count(*) FROM t",
        "SELECT bl_number FROM bills_of_lading UNION SELECT bl_number FROM bills_of_lading",
        "SELECT * FROM (SELECT bl_number FROM bills_of_lading) AS sub",
        "SELECT 1",
    ],
)
def test_allows_single_read_query_on_whitelisted_tables(sql):
    validate_sql(sql, ALLOWED)


# --- 解析防線：拒絕的查詢 ---

@pytest.mark.parametrize(
    "sql",
    [
        "INSERT INTO bills_of_lading (bl_number) VALUES ('x')",
        "UPDATE bills_of_lading SET freight_cost = 0",
        "DELETE FROM bills_of_lading",
        "DROP TABLE bills_of_lading",
        "PRAGMA table_info(bills_of_lading)",
        "ATTACH DATABASE 'other.db' AS other",
        "VACUUM",
    ],
)
def test_rejects_non_select_statements(sql):
    with pytest.raises(UnsafeQueryError):
        validate_sql(sql, ALLOWED)


def test_rejects_multiple_statements():
    with pytest.raises(UnsafeQueryError, match="一次只能執行一句"):
        validate_sql("SELECT 1; DROP TABLE bills_of_lading", ALLOWED)


@pytest.mark.parametrize(
    "sql",
    [
        "SELECT * FROM bad_cases",
        "SELECT * FROM main.bad_cases",
        "SELECT * FROM (SELECT * FROM bad_cases)",
        "SELECT * FROM bills_of_lading WHERE id IN (SELECT id FROM bad_cases)",
        "SELECT * FROM bills_of_lading JOIN bad_cases ON 1=1",
        "WITH t AS (SELECT * FROM bad_cases) SELECT * FROM t",
        "SELECT name FROM sqlite_master",
    ],
)
def test_rejects_tables_outside_whitelist(sql):
    with pytest.raises(UnsafeQueryError, match="不在可查詢範圍內"):
        validate_sql(sql, ALLOWED)


def test_rejects_table_valued_functions():
    with pytest.raises(UnsafeQueryError):
        validate_sql("SELECT * FROM pragma_table_info('bad_cases')", ALLOWED)


def test_whitelist_is_configurable():
    validate_sql("SELECT * FROM bad_cases", ["bad_cases"])


# --- 唯讀連線防線：即使繞過解析也寫不進去 ---

def test_readonly_engine_rejects_writes_on_its_own(ro_engine):
    with ro_engine.connect() as conn:
        with pytest.raises(OperationalError, match="readonly"):
            conn.execute(text("DELETE FROM bills_of_lading"))


# --- 筆數上限 ---

def test_truncates_beyond_max_rows(ro_engine):
    columns, rows, truncated = run_guarded_query(
        ro_engine, "SELECT bl_number FROM bills_of_lading ORDER BY id", ALLOWED, max_rows=200
    )
    assert columns == ["bl_number"]
    assert len(rows) == 200
    assert truncated is True
    # 抓 N+1 而不是包 LIMIT：原本的排序保持不變
    assert rows[0] == ("BL0000",)


def test_not_truncated_when_within_limit(ro_engine):
    _, rows, truncated = run_guarded_query(
        ro_engine, "SELECT count(*) FROM bills_of_lading", ALLOWED
    )
    assert rows == [(250,)]
    assert truncated is False


# --- 逾時 ---

def test_interrupts_slow_query(ro_engine):
    slow_sql = (
        "WITH RECURSIVE n(x) AS (SELECT 1 UNION ALL SELECT x + 1 FROM n) "
        "SELECT count(*) FROM n"
    )
    with pytest.raises(UnsafeQueryError, match="被中斷"):
        run_guarded_query(ro_engine, slow_sql, ALLOWED, timeout_seconds=0.2)

    # 中斷後連線仍可正常使用（progress handler 已被清除）
    _, rows, _ = run_guarded_query(ro_engine, "SELECT 1", ALLOWED)
    assert rows == [(1,)]


# --- LangChain 介面：錯誤要以文字回給 Agent ---

def test_guarded_db_returns_errors_as_text_for_agent(ro_engine):
    db = GuardedSQLDatabase(ro_engine, include_tables=ALLOWED)
    result = db.run_no_throw("SELECT * FROM bad_cases")
    assert result.startswith("Error:")
    assert "secret" not in result


def test_guarded_db_adds_truncation_note(ro_engine):
    db = GuardedSQLDatabase(ro_engine, include_tables=ALLOWED, max_rows=10)
    result = db.run_no_throw("SELECT bl_number FROM bills_of_lading")
    assert "結果已截斷" in result


def test_guarded_db_hides_other_tables_from_schema(ro_engine):
    db = GuardedSQLDatabase(ro_engine, include_tables=ALLOWED)
    assert db.get_usable_table_names() == ["bills_of_lading"]
