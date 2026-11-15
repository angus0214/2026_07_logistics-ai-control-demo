"""Demo 用運費帳 (Freight Ledger)：先產生乾淨 Charge Line，再弄髒成財務匯出檔（ticket 02）。

固定 seed，每次產生結果都一樣（ADR-0006）。乾淨資料是標準答案的唯一來源。
"""
import csv
import os
import random
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from scripts.demo_bills import SHIPPERS, generate_bills_of_lading

SOURCE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"
CLEAN_CSV = SOURCE_DIR / "freight_ledger_clean.csv"    # 標準答案的來源（ticket 06）
EXPORT_CSV = SOURCE_DIR / "freight_ledger_export.csv"  # 「財務系統匯出檔」，03 原樣載入
ALIASES_CSV = SOURCE_DIR / "customer_aliases.csv"      # 03 的客戶別名表
FX_RATES_CSV = SOURCE_DIR / "fx_rates.csv"             # 03 的月匯率表

SEED = 20260802
CREDIT_NOTE_BL_COUNT = 7  # 約 15% 的提單有 Credit Note
UNMATCHED_LINE_COUNT = 7  # 營運系統沒有建檔的貨件：提單號對不上任何提單
BL_PREFIXES = ["EGLV", "YMLU", "ONEY", "MSCU", "HLXU"]

# 月匯率：每 1 USD 可換多少該幣別。key 是發票月份 (YYYY-MM)
FX_RATES = {
    "2026-08": {"USD": 1.0, "TWD": 32.40, "EUR": 0.92, "JPY": 147.00},
    "2026-09": {"USD": 1.0, "TWD": 32.10, "EUR": 0.91, "JPY": 149.50},
    "2026-10": {"USD": 1.0, "TWD": 31.80, "EUR": 0.93, "JPY": 151.20},
    "2026-11": {"USD": 1.0, "TWD": 31.95, "EUR": 0.94, "JPY": 152.80},
}
CURRENCY_WEIGHTS = {"USD": 0.60, "TWD": 0.25, "EUR": 0.10, "JPY": 0.05}
WHOLE_UNIT_CURRENCIES = {"TWD", "JPY"}  # 帳上不帶小數


def to_usd(amount: float, currency: str, invoice_date: str) -> float:
    """依發票月份匯率把原幣金額換成 USD（Billed Amount 的換算規則）。"""
    return amount / FX_RATES[invoice_date[:7]][currency]


def _from_usd(usd: float, currency: str, invoice_date: str) -> float:
    amount = usd * FX_RATES[invoice_date[:7]][currency]
    return round(amount) if currency in WHOLE_UNIT_CURRENCIES else round(amount, 2)


def _split_usd(rng: random.Random, target: float, codes: list[str]) -> dict[str, float]:
    """把目標請款金額拆給各費用；Credit Note 為負，其餘費用加總後扣掉它剛好等於目標。"""
    credit = target * rng.uniform(0.05, 0.15) if "CN" in codes else 0.0
    charges = target + credit
    split = {}
    if "THC" in codes:
        split["THC"] = charges * rng.uniform(0.08, 0.15)
    if "BAF" in codes:
        split["BAF"] = charges * rng.uniform(0.05, 0.12)
    split["OF"] = charges - sum(split.values())
    if credit:
        split["CN"] = -credit
    return split


def generate_charge_lines(bills: list[dict]) -> list[dict]:
    """乾淨 Charge Line：原幣金額（Credit Note 為負）、ISO 幣別、ISO 發票日。"""
    rng = random.Random(SEED)
    credit_note_bls = {bl["bl_number"] for bl in rng.sample(bills, CREDIT_NOTE_BL_COUNT)}
    lines = []
    for bl in bills:
        if bl["bl_number"] in credit_note_bls:
            codes = ["OF", "CN"] + rng.sample(["THC", "BAF"], rng.randint(0, 1))
        else:
            codes = ["OF"] + rng.sample(["THC", "BAF"], rng.choices([0, 1, 2], [2, 4, 4])[0])
        on_board = date.fromisoformat(bl["on_board_date"])
        for code, usd in _split_usd(rng, bl["target_billed_usd"], codes).items():
            invoice_date = on_board + timedelta(days=rng.randint(3, 20))
            lines.append({"bl_number": bl["bl_number"], "customer": bl["shipper"], "charge_code": code, "usd": usd, "invoice_date": invoice_date.isoformat()})
    lines += _unmatched_lines(rng, {bl["bl_number"] for bl in bills})

    # 幣別依比例精準分配，再換成原幣金額
    for line, currency in zip(lines, _currency_pool(rng, len(lines))):
        line["currency"] = currency
        line["amount"] = _from_usd(line.pop("usd"), currency, line["invoice_date"])
    # 財務系統依發票日匯出；(bl_number, charge_code) 是唯一鍵
    lines.sort(key=lambda line: (line["invoice_date"], line["bl_number"], line["charge_code"]))
    return lines


