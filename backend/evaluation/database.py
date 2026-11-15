"""評估用資料庫：剛 seed 好、內容固定的獨立 SQLite 檔，不碰 demo 用的 DB（ADR-0006）。"""
from pathlib import Path

from sqlmodel import Session, SQLModel, create_engine

from db.freight_ledger import load_freight_ledger
from db.models import BillOfLading
from scripts.demo_bills import generate_bills_of_lading


def build_eval_db(path: Path) -> None:
    """在 path 建一份全新的評估資料庫：01 的固定提單＋02/03 的運費帳與 view。已存在就整個換掉。"""
    path = Path(path)
    path.unlink(missing_ok=True)
    engine = create_engine(f"sqlite:///{path.as_posix()}")
    try:
        SQLModel.metadata.create_all(engine)
        with Session(engine) as session:
            for bill in generate_bills_of_lading():
                session.add(BillOfLading(**{k: v for k, v in bill.items() if k != "target_billed_usd"}, is_verified=True))
            session.commit()
        load_freight_ledger(engine)
    finally:
        engine.dispose()
