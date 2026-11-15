"""模型能用預設的 created_at 寫進資料庫（sqlmodel 0.0.50 起，datetime 必須帶時區）。"""
import pytest
from sqlmodel import Session, SQLModel, create_engine, select
from sqlalchemy.pool import StaticPool

from db.models import BadCaseFeedback, BillOfLading


@pytest.fixture
def session():
    engine = create_engine("sqlite://", connect_args={"check_same_thread": False}, poolclass=StaticPool)
    SQLModel.metadata.create_all(engine)
    with Session(engine) as s:
        yield s


def test_bill_of_lading_saves_with_default_created_at(session):
    session.add(BillOfLading(
        bl_number="EGLV12345678", shipper="Apple Inc.", consignee="BestBuy US",
        destination="USLAX (Los Angeles)", gross_weight=1000.0, on_board_date="2026-09-01",
    ))
    session.commit()

    saved = session.exec(select(BillOfLading)).one()
    assert saved.bl_number == "EGLV12345678"
    assert saved.created_at is not None


def test_bad_case_saves_with_default_created_at(session):
    bl = BillOfLading(
        bl_number="EGLV12345678", shipper="Apple Inc.", consignee="BestBuy US",
        destination="USLAX (Los Angeles)", gross_weight=1000.0, on_board_date="2026-09-01",
    )
    session.add(bl)
    session.commit()
    session.add(BadCaseFeedback(
        bl_id=bl.id, ai_raw_output="{}", human_corrected_output="{}", image_base64="",
    ))
    session.commit()

    saved = session.exec(select(BadCaseFeedback)).one()
    assert saved.bl_id == bl.id
    assert saved.created_at is not None
