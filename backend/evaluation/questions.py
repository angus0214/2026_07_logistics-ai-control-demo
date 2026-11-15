"""評估集 (Eval Set)：20 題老闆式提問與標準答案 (Gold Answer)。

標準答案一律從弄髒之前的乾淨原始資料算出（bills_of_lading.csv、freight_ledger_clean.csv、
fx_rates.csv），絕不從整理過的 view 查，否則等於讓 view 自己幫自己打分數（ADR-0006）。
題目一律寫明確月份。每題標註主要考的陷阱；Raw 組的同一題常同時碰到多個陷阱。
"""
import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

from evaluation.scoring import Gold, Number, Pairs, Value

SOURCE_DIR = Path(__file__).resolve().parent.parent / "data" / "source"


@dataclass(frozen=True)
class Question:
    qid: str
    trap: str
    text: str
    gold: Gold


def _read(name: str) -> list[dict]:
    with (SOURCE_DIR / name).open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


_bills = {b["bl_number"]: b for b in _read("bills_of_lading.csv")}
_rates = {(r["month"], r["currency"]): float(r["units_per_usd"]) for r in _read("fx_rates.csv")}
_lines = _read("freight_ledger_clean.csv")
for _line in _lines:
    _line["usd"] = float(_line["amount"]) / _rates[(_line["invoice_date"][:7], _line["currency"])]
    _line["on_board_date"] = _bills[_line["bl_number"]]["on_board_date"] if _line["bl_number"] in _bills else None


def _usd(lines) -> float:
    return round(sum(line["usd"] for line in lines), 2)


def _shipped_in(month: str) -> list[dict]:
    """依開航日歸月的 Charge Line；對不上提單的列沒有開航日，不屬於任何月份。"""
    return [line for line in _lines if line["on_board_date"] and line["on_board_date"].startswith(month)]


def _of(customer: str, lines) -> list[dict]:
    return [line for line in lines if line["customer"] == customer]


def _bills_shipped_in(month: str) -> list[dict]:
    return [b for b in _bills.values() if b["on_board_date"].startswith(month)]


def _billed(bl_number: str) -> float:
    return sum(line["usd"] for line in _lines if line["bl_number"] == bl_number)


def _per_customer(lines) -> dict[str, float]:
    totals = defaultdict(float)
    for line in lines:
        totals[line["customer"]] += line["usd"]
    return {customer: round(total, 2) for customer, total in totals.items()}


_aug_bills = _bills_shipped_in("2026-08")
_most_over_quoted = max(_aug_bills, key=lambda b: _billed(b["bl_number"]) - float(b["freight_cost"]))
_busiest_port = Counter(b["destination"] for b in _bills.values()).most_common(1)[0][0]

QUESTIONS = [
    # ---- Credit Note ----
    Question("CN-1", "Credit Note", "Nvidia Corp 2026 年 9 月開航貨件的運費是多少？",
             Number(_usd(_of("Nvidia Corp", _shipped_in("2026-09"))))),
    Question("CN-2", "Credit Note", "2026 年 10 月開航的貨件，沖銷 (Credit Note) 總共多少？",
             Number(_usd(line for line in _shipped_in("2026-10") if line["charge_code"] == "CN"))),
    # ---- 多幣別 ----
    Question("FX-1", "多幣別", "2026 年 8 月開航的貨件中，以台幣開立的費用換算成美元是多少？",
             Number(_usd(line for line in _shipped_in("2026-08") if line["currency"] == "TWD"))),
    Question("FX-2", "多幣別", "Samsung Electronics 2026 年 10 月開航貨件的運費是多少美元？",
             Number(_usd(_of("Samsung Electronics", _shipped_in("2026-10"))))),
    # ---- 客戶別名 ----
    Question("AL-1", "客戶別名", "Foxconn Global 2026 年 10 月開航貨件的運費是多少？",
             Number(_usd(_of("Foxconn Global", _shipped_in("2026-10"))))),
    Question("AL-2", "客戶別名", "ASUS Tek 2026 年 9 月開航貨件的運費是多少？",
             Number(_usd(_of("ASUS Tek", _shipped_in("2026-09"))))),
    # ---- Unmatched（沒指定期間的總額要含系統外貨件）----
    Question("UM-1", "Unmatched", "Tesla Logistics 一共被請款多少錢？",
             Number(_usd(_of("Tesla Logistics", _lines)))),
    Question("UM-2", "Unmatched", "運費帳裡有幾筆費用對不上任何提單？",
             Number(sum(1 for line in _lines if line["on_board_date"] is None))),
    # ---- 開航日 vs 發票日 ----
    Question("PD-1", "開航日 vs 發票日", "2026 年 11 月開立的發票總金額是多少？",
             Number(_usd(line for line in _lines if line["invoice_date"].startswith("2026-11")))),
    Question("PD-2", "開航日 vs 發票日", "2026 年 10 月各客戶的運費分別是多少？",
             Pairs(_per_customer(_shipped_in("2026-10")))),
    # ---- 報價 vs 請款 ----
    Question("QB-1", "報價 vs 請款", "2026 年 8 月開航的提單中，請款金額比報價運費高出最多的是哪一張？",
             Value(_most_over_quoted["bl_number"])),
    Question("QB-2", "報價 vs 請款", "2026 年 10 月開航提單的報價運費總額是多少？",
             Number(round(sum(float(b["freight_cost"]) for b in _bills_shipped_in("2026-10")), 2))),
    # ---- 提單號正規化（這兩張在財務匯出檔裡的寫法都對不上原樣）----
    Question("BL-1", "提單號正規化", "提單 MSCU25271972 的運費是多少？",
             Number(round(_billed("MSCU25271972"), 2))),
    Question("BL-2", "提單號正規化", "提單 YMLU98988798 的請款金額比報價運費多多少？",
             Number(round(_billed("YMLU98988798") - float(_bills["YMLU98988798"]["freight_cost"]), 2))),
    # ---- 對照題：只查提單主表，三組都應該答對 ----
    Question("CT-1", "對照題", "2026 年 9 月開航的提單有幾張？",
             Number(len(_bills_shipped_in("2026-09")))),
    Question("CT-2", "對照題", "2026 年 10 月運往 USLAX 的貨物總重量是多少公斤？",
             Number(round(sum(float(b["gross_weight"]) for b in _bills_shipped_in("2026-10") if "USLAX" in b["destination"]), 2))),
    Question("CT-3", "對照題", "哪個目的地港口的提單最多？",
             Value(_busiest_port)),
    Question("CT-4", "對照題", "Foxconn Global 在 2026 年 8 到 10 月一共出了幾張提單？",
             Number(sum(1 for b in _bills.values() if b["shipper"] == "Foxconn Global"))),
    Question("CT-5", "對照題", "2026 年 8 月開航提單的總體積是多少 CBM？",
             Number(round(sum(float(b["volume"]) for b in _aug_bills), 2))),
    Question("CT-6", "對照題", "AI 萃取信心度低於 90 的提單有幾張？",
             Number(sum(1 for b in _bills.values() if int(b["confidence_score"]) < 90))),
]
