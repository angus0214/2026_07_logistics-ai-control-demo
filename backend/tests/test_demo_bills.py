"""固定 seed 的提單乾淨原始資料（ticket 01、ADR-0006）。"""
import re

from scripts.demo_bills import generate_bills_of_lading


def test_same_data_every_run():
    assert generate_bills_of_lading() == generate_bills_of_lading()


def test_fifty_bills_of_lading():
    assert len(generate_bills_of_lading()) == 50


def test_on_board_dates_are_absolute_and_span_aug_to_oct_2026():
    dates = [bl["on_board_date"] for bl in generate_bills_of_lading()]
    assert all("2026-08-01" <= d <= "2026-10-31" for d in dates)
    # 三個月都要有資料，評估題才能問「8 月」「9 月」「10 月」
    assert {d[:7] for d in dates} == {"2026-08", "2026-09", "2026-10"}


def test_bl_numbers_keep_carrier_prefix_format_and_are_unique():
    numbers = [bl["bl_number"] for bl in generate_bills_of_lading()]
    assert all(re.fullmatch(r"(EGLV|YMLU|ONEY|MSCU|HLXU)\d{8}", n) for n in numbers)
    # B/L Number 是運費帳對帳的唯一鍵，不能重複
    assert len(set(numbers)) == len(numbers)


def test_quoted_freight_is_75_to_90_percent_of_billed_except_a_few_underquoted():
    ratios = [bl["freight_cost"] / bl["target_billed_usd"] for bl in generate_bills_of_lading()]
    underquoted = [r for r in ratios if r < 0.5]
    normal = [r for r in ratios if r >= 0.5]
    # 刻意放 3–4 張「請款遠超報價」的異常，供評估題「哪幾張請款遠超報價」
    assert 3 <= len(underquoted) <= 4
    assert all(0.75 <= r <= 0.90 for r in normal)
