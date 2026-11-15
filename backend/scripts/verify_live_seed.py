"""比對部署環境的提單資料與 repo 內的乾淨原始資料 CSV。

在 Render 上跑完 seed_demo_data.py 後，於本機執行，確認線上資料與 CSV 一筆一筆一致：

    python scripts/verify_live_seed.py                      # 預設比對 Render 後端
    python scripts/verify_live_seed.py http://localhost:8000  # 比對本機後端

一致時 exit code 為 0，否則為 1。
"""
import csv
import json
import sys
import urllib.request
from pathlib import Path

DEFAULT_BASE_URL = "https://logistics-ai-backend-nuhv.onrender.com"
SOURCE_CSV = Path(__file__).resolve().parent.parent / "data" / "source" / "bills_of_lading.csv"
FIELDS = ["bl_number", "shipper", "consignee", "destination", "gross_weight", "volume", "freight_cost", "on_board_date", "confidence_score"]
FLOAT_FIELDS = {"gross_weight", "volume", "freight_cost"}


def row_key(row: dict) -> tuple:
    return tuple(str(float(row[f])) if f in FLOAT_FIELDS else str(row[f]) for f in FIELDS)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")  # Windows 主控台預設 cp950 印不出 ✅
    base_url = (sys.argv[1] if len(sys.argv) > 1 else DEFAULT_BASE_URL).rstrip("/")

    with urllib.request.urlopen(f"{base_url}/api/bl_list", timeout=60) as resp:
        online = json.load(resp)
    with SOURCE_CSV.open(encoding="utf-8") as f:
        expected = list(csv.DictReader(f))

    online_keys = {row_key(r) for r in online}
    expected_keys = {row_key(r) for r in expected}
    missing = expected_keys - online_keys
    extra = online_keys - expected_keys
    expected_total = round(sum(float(r["freight_cost"]) for r in expected), 2)

    print(f"比對對象：{base_url}")
    print(f"線上提單數：{len(online)}（預期 {len(expected)}）")
    print(f"總 Quoted Freight：{round(sum(r['freight_cost'] for r in online), 2)}（預期 {expected_total}）")
    print(f"CSV 有、線上沒有：{len(missing)}；線上有、CSV 沒有：{len(extra)}")
    for k in list(missing)[:5]:
        print("  缺少：", k)
    for k in list(extra)[:5]:
        print("  多出：", k)

    ok = len(online) == len(expected) and not missing and not extra
    print("✅ 線上資料與 CSV 完全一致" if ok else "❌ 不一致")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
