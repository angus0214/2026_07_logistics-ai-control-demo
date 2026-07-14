from fastapi import APIRouter
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from services.rag_service import get_rag_response, stream_rag_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat/op_rag", response_model=None)
def op_rag_chat(request: ChatRequest) -> StreamingResponse | dict:
    """
    接收前端發送的問題，呼叫 RAG 引擎從 PDF 文件中檢索答案並回傳。
    
    本端點使用 text/plain 回傳 StreamingResponse，讓前端可以簡單地透過 Fetch API
    接收連續的字串碎片，達成打字機效果。
    
    Args:
        request (ChatRequest): 包含使用者提問內容的請求物件。
        
    Returns:
        StreamingResponse | dict: 成功時回傳純文字串流 (StreamingResponse)；
                                 失敗時回傳包含錯誤訊息的字典 (dict)。
    """
    try:
        # 使用 text/plain 讓前端 fetch 可以單純地接收字串碎片
        headers = {
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no"
        }
        return StreamingResponse(
            stream_rag_response(request.message), 
            media_type="text/plain",
            headers=headers
        )
    except Exception as e:
        return {"reply": f"AI 助理發生錯誤: {str(e)}"}
