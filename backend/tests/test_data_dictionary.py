"""資料字典（ticket 04）：給人看也給 Agent 看，內容必須和實際 schema 一致。"""
import pytest
import yaml
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import SQLModel, create_engine

import db.models  # noqa: F401  註冊 SQLModel 資料表
from db.freight_ledger import load_freight_ledger
from services.data_dictionary import load_dictionary

# 每個字典版本對應的對照組 (Arm) 看得到的資料表
ARM_TABLES = {
    "view": {"bills_of_lading", "freight_charges"},
    "raw": {"bills_of_lading", "freight_ledger", "customer_aliases", "fx_rates"},
}


@pytest.fixture(scope="module")
def schema():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    load_freight_ledger(engine)
    with engine.connect() as conn:
        tables = [r[0] for r in conn.execute(text("SELECT name FROM sqlite_master WHERE type IN ('table', 'view')"))]
        return {t: {r[1] for r in conn.execute(text(f"PRAGMA table_info({t})"))} for t in tables}


@pytest.mark.parametrize("version", ["view", "raw"])
def test_dictionary_describes_exactly_the_tables_and_columns_its_arm_can_query(version, schema):
    tables = yaml.safe_load(load_dictionary(version))["tables"]
    assert tables.keys() == ARM_TABLES[version]
    for name, table in tables.items():
        assert set(table["columns"]) == schema[name], name


REQUIRED_RULES = {
    "freight_means_billed_amount",  # 沒指定的「運費」＝ Billed Amount
    "period_by_on_board_date",      # 期間預設以開航日為準，unmatched 不屬於任何期間
    "unmatched_in_totals",          # 沒指定期間的總額要含 unmatched
    "credit_note_negative",         # Credit Note 算負數
    "customer_is_shipper",          # 客戶＝Shipper
    "quoted_vs_billed",             # 「請款遠超報價」的門檻
}


@pytest.mark.parametrize("version", ["view", "raw"])
def test_dictionary_states_the_business_rules_and_which_table_answers_what(version):
    spec = yaml.safe_load(load_dictionary(version))
    assert spec["business_rules"].keys() == REQUIRED_RULES
    money_table = {"view": "freight_charges", "raw": "freight_ledger"}[version]
    assert money_table in spec["business_rules"]["freight_means_billed_amount"]
    assert "on_board_date" in spec["business_rules"]["period_by_on_board_date"]
    # 「運費」是全部費用類型，不能只篩 OF（海運費）
    assert all(code in spec["business_rules"]["freight_means_billed_amount"] for code in ["OF", "THC", "BAF", "CN"])
    assert "bills_of_lading" in spec["routing"]["shipments"]
    assert money_table in spec["routing"]["money"]


def test_view_dictionary_defines_billed_amount_as_sum_of_amount_usd():
    rules = yaml.safe_load(load_dictionary("view"))["business_rules"]
    assert "SUM(amount_usd)" in rules["freight_means_billed_amount"]


@pytest.mark.parametrize("version, hidden_table", [("view", "freight_ledger"), ("raw", "freight_charges")])
def test_dictionary_never_mentions_the_other_arms_table(version, hidden_table):
    assert hidden_table not in load_dictionary(version)

