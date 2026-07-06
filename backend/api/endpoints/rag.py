from fastapi import APIRouter
from pydantic import BaseModel
from services.rag_service import get_rag_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat/op_rag")
def op_rag_chat(request: ChatRequest):
    """
    接收前端發送的問題，呼叫 RAG 引擎從 PDF 文件中檢索答案並回傳。
    """
    try:
        answer = get_rag_response(request.message)
        return {"reply": answer}
    except Exception as e:
        return {"reply": f"AI 助理發生錯誤: {str(e)}"}
