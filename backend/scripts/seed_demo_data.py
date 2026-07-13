import sys
import os
import random
from datetime import datetime, timedelta
from sqlmodel import Session, SQLModel

# 將 backend 目錄加入 sys.path，確保可以正確 import db
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from db.database import engine, create_db_and_tables
from db.models import BillOfLading

# 假資料維度
SHIPPERS = ["Apple Inc.", "Tesla Logistics", "TSMC Export", "Foxconn Global", "Samsung Electronics", "Nvidia Corp", "ASUS Tek"]
CONSIGNEES = ["BestBuy US", "Walmart Central", "Amazon FBA", "MediaMarkt EU", "Target Stores", "Sony Interactive"]
DESTINATIONS = ["USLAX (Los Angeles)", "JPTYO (Tokyo)", "SGSIN (Singapore)", "NLRTM (Rotterdam)", "DEHAM (Hamburg)", "UKLHR (London)"]

def generate_random_date():
    start_date = datetime.now()
    # Generate dates in the past 10 to 90 days
    random_days = random.randint(10, 90)
    return (start_date - timedelta(days=random_days)).strftime("%Y-%m-%d")

def generate_fake_bl_number():
    prefix = random.choice(["EGLV", "YMLU", "ONEY", "MSCU", "HLXU"])
    number = "".join([str(random.randint(0, 9)) for _ in range(8)])
    return f"{prefix}{number}"

def seed_data():
    # Drop existing tables to recreate schema
    SQLModel.metadata.drop_all(engine)
    # 確保資料表已建立 (會自動連線 logistics.db)
    create_db_and_tables()

    with Session(engine) as session:
        # 清空舊資料
        # 注意: 這是 SQLite，直接刪除或 drop table 最快，但這裡我們只是簡單刪除所有紀錄
        existing = session.query(BillOfLading).all()
        for e in existing:
            session.delete(e)
        session.commit()

        print("=== 開始匯入 50 筆火力展示用假提單資料 ===")
        
        for _ in range(50):
            volume = round(random.uniform(5.0, 65.0), 2)
            # 依據體積推算運費，加入隨機波動，讓 SQL 計算有高有低
            base_freight = volume * random.uniform(80, 150)
            freight_cost = round(base_freight, 2)
            gross_weight = round(volume * random.uniform(100, 300), 2)
            
            bl = BillOfLading(
                bl_number=generate_fake_bl_number(),
                shipper=random.choice(SHIPPERS),
                consignee=random.choice(CONSIGNEES),
                destination=random.choice(DESTINATIONS),
                gross_weight=gross_weight,
                volume=volume,
                freight_cost=freight_cost,
                on_board_date=generate_random_date(),
                confidence_score=random.randint(85, 100),
                is_verified=True,
                verified_by="System (Seeder)",
                ai_raw_output='{"status": "simulated"}',
                image_base64=None
            )
            session.add(bl)

        session.commit()
        print("=== 匯入完成！資料庫中已有 50 筆帶有體積與運費的 B/L 紀錄 ===")

if __name__ == "__main__":
    seed_data()
