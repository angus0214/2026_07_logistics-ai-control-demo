"""運費帳產生器：乾淨 Charge Line 與弄髒後的財務匯出檔（ticket 02）。"""
import re
from collections import Counter
from datetime import date, datetime

import pytest

from scripts.demo_bills import SHIPPERS, generate_bills_of_lading
from scripts.demo_freight_ledger import (
    CUSTOMER_ALIASES,
    UNMAPPED_CUSTOMER_NAMES,
    dirty_export,
    generate_charge_lines,
    to_usd,
)


@pytest.fixture(scope="module")
def bills():
    return generate_bills_of_lading()


@pytest.fixture(scope="module")
def lines(bills):
    return generate_charge_lines(bills)


@pytest.fixture(scope="module")
def export(lines):
    return dirty_export(lines)


def test_same_charge_lines_every_run(bills, lines):
    assert generate_charge_lines(bills) == lines


def test_every_bill_of_lading_has_one_to_three_charge_lines(bills, lines):
    per_bl = Counter(line["bl_number"] for line in lines)
    assert all(1 <= per_bl[bl["bl_number"]] <= 3 for bl in bills)


def test_charge_codes_are_clean_codes(lines):
    assert {line["charge_code"] for line in lines} <= {"OF", "THC", "BAF", "CN"}


def test_to_usd_divides_by_the_invoice_months_rate():
    # 2026-09 的 TWD 匯率是 32.10（每 1 USD）
    assert to_usd(3210, "TWD", "2026-09-15") == pytest.approx(100.0)
    assert to_usd(-50, "USD", "2026-11-02") == -50


def test_billed_amount_of_each_bill_is_within_one_usd_of_its_target(bills, lines):
    billed = Counter()
    for line in lines:
        billed[line["bl_number"]] += to_usd(line["amount"], line["currency"], line["invoice_date"])
    assert all(abs(billed[bl["bl_number"]] - bl["target_billed_usd"]) < 1 for bl in bills)


def test_credit_notes_are_negative_and_on_about_15_percent_of_bills(lines):
    credit_notes = [line for line in lines if line["charge_code"] == "CN"]
    assert all(line["amount"] < 0 for line in credit_notes)
    assert all(line["amount"] > 0 for line in lines if line["charge_code"] != "CN")
    assert 6 <= len({line["bl_number"] for line in credit_notes}) <= 9


def test_six_to_eight_lines_belong_to_shipments_outside_the_bills_of_lading(bills, lines):
    known = {bl["bl_number"] for bl in bills}
    unmatched = [line for line in lines if line["bl_number"] not in known]
    assert 6 <= len(unmatched) <= 8
    # 外觀和真的提單號一樣，只是營運系統裡沒有這張提單
    assert all(re.fullmatch(r"(EGLV|YMLU|ONEY|MSCU|HLXU)\d{8}", line["bl_number"]) for line in unmatched)


def test_about_120_charge_lines_in_total(lines):
    assert 110 <= len(lines) <= 130


def test_currency_mix_is_60_usd_25_twd_10_eur_5_jpy(lines):
    share = {cur: n / len(lines) for cur, n in Counter(line["currency"] for line in lines).items()}
    expected = {"USD": 0.60, "TWD": 0.25, "EUR": 0.10, "JPY": 0.05}
    assert share.keys() == expected.keys()
    assert all(share[cur] == pytest.approx(expected[cur], abs=0.02) for cur in expected)


def test_invoices_are_dated_3_to_20_days_after_on_board_and_some_cross_into_next_month(bills, lines):
    on_board = {bl["bl_number"]: date.fromisoformat(bl["on_board_date"]) for bl in bills}
    matched = [line for line in lines if line["bl_number"] in on_board]
    gaps = [(date.fromisoformat(line["invoice_date"]) - on_board[line["bl_number"]]).days for line in matched]
    assert all(3 <= gap <= 20 for gap in gaps)
    # 「以開航日算」與「以發票日算」期間答案不同的陷阱
    crossing = [line for line in matched if line["invoice_date"][:7] != on_board[line["bl_number"]].isoformat()[:7]]
    assert len(crossing) >= 10
    assert any(line["invoice_date"].startswith("2026-11") for line in crossing)


def test_customer_is_the_shipper_of_the_bill_of_lading(bills, lines):
    shipper = {bl["bl_number"]: bl["shipper"] for bl in bills}
    assert all(line["customer"] == shipper[line["bl_number"]] for line in lines if line["bl_number"] in shipper)
    # 系統外貨件也是既有客戶出的貨
    assert all(line["customer"] in SHIPPERS for line in lines if line["bl_number"] not in shipper)



# ---- 財務匯出檔（弄髒後）：第 i 列對應第 i 筆 Charge Line ----

