import pytest
from fastapi.testclient import TestClient
from main import app

# 建立 FastAPI 測試客戶端
client = TestClient(app)

def test_boss_sql_endpoint_returns_sse_stream():
    """測試 /api/chat/boss_sql 是否有正確回傳 SSE (Server-Sent Events) 格式"""
    
    # 由於我們尚未在 main.py 掛載這個 router，這裡會得到 404，測試亮紅燈
    response = client.post(
        "/api/chat/boss_sql",
        json={"message": "總運費多少"}
    )
    
    # 驗證 HTTP 狀態碼
    assert response.status_code == 200, "API 應該要能正常連線"
    
    # 驗證 Header 的 Content-Type 必須是 text/event-stream
    assert "text/event-stream" in response.headers.get("content-type", ""), "必須以 SSE 格式回傳"
    
    # 簡單驗證內容有遵循 SSE 格式 (data: {JSON})
    content = response.content.decode("utf-8")
    assert "data: " in content, "必須包含 SSE 的 data 前綴"
