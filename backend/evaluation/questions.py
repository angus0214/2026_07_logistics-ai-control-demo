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


# ---- 驗證題 (ticket 07)：沒用過的多步計算題 ----
# 用來驗證「最後一句 SQL 必須單獨回答整個問題」規則（ADR-0008），以及 QB-2 暴露的「報價」弱點。
# 在看到規則上線後的結果之前就固定下來，不拿原本 20 題證明修好了。

def _billed_minus_quoted(bills) -> float:
    return round(sum(_billed(b["bl_number"]) - float(b["freight_cost"]) for b in bills), 2)


_oct_lines = _shipped_in("2026-10")
_sep_bills = _bills_shipped_in("2026-09")
_gap_by_month = {m: _billed_minus_quoted(_bills_shipped_in(m)) for m in ("2026-08", "2026-09", "2026-10")}

HOLDOUT_QUESTIONS = [
    Question("H-1", "多步：差額", "提單 EGLV31480004 的請款金額比報價運費多多少？",
             Number(round(_billed("EGLV31480004") - float(_bills["EGLV31480004"]["freight_cost"]), 2))),
    Question("H-2", "多步：差額", "2026 年 9 月開航的提單，請款總額比報價總額多多少？",
             Number(_billed_minus_quoted(_sep_bills))),
    Question("H-3", "多步：比例", "2026 年 10 月開航貨件的運費中，以台幣開立的費用占多少百分比？（例如 12.34）",
             Number(round(sum(line["usd"] for line in _oct_lines if line["currency"] == "TWD")
                          / sum(line["usd"] for line in _oct_lines) * 100, 2))),
    Question("H-4", "報價", "Nvidia Corp 2026 年 10 月開航提單的報價運費總額是多少？",
             Number(round(sum(float(b["freight_cost"]) for b in _bills_shipped_in("2026-10") if b["shipper"] == "Nvidia Corp"), 2))),
    Question("H-5", "報價", "2026 年 9 月開航的提單中，報價運費最高的是哪一張？",
             Value(max(_sep_bills, key=lambda b: float(b["freight_cost"]))["bl_number"])),
    Question("H-6", "多步：比較", "2026 年 8、9、10 月中，哪個月開航的貨件請款總額比報價總額多最多？請以 YYYY-MM 表示。",
             Value(max(_gap_by_month, key=_gap_by_month.get))),
]


# ---- 第二組驗證題 (ticket 10)：只驗證 09 的規則用詞 ----
# 09 之後 H 題組與原 20 題都已用過，不能再拿來證明修好了。這組在看到 09 的結果之前固定下來，
# 只考 09 要修的兩件事：只問一個總數時不要拆成明細；差額、比例要在同一句算好。
# 刻意避開「JOIN 後加總提單欄位」與「報價」：這兩個是已知限制（08 wontfix），不出題證明修好。

def _bill_count(lines) -> int:
    return len({line["bl_number"] for line in lines})


_sep_lines = _shipped_in("2026-09")
_validation_lines = {
    "V-1": _of("TSMC Export", _shipped_in("2026-08")),
    "V-2": _of("Apple Inc.", _sep_lines),
    "V-3": _of("Samsung Electronics", _shipped_in("2026-08") + _sep_lines + _oct_lines),
    "V-4": _sep_lines,
    "V-5": _of("Samsung Electronics", _sep_lines) + _of("TSMC Export", _sep_lines),
}
VALIDATION_BILL_COUNTS = {qid: _bill_count(lines) for qid, lines in _validation_lines.items()}

VALIDATION_QUESTIONS = [
    Question("V-1", "只問總數", "TSMC Export 2026 年 8 月開航貨件的運費是多少？",
             Number(_usd(_validation_lines["V-1"]))),
    Question("V-2", "只問總數", "Apple Inc. 2026 年 9 月開航貨件的運費總共多少？",
             Number(_usd(_validation_lines["V-2"]))),
    Question("V-3", "只問總數", "Samsung Electronics 在 2026 年 8 到 10 月開航的貨件，運費加起來是多少？",
             Number(_usd(_validation_lines["V-3"]))),
    Question("V-4", "只問總數", "2026 年 9 月開航的貨件，運費總額是多少？",
             Number(_usd(_validation_lines["V-4"]))),
    Question("V-5", "只問總數", "2026 年 9 月開航的貨件中，Samsung Electronics 和 TSMC Export 的運費合計是多少？",
             Number(_usd(_validation_lines["V-5"]))),
    Question("V-6", "同一句算好", "Apple Inc. 2026 年 10 月開航貨件的運費，減掉 2026 年 9 月的，差多少？",
             Number(round(_usd(_of("Apple Inc.", _oct_lines)) - _usd(_validation_lines["V-2"]), 2))),
    Question("V-7", "同一句算好", "2026 年 9 月開航貨件的運費中，Nvidia Corp 占多少百分比？（例如 12.34）",
             Number(round(_usd(_of("Nvidia Corp", _sep_lines)) / _usd(_sep_lines) * 100, 2))),
    Question("V-8", "同一句算好", "2026 年 9 月開航的貨件，Nvidia Corp 的運費比 TSMC Export 多多少？",
             Number(round(_usd(_of("Nvidia Corp", _sep_lines)) - _usd(_of("TSMC Export", _sep_lines)), 2))),
]