def _currency_pool(rng: random.Random, n: int) -> list[str]:
    counts = {cur: round(n * w) for cur, w in CURRENCY_WEIGHTS.items()}
    counts["USD"] += n - sum(counts.values())
    pool = [cur for cur, k in counts.items() for _ in range(k)]
    rng.shuffle(pool)
    return pool


def _unmatched_lines(rng: random.Random, known_bl_numbers: set[str]) -> list[dict]:
    lines = []
    while len(lines) < UNMATCHED_LINE_COUNT:
        bl_number = rng.choice(BL_PREFIXES) + "".join(str(rng.randint(0, 9)) for _ in range(8))
        if bl_number in known_bl_numbers or any(line["bl_number"] == bl_number for line in lines):
            continue
        invoice_date = date(2026, 8, 4) + timedelta(days=rng.randint(0, 88))
        lines.append({"bl_number": bl_number, "customer": rng.choice(SHIPPERS), "charge_code": "OF", "usd": rng.uniform(500, 6000), "invoice_date": invoice_date.isoformat()})
    return lines


EXPORT_SEED = 20260803
BL_VARIANT_SHARE = 0.15  # 提單號只差大小寫／空白／「-」，正規化後對得上

CUSTOMER_RENAME_SHARE = 0.40  # 客戶名不是標準寫法（含下面 2 筆 Unmapped）

# 別名 → 標準 Shipper 名稱；03 的客戶別名表就是這份
CUSTOMER_ALIASES = {
    "Apple Inc.": ["APPLE INC", "Apple Inc", "apple inc.", "蘋果"],
    "Tesla Logistics": ["TESLA LOGISTICS", "Tesla Logistic", "特斯拉物流"],
    "TSMC Export": ["TSMC", "tsmc export", "台積電"],
    "Foxconn Global": ["FOXCONN", "Hon Hai (Foxconn)", "鴻海"],
    "Samsung Electronics": ["SAMSUNG ELEC.", "Samsung Electronics Co.", "三星電子"],
    "Nvidia Corp": ["NVIDIA CORP", "NVIDIA Corporation", "輝達"],
    "ASUS Tek": ["ASUSTeK", "ASUS", "華碩"],
}
# 刻意不放進別名表的寫法（Unmapped Customer）→ 實際是哪個 Shipper，供標準答案使用
UNMAPPED_CUSTOMER_NAMES = {
    "Apple Taiwan Branch": "Apple Inc.",
    "TSMC Arizona": "TSMC Export",
}

# 金額欄：幣別混在字串裡，每種幣別有 3 種寫法
AMOUNT_FORMATS = {
    "USD": ["USD {:,.2f}", "US${:,.2f}", "{:.2f} usd"],
    "TWD": ["NT${:,.0f}", "TWD {:.0f}", "{:,.0f} twd"],
    "EUR": ["€{:,.2f}", "EUR {:.2f}", "{:.2f} eur"],
    "JPY": ["¥{:,.0f}", "JPY {:.0f}", "{:,.0f} jpy"],
}
MONTH_ABBR = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
# 發票日 4 種格式平均分布（不用 03/11/2026 這種月日分不清的寫法）
DATE_FORMATS = [
    lambda d: f"{d.year}/{d.month}/{d.day}",                          # 2026/3/11
    lambda d: f"{d.day:02d}-{MONTH_ABBR[d.month - 1]}-{d.year % 100:02d}",  # 11-Mar-26
    lambda d: f"{d.year}{d.month:02d}{d.day:02d}",                    # 20260311
    lambda d: f"{d.year}.{d.month:02d}.{d.day:02d}",                  # 2026.03.11
]
CREDIT_NOTE_MINUS_COUNT = 2  # 其餘 Credit Note 存正數，只靠 CN 代碼判斷
CREDIT_NOTE_PARENTHESES_COUNT = 1

