import sys
import os
import csv
from pathlib import Path
from sqlmodel import Session, SQLModel

# 將 backend 目錄加入 sys.path，確保可以正確 import db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import engine, create_db_and_tables
from db.models import BillOfLading
from scripts.demo_bills import generate_bills_of_lading

# 乾淨原始資料：給運費帳產生器 (ticket 02) 與標準答案 (ticket 06) 使用，commit 進 repo
SOURCE_CSV = Path(__file__).resolve().parent.parent / "data" / "source" / "bills_of_lading.csv"


def write_source_csv(bills: list[dict]) -> None:
    SOURCE_CSV.parent.mkdir(parents=True, exist_ok=True)
    with SOURCE_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(bills[0].keys()))
        writer.writeheader()
        writer.writerows(bills)


def seed_data():
    bills = generate_bills_of_lading()
    write_source_csv(bills)

    # 重建資料表：會清掉既有提單與 bad_cases
    SQLModel.metadata.drop_all(engine)
    create_db_and_tables()

    with Session(engine) as session:
        for bill in bills:
            # Billed Amount 屬於運費帳 (ticket 02/03)，不進提單主表
            fields = {k: v for k, v in bill.items() if k != "billed_amount_usd"}
            session.add(BillOfLading(**fields, is_verified=True))
        session.commit()

    print(f"=== 匯入完成：{len(bills)} 筆提單；乾淨原始資料已寫入 {SOURCE_CSV} ===")


if __name__ == "__main__":
    seed_data()
