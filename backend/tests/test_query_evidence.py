"""查詢依據 (Query Evidence)：後端拿 Agent 最後一句 SQL 的結果直接產生表格（ticket 07）。"""
import json

import pytest
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from db.models import BillOfLading
from services.sql_agent_service import result_event

ALLOWED = ("bills_of_lading",)


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for i, cost in enumerate([100.5, 200.25], start=1):
            session.add(BillOfLading(bl_number=f"EGLV0000000{i}", shipper="Apple Inc.", consignee="BestBuy US",
                                     destination="USLAX (Los Angeles)", gross_weight=1000.0,
                                     freight_cost=cost, on_board_date="2026-09-01"))
        session.commit()
    return engine


def test_evidence_is_the_raw_result_of_the_last_sql(engine):
    sql = "SELECT bl_number, freight_cost FROM bills_of_lading ORDER BY bl_number"
    assert result_event(engine, sql, ALLOWED) == {
        "event": "result",
        "sql": sql,
        "columns": ["bl_number", "freight_cost"],
        "rows": [["EGLV00000001", 100.5], ["EGLV00000002", 200.25]],
        "truncated": False,
    }


def test_empty_result_is_still_evidence(engine):
    event = result_event(engine, "SELECT bl_number FROM bills_of_lading WHERE 1 = 0", ALLOWED)
    assert event["rows"] == [] and event["columns"] == ["bl_number"]


def test_no_evidence_without_sql(engine):
    assert result_event(engine, None, ALLOWED) is None


def test_no_evidence_when_the_query_fails_or_leaves_the_whitelist(engine):
    assert result_event(engine, "SELECT nope FROM bills_of_lading", ALLOWED) is None
    assert result_event(engine, "SELECT * FROM bad_cases", ALLOWED) is None


def test_marks_truncated_results(engine):
    event = result_event(engine, "SELECT bl_number FROM bills_of_lading", ALLOWED, max_rows=1)
    assert event["truncated"] is True and len(event["rows"]) == 1


def test_values_are_json_safe(engine):
    # created_at 是 datetime；SSE 用 json.dumps 送出，非基本型別要轉成字串
    event = result_event(engine, "SELECT created_at FROM bills_of_lading LIMIT 1", ALLOWED)
    assert isinstance(event["rows"][0][0], str)
    json.dumps(event)