BL_VARIANTS = [
    lambda bl: bl.lower(),
    lambda bl: f"{bl[:4]} {bl[4:]}",
    lambda bl: f"{bl[:4]}-{bl[4:]}",
    lambda bl: f" {bl} ",
    lambda bl: f"{bl[:4].lower()}-{bl[4:]}",
]


def _pick(rng: random.Random, n: int, share: float) -> set[int]:
    """精準挑出 share 比例的列號。"""
    return set(rng.sample(range(n), round(n * share)))


def dirty_export(lines: list[dict]) -> list[dict]:
    """把乾淨 Charge Line 弄髒成「財務系統匯出檔」：全是字串，第 i 列對應第 i 筆 Charge Line。"""
    rng = random.Random(EXPORT_SEED)
    bl_variant_rows = _pick(rng, len(lines), BL_VARIANT_SHARE)
    customer_names = _dirty_customer_names(rng, lines)
    amounts = _dirty_amounts(rng, lines)
    date_formats = [DATE_FORMATS[i % len(DATE_FORMATS)] for i in range(len(lines))]
    rng.shuffle(date_formats)
    return [
        {
            "BL_NO": rng.choice(BL_VARIANTS)(line["bl_number"]) if i in bl_variant_rows else line["bl_number"],
            "CUSTOMER": customer_names[i],
            "CHG_CODE": line["charge_code"],
            "AMOUNT": amounts[i],
            "INV_DATE": date_formats[i](date.fromisoformat(line["invoice_date"])),
        }
        for i, line in enumerate(lines)
    ]


def _dirty_customer_names(rng: random.Random, lines: list[dict]) -> list[str]:
    names = [line["customer"] for line in lines]
    renamed = set()
    for unmapped, shipper in UNMAPPED_CUSTOMER_NAMES.items():
        i = rng.choice([i for i, name in enumerate(names) if name == shipper and i not in renamed])
        names[i] = unmapped
        renamed.add(i)
    remaining = [i for i in range(len(lines)) if i not in renamed]
    for i in rng.sample(remaining, round(len(lines) * CUSTOMER_RENAME_SHARE) - len(renamed)):
        names[i] = rng.choice(CUSTOMER_ALIASES[names[i]])
    return names


def _dirty_amounts(rng: random.Random, lines: list[dict]) -> list[str]:
    amounts = [rng.choice(AMOUNT_FORMATS[line["currency"]]).format(abs(line["amount"])) for line in lines]
    credit_rows = [i for i, line in enumerate(lines) if line["charge_code"] == "CN"]
    signed = rng.sample(credit_rows, CREDIT_NOTE_MINUS_COUNT + CREDIT_NOTE_PARENTHESES_COUNT)
    for i in signed[:CREDIT_NOTE_MINUS_COUNT]:
        amounts[i] = re.sub(r"(\d)", r"-\g<1>", amounts[i], count=1)  # 「USD -500.00」
    for i in signed[CREDIT_NOTE_MINUS_COUNT:]:
        amounts[i] = f"({amounts[i]})"  # 會計括號表示負數
    return amounts


def _write_csv(path: Path, rows: list[dict]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


if __name__ == "__main__":
    lines = generate_charge_lines(generate_bills_of_lading())
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    _write_csv(CLEAN_CSV, lines)
    _write_csv(EXPORT_CSV, dirty_export(lines))
    # 別名表含標準名稱對應自己；UNMAPPED_CUSTOMER_NAMES 刻意不放
    _write_csv(ALIASES_CSV, [
        {"alias": alias, "shipper": shipper}
        for shipper, aliases in CUSTOMER_ALIASES.items()
        for alias in [shipper, *aliases]
    ])
    _write_csv(FX_RATES_CSV, [
        {"month": month, "currency": currency, "units_per_usd": rate}
        for month, rates in FX_RATES.items()
        for currency, rate in rates.items()
    ])
    print(f"已寫入 {len(lines)} 筆 Charge Line 與參考表：{SOURCE_DIR}")
