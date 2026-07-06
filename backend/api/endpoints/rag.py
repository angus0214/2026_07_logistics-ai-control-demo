from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.rag_service import get_rag_response, stream_rag_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat/op_rag")
def op_rag_chat(request: ChatRequest):
    """
    接收前端發送的問題，呼叫 RAG 引擎從 PDF 文件中檢索答案並回傳串流資料。
    """
    try:
        # 使用 text/plain 讓前端 fetch 可以單純地接收字串碎片
        return StreamingResponse(
            stream_rag_response(request.message), 
            media_type="text/plain"
        )
    except Exception as e:
        return {"reply": f"AI 助理發生錯誤: {str(e)}"}
