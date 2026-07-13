from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import datetime

class BillOfLading(SQLModel, table=True):
    __tablename__ = "bills_of_lading"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    bl_number: str = Field(index=True, description="提單號碼 (B/L No.)")
    shipper: str = Field(description="託運人")
    consignee: str = Field(description="收貨人")
    destination: str = Field(description="目的地港口")
    gross_weight: float = Field(description="貨物總重 (公斤)")
    volume: float = Field(default=0.0, description="體積 (CBM)")
    freight_cost: float = Field(default=0.0, description="運費")
    eta: str = Field(description="預計抵達日期")
    confidence_score: int = Field(default=100, description="AI 萃取信心度 (0-100)")
    is_verified: bool = Field(default=False, description="是否已由人工覆核確認")
    created_at: datetime = Field(default_factory=datetime.utcnow)

class BadCaseFeedback(SQLModel, table=True):
    __tablename__ = "bad_cases"
    
    id: Optional[int] = Field(default=None, primary_key=True)
    bl_id: int = Field(foreign_key="bills_of_lading.id", description="關聯的提單ID")
    ai_raw_output: str = Field(description="AI 原始預測的 JSON 字串")
    human_corrected_output: str = Field(description="人員手動修正後的 JSON 字串")
    modified_fields: str = Field(default="[]", description="被修改的欄位清單 (JSON 字串陣列)")
    image_base64: str = Field(description="提單原始圖片的 Base64")
    created_at: datetime = Field(default_factory=datetime.utcnow, description="建立時間")
