import base64
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from typing import Optional

# 定義一個專門給 LLM 輸出的 Pydantic Schema (隔離 DB 實體)
class OCRExtractionResult(BaseModel):
    bl_number: str = Field(description="提單號碼 (S/O NO. 或 B/L No.)，若無則填寫 'Unknown'")
    shipper: str = Field(description="託運人 (Shipper) 名稱，若無則填寫 'Unknown'")
    consignee: str = Field(description="收貨人 (Consignee) 名稱，若無則填寫 'Unknown'")
    destination: str = Field(description="目的地港口 (Port of Discharge / Place of Delivery)，若無則填寫 'Unknown'")
    gross_weight: float = Field(description="貨物總重 (Gross Weight KGS)，請提取數字，若無則回傳 0.0")
    eta: str = Field(description="預計抵達日期 (ETA) 或航班日期，若無則填寫 'Unknown'")
    confidence_score: int = Field(description="你對這份文件解析的整體信心度 (0-100)。如果圖片模糊或缺少關鍵欄位，請降低分數。")

from core.config import settings

def process_bill_of_lading_image(base64_image: str) -> OCRExtractionResult:
    """
    使用 OpenAI GPT-4o Vision 解析提單圖片，並強制回傳結構化資料。
    """
    llm = ChatOpenAI(model="gpt-4o", temperature=0, api_key=settings.OPENAI_API_KEY)
    structured_llm = llm.with_structured_output(OCRExtractionResult)
    
    prompt_text = "你是一位專業的物流報關專員。請詳細閱讀這張提單/裝貨單(Shipping Order/Bill of Lading)，並精準提取出以下欄位資訊。"
    
    message = HumanMessage(
        content=[
            {"type": "text", "text": prompt_text},
            {
                "type": "image_url",
                "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"},
            },
        ]
    )
    
    # 呼叫 LLM
    result = structured_llm.invoke([message])
    return result