def test_export_uses_finance_column_names_one_row_per_charge_line(lines, export):
    assert len(export) == len(lines)
    assert all(list(row) == ["BL_NO", "CUSTOMER", "CHG_CODE", "AMOUNT", "INV_DATE"] for row in export)


def test_export_is_the_same_every_run(lines, export):
    assert dirty_export(lines) == export


def test_export_keeps_charge_codes_clean_and_has_no_duplicate_rows(lines, export):
    assert [row["CHG_CODE"] for row in export] == [line["charge_code"] for line in lines]
    assert len({tuple(row.values()) for row in export}) == len(export)


def test_about_15_percent_of_bl_numbers_differ_only_by_case_space_or_hyphen(lines, export):
    def normalize(raw):
        return re.sub(r"[\s-]", "", raw).upper()

    assert all(normalize(row["BL_NO"]) == line["bl_number"] for row, line in zip(export, lines))
    variants = [row for row, line in zip(export, lines) if row["BL_NO"] != line["bl_number"]]
    assert len(variants) / len(lines) == pytest.approx(0.15, abs=0.02)


def test_about_40_percent_of_customer_names_are_known_aliases(lines, export):
    renamed = [(row, line) for row, line in zip(export, lines) if row["CUSTOMER"] != line["customer"]]
    assert len(renamed) / len(lines) == pytest.approx(0.40, abs=0.03)
    aliased = [(row, line) for row, line in renamed if row["CUSTOMER"] not in UNMAPPED_CUSTOMER_NAMES]
    assert all(row["CUSTOMER"] in CUSTOMER_ALIASES[line["customer"]] for row, line in aliased)


def test_two_rows_use_customer_names_missing_from_the_alias_table(export):
    unmapped = [row for row in export if row["CUSTOMER"] in UNMAPPED_CUSTOMER_NAMES]
    assert len(unmapped) == 2
    known_names = set(SHIPPERS) | {alias for aliases in CUSTOMER_ALIASES.values() for alias in aliases}
    assert not set(UNMAPPED_CUSTOMER_NAMES) & known_names


CURRENCY_MARKERS = {"USD": ["USD", "usd", "US$"], "TWD": ["NT$", "TWD", "twd"], "EUR": ["€", "EUR", "eur"], "JPY": ["¥", "JPY", "jpy"]}


def test_amount_is_a_string_with_currency_marker_and_the_original_amount(lines, export):
    for row, line in zip(export, lines):
        assert any(marker in row["AMOUNT"] for marker in CURRENCY_MARKERS[line["currency"]]), row["AMOUNT"]
        digits = re.sub(r"[^\d.]", "", row["AMOUNT"])
        assert float(digits) == pytest.approx(abs(line["amount"])), row["AMOUNT"]


def test_each_currency_is_written_at_least_three_ways(lines, export):
    for currency in CURRENCY_MARKERS:
        shapes = {re.sub(r"\d", "9", re.sub(r"[-()]", "", row["AMOUNT"]))[:3]
                  for row, line in zip(export, lines) if line["currency"] == currency}
        assert len(shapes) >= 3, (currency, shapes)


def test_credit_notes_are_mostly_written_positive_a_few_as_minus_or_parentheses(lines, export):
    def written_negative(amount):
        return "-" in amount or amount.startswith("(")

    cn_rows = [row["AMOUNT"] for row, line in zip(export, lines) if line["charge_code"] == "CN"]
    negative = [a for a in cn_rows if written_negative(a)]
    assert 2 <= len(negative) <= 3
    assert any("-" in a for a in negative) and any(a.startswith("(") for a in negative)
    assert not any(written_negative(row["AMOUNT"]) for row, line in zip(export, lines) if line["charge_code"] != "CN")


DATE_FORMATS = {
    "2026/3/11": (r"\d{4}/\d{1,2}/\d{1,2}", "%Y/%m/%d"),
    "11-Mar-26": (r"\d{2}-[A-Z][a-z]{2}-\d{2}", "%d-%b-%y"),
    "20260311": (r"\d{8}", "%Y%m%d"),
    "2026.03.11": (r"\d{4}\.\d{2}\.\d{2}", "%Y.%m.%d"),
}


def test_invoice_dates_use_four_formats_evenly_and_parse_back(lines, export):
    used = Counter()
    for row, line in zip(export, lines):
        name, (pattern, fmt) = next((n, f) for n, f in DATE_FORMATS.items() if re.fullmatch(f[0], row["INV_DATE"]))
        assert datetime.strptime(row["INV_DATE"], fmt).date().isoformat() == line["invoice_date"]
        used[name] += 1
    assert all(n / len(lines) == pytest.approx(0.25, abs=0.03) for n in used.values())
    assert used.keys() == DATE_FORMATS.keys()
