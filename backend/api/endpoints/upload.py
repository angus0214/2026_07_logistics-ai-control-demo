from fastapi import APIRouter, UploadFile, File, HTTPException
import base64
from services.ocr_service import process_bill_of_lading_image
from db.models import BillOfLading
from db.database import get_session
from fastapi import Depends
from sqlmodel import Session, select

router = APIRouter()

@router.post("/upload_bl")
async def upload_bill_of_lading(file: UploadFile = File(...)):
    """
    接收前端上傳的圖片檔，打入 OpenAI Vision 進行 OCR 解析。
    此步驟僅回傳預覽資料，不寫入資料庫。
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="請上傳圖片檔 (JPEG/PNG)")
    
    # 將圖片轉為 Base64
    contents = await file.read()
    base64_image = base64.b64encode(contents).decode('utf-8')
    
    try:
        # 呼叫 LangChain Service
        ocr_result = process_bill_of_lading_image(base64_image)
        return {
            "status": "success",
            "message": "AI 解析成功，請等待人工覆核。",
            "data": ocr_result.model_dump()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OCR 解析失敗: {str(e)}")

from pydantic import BaseModel
import json

class SaveBillOfLadingRequest(BaseModel):
    data: dict
    is_bad_case: bool = False
    ai_raw_output: dict | None = None
    image_base64: str | None = None

@router.post("/save_bl")
def save_bill_of_lading(request: SaveBillOfLadingRequest, session: Session = Depends(get_session)):
    """
    前端人工覆核確認後，將最終資料寫入 SQLite。
    若被判定為 Bad Case (有修改過)，一併存入 BadCaseFeedback。
    """
    try:
        # 將前端傳來的 JSON 轉為 SQLModel 物件
        bl_record = BillOfLading(**request.data)
        bl_record.is_verified = True  # 標記為已覆核
        
        session.add(bl_record)
        session.commit()
        session.refresh(bl_record)
        
        # 處理 Bad Case
        if request.is_bad_case and request.image_base64 and request.ai_raw_output:
            from db.models import BadCaseFeedback
            bad_case = BadCaseFeedback(
                bl_id=bl_record.id,
                image_base64=request.image_base64,
                ai_raw_output=json.dumps(request.ai_raw_output, ensure_ascii=False),
                human_corrected_output=json.dumps(request.data, ensure_ascii=False)
            )
            session.add(bad_case)
            session.commit()
        
        return {"status": "success", "id": bl_record.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"寫入資料庫失敗: {str(e)}")

@router.get("/bl_list")
def get_bill_of_lading_list(session: Session = Depends(get_session)):
    """
    取得所有提單列表，供戰情室 Dashboard 顯示。
    """
    statement = select(BillOfLading).order_by(BillOfLading.created_at.desc())
    results = session.exec(statement).all()
    return results

@router.get("/bad_cases")
def get_bad_cases_list(session: Session = Depends(get_session)):
    """
    取得所有 Bad Case 列表，供資料飛輪與工程團隊檢視。
    """
    from db.models import BadCaseFeedback
    statement = select(BadCaseFeedback).order_by(BadCaseFeedback.created_at.desc())
    results = session.exec(statement).all()
    return results
