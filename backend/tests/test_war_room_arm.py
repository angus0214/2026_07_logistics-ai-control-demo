"""戰情室的對照組 (Arm)：查 freight_charges view，帶 View 版資料字典（ticket 05、ADR-0005）。"""
import pytest
import yaml
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import db.models  # noqa: F401  註冊 SQLModel 資料表
from db.freight_ledger import load_freight_ledger
from services.data_dictionary import load_dictionary
from services.sql_agent_service import WAR_ROOM_ARM
from services.sql_guard import GuardedSQLDatabase, UnsafeQueryError, validate_sql


@pytest.fixture(scope="module")
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    load_freight_ledger(engine)
    return engine


def test_agent_database_can_list_and_describe_the_cleaned_view(engine):
    db = GuardedSQLDatabase(engine, include_tables=["bills_of_lading", "freight_charges"])
    assert set(db.get_usable_table_names()) == {"bills_of_lading", "freight_charges"}
    # LangChain 描述 schema 時會丟掉沒有型別的欄位；view 的每個欄位都要讓 Agent 看得到
    schema = db.get_table_info(["freight_charges"]).split("*/")[0].split("/*")[0]
    for column in ["bl_number", "match_status", "customer", "is_unmapped_customer", "is_credit_note",
                   "currency", "amount", "amount_usd", "invoice_date", "on_board_date"]:
        assert f"\t{column} " in schema, column
    assert "freight_ledger" not in db.get_table_info()


def test_war_room_queries_the_cleaned_view_and_never_the_raw_ledger():
    validate_sql("SELECT bl_number, SUM(amount_usd) FROM freight_charges GROUP BY bl_number", WAR_ROOM_ARM.allowed_tables)
    for hidden in ["freight_ledger", "customer_aliases", "fx_rates"]:
        with pytest.raises(UnsafeQueryError):
            validate_sql(f"SELECT * FROM {hidden}", WAR_ROOM_ARM.allowed_tables)


def test_war_room_dictionary_describes_exactly_the_tables_it_may_query():
    assert WAR_ROOM_ARM.dictionary == "view"
    described = yaml.safe_load(load_dictionary(WAR_ROOM_ARM.dictionary))["tables"]
    assert set(described) == set(WAR_ROOM_ARM.allowed_tables)
