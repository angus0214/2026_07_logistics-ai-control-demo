from fastapi import APIRouter, UploadFile, File, HTTPException
import base64
from services.ocr_service import process_bill_of_lading_image
from db.models import BillOfLading
from db.database import get_session
from fastapi import Depends
from sqlmodel import Session, select

router = APIRouter()

@router.post("/upload_bl")
async def upload_bill_of_lading(file: UploadFile = File(...)) -> dict:
    """
    接收前端上傳的圖片檔，打入 OpenAI Vision 進行 OCR 解析。
    
    此步驟僅回傳預覽資料，不寫入資料庫。
    
    Args:
        file (UploadFile): 前端上傳的圖片檔案 (必須為 JPEG/PNG 格式)。
        
    Returns:
        dict: 包含解析狀態、訊息與解析出來的 OCR 資料。
        
    Raises:
        HTTPException: 若檔案格式不符或 OCR 解析發生錯誤時拋出。
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
    modified_fields: list[str] | None = None

@router.post("/save_bl")
def save_bill_of_lading(request: SaveBillOfLadingRequest, session: Session = Depends(get_session)) -> dict:
    """
    前端人工覆核確認後，將最終資料寫入 SQLite。
    
    若資料被判定為 Bad Case (曾被人工修改過)，將會一併把原始圖片與 AI 原始輸出存入 BadCaseFeedback 資料表，供後續資料飛輪與模型微調使用。
    
    Args:
        request (SaveBillOfLadingRequest): 包含覆核後資料、是否為 Bad Case 以及 AI 原始輸出的請求物件。
        session (Session): SQLModel 的資料庫 Session。
        
    Returns:
        dict: 包含儲存狀態與新增的提單 ID。
        
    Raises:
        HTTPException: 若寫入資料庫失敗時拋出 400 錯誤。
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
                human_corrected_output=json.dumps(request.data, ensure_ascii=False),
                modified_fields=json.dumps(request.modified_fields, ensure_ascii=False) if request.modified_fields else "[]"
            )
            session.add(bad_case)
            session.commit()
        
        return {"status": "success", "id": bl_record.id}
    except Exception as e:
        session.rollback()
        raise HTTPException(status_code=400, detail=f"寫入資料庫失敗: {str(e)}")

@router.get("/bl_list")
def get_bill_of_lading_list(session: Session = Depends(get_session)) -> list[BillOfLading]:
    """
    取得所有提單列表。
    
    供戰情室 Dashboard 顯示歷史提單紀錄，按照建立時間反向排序。
    
    Args:
        session (Session): SQLModel 的資料庫 Session。
        
    Returns:
        list[BillOfLading]: 提單紀錄列表。
    """
    statement = select(BillOfLading).order_by(BillOfLading.created_at.desc())
    results = session.exec(statement).all()
    return results

@router.get("/bad_cases")
def get_bad_cases_list(session: Session = Depends(get_session)) -> list:
    """
    取得所有 Bad Case 列表。
    
    供資料飛輪與工程團隊檢視系統的判斷盲區，按照建立時間反向排序。
    
    Args:
        session (Session): SQLModel 的資料庫 Session。
        
    Returns:
        list: Bad Case 紀錄列表。
    """
    from db.models import BadCaseFeedback
    statement = select(BadCaseFeedback).order_by(BadCaseFeedback.created_at.desc())
    results = session.exec(statement).all()
    return results
