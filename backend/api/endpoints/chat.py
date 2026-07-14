import json
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from db.database import engine
from services.sql_agent_service import stream_sql_agent

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/boss_sql", response_model=None)
async def chat_boss_sql(request: ChatRequest) -> StreamingResponse:
    """
    接收 Boss Dashboard 的自然語言提問，並透過 SSE (Server-Sent Events) 串流回傳思考軌跡與最終答案。
    
    此端點整合了 SQL Agent 服務，會即時回傳 Agent 的思考過程 (thought) 與最終答案 (answer)。
    
    Args:
        request (ChatRequest): 包含使用者提問內容的請求物件。
        
    Returns:
        StreamingResponse: SSE 格式的字串流，每一段資料遵循 `data: {JSON}\n\n` 的格式。
    """
    async def sse_generator():
        try:
            # 呼叫我們剛剛寫好且通過測試的大腦 (stream_sql_agent)
            generator = stream_sql_agent(request.message, engine)
            
            async for chunk in generator:
                # 轉化為標準的 Server-Sent Events 格式 (data: {JSON}\n\n)
                yield f"data: {json.dumps(chunk, ensure_ascii=False)}\n\n"
        except Exception as e:
            # 錯誤處理機制
            error_chunk = {"event": "thought", "data": f"發生錯誤: {str(e)}"}
            yield f"data: {json.dumps(error_chunk, ensure_ascii=False)}\n\n"

    headers = {
        "Cache-Control": "no-cache",
        "Connection": "keep-alive",
        "X-Accel-Buffering": "no"
    }
    return StreamingResponse(sse_generator(), media_type="text/event-stream", headers=headers)
