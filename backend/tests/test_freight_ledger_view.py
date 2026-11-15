"""運費帳原樣載入、參考表與 freight_charges view（ticket 03）。

標準答案一律從 02 的乾淨原始資料 (freight_ledger_clean.csv) 算，絕不從 view 查（ADR-0006）。
"""
import csv
from pathlib import Path

import pytest
from sqlalchemy import text
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

from db.freight_ledger import load_freight_ledger
from db.models import BillOfLading
from scripts.demo_bills import generate_bills_of_lading

SOURCE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"


def read_csv(name):
    with (SOURCE_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


@pytest.fixture
def engine():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        for bill in generate_bills_of_lading():
            session.add(BillOfLading(**{k: v for k, v in bill.items() if k != "target_billed_usd"}))
        session.commit()
    load_freight_ledger(engine)
    return engine


def query(engine, sql):
    with engine.connect() as conn:
        return [dict(row._mapping) for row in conn.execute(text(sql))]


def test_raw_ledger_is_the_finance_export_word_for_word(engine):
    raw = query(engine, "SELECT BL_NO, CUSTOMER, CHG_CODE, AMOUNT, INV_DATE FROM freight_ledger ORDER BY rowid")
    assert raw == read_csv("freight_ledger_export.csv")


def test_loading_again_does_not_duplicate_the_raw_ledger(engine):
    load_freight_ledger(engine)
    assert query(engine, "SELECT COUNT(*) AS n FROM freight_ledger")[0]["n"] == len(read_csv("freight_ledger_export.csv"))


@pytest.fixture(scope="module")
def clean():
    """乾淨 Charge Line，附上它在財務匯出檔裡的原始寫法（第 i 列對應第 i 筆）。"""
    known = {bl["bl_number"] for bl in generate_bills_of_lading()}
    lines = read_csv("freight_ledger_clean.csv")
    for line, row in zip(lines, read_csv("freight_ledger_export.csv")):
        line["raw"] = row
        if line["bl_number"] not in known:
            line["match_status"] = "unmatched"
        elif row["BL_NO"] != line["bl_number"]:
            line["match_status"] = "normalized_match"
        else:
            line["match_status"] = "matched"
    return lines


def test_bl_numbers_are_normalized_and_every_line_keeps_a_match_status(engine, clean):
    view = query(engine, "SELECT bl_number, charge_code, match_status FROM freight_charges")
    assert sorted((r["bl_number"], r["charge_code"], r["match_status"]) for r in view) == \
        sorted((c["bl_number"], c["charge_code"], c["match_status"]) for c in clean)
    statuses = {c["match_status"] for c in clean}
    assert statuses == {"matched", "normalized_match", "unmatched"}


def view_by_key(engine, columns):
    rows = query(engine, f"SELECT bl_number, charge_code, {columns} FROM freight_charges")
    return {(r["bl_number"], r["charge_code"]): r for r in rows}


def test_customers_map_to_the_shipper_and_unknown_names_are_kept_and_flagged(engine, clean):
    view = view_by_key(engine, "raw_customer, customer, is_unmapped_customer")
    unmapped = {"Apple Taiwan Branch", "TSMC Arizona"}  # 02 刻意不放進別名表的寫法
    for c in clean:
        row = view[(c["bl_number"], c["charge_code"])]
        assert row["raw_customer"] == c["raw"]["CUSTOMER"]
        if c["raw"]["CUSTOMER"] in unmapped:
            assert (row["customer"], row["is_unmapped_customer"]) == (c["raw"]["CUSTOMER"], 1)
        else:
            assert (row["customer"], row["is_unmapped_customer"]) == (c["customer"], 0)
    assert sum(r["is_unmapped_customer"] for r in view.values()) == 2


def test_invoice_dates_in_four_formats_become_iso_dates(engine, clean):
    view = view_by_key(engine, "invoice_date")
    assert all(view[(c["bl_number"], c["charge_code"])]["invoice_date"] == c["invoice_date"] for c in clean)


def test_on_board_date_comes_from_the_bill_of_lading_and_is_empty_when_unmatched(engine, clean):
    on_board = {bl["bl_number"]: bl["on_board_date"] for bl in generate_bills_of_lading()}
    view = view_by_key(engine, "on_board_date")
    for c in clean:
        assert view[(c["bl_number"], c["charge_code"])]["on_board_date"] == on_board.get(c["bl_number"])


@pytest.fixture(scope="module")
def clean_usd(clean):
    """乾淨資料依 fx_rates.csv 換算的每筆 USD 金額，key 為 (bl_number, charge_code)。"""
    rates = {(r["month"], r["currency"]): float(r["units_per_usd"]) for r in read_csv("fx_rates.csv")}
    return {
        (c["bl_number"], c["charge_code"]): float(c["amount"]) / rates[(c["invoice_date"][:7], c["currency"])]
        for c in clean
    }


def test_amount_strings_become_iso_currency_and_signed_original_amount(engine, clean):
    view = view_by_key(engine, "raw_amount, currency, amount, is_credit_note")
    for c in clean:
        row = view[(c["bl_number"], c["charge_code"])]
        assert row["raw_amount"] == c["raw"]["AMOUNT"]
        assert row["currency"] == c["currency"]
        # Credit Note 不論原始怎麼寫正負號，一律為負
        assert row["amount"] == pytest.approx(float(c["amount"])), c["raw"]["AMOUNT"]
        assert row["is_credit_note"] == (c["charge_code"] == "CN")


def test_amount_usd_uses_the_invoice_months_rate(engine, clean_usd):
    view = view_by_key(engine, "amount_usd")
    assert all(view[key]["amount_usd"] == pytest.approx(usd, abs=0.01) for key, usd in clean_usd.items())


def test_billed_amount_per_bill_of_lading_matches_the_clean_source(engine, clean_usd):
    expected = {}
    for (bl_number, _), usd in clean_usd.items():
        expected[bl_number] = expected.get(bl_number, 0) + usd
    billed = query(engine, "SELECT bl_number, SUM(amount_usd) AS billed FROM freight_charges GROUP BY bl_number")
    assert {r["bl_number"] for r in billed} == expected.keys()
    assert all(r["billed"] == pytest.approx(expected[r["bl_number"]], abs=0.01) for r in billed)
