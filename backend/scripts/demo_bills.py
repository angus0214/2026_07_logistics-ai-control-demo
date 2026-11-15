"""Demo 用提單的乾淨原始資料：固定 seed，每次產生結果都一樣（ADR-0006）。"""
import random
from datetime import date, timedelta

SEED = 20260801
BL_COUNT = 50
UNDERQUOTED_COUNT = 4  # Quoted 不到 Billed 一半的異常提單

SHIPPERS = ["Apple Inc.", "Tesla Logistics", "TSMC Export", "Foxconn Global", "Samsung Electronics", "Nvidia Corp", "ASUS Tek"]
CONSIGNEES = ["BestBuy US", "Walmart Central", "Amazon FBA", "MediaMarkt EU", "Target Stores", "Sony Interactive"]
DESTINATIONS = ["USLAX (Los Angeles)", "JPTYO (Tokyo)", "SGSIN (Singapore)", "NLRTM (Rotterdam)", "DEHAM (Hamburg)", "UKLHR (London)"]
FIRST_ON_BOARD_DATE = date(2026, 8, 1)
LAST_ON_BOARD_DATE = date(2026, 10, 31)
BL_PREFIXES = ["EGLV", "YMLU", "ONEY", "MSCU", "HLXU"]


def generate_bills_of_lading() -> list[dict]:
    rng = random.Random(SEED)
    underquoted = set(rng.sample(range(BL_COUNT), UNDERQUOTED_COUNT))
    bills = []
    for i in range(BL_COUNT):
        volume = round(rng.uniform(5.0, 65.0), 2)
        # 先決定 Billed Amount，再反推 Quoted Freight（ticket 01）
        billed = round(volume * rng.uniform(90, 170), 2)
        quote_ratio = rng.uniform(0.30, 0.45) if i in underquoted else rng.uniform(0.75, 0.90)
        bills.append({
            "bl_number": rng.choice(BL_PREFIXES) + "".join(str(rng.randint(0, 9)) for _ in range(8)),
            "shipper": rng.choice(SHIPPERS),
            "consignee": rng.choice(CONSIGNEES),
            "destination": rng.choice(DESTINATIONS),
            "gross_weight": round(volume * rng.uniform(100, 300), 2),
            "volume": volume,
            "freight_cost": round(billed * quote_ratio, 2),
            "billed_amount_usd": billed,
            "on_board_date": (FIRST_ON_BOARD_DATE + timedelta(days=rng.randint(0, (LAST_ON_BOARD_DATE - FIRST_ON_BOARD_DATE).days))).isoformat(),
            "confidence_score": rng.randint(85, 100),
        })
    return bills
