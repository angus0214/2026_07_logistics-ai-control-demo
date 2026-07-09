import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.pool import StaticPool

# 由於我們還沒實作 sql_agent_service，這裡的 import 會直接拋出 ImportError (標準的紅燈)
from services.sql_agent_service import stream_sql_agent

@pytest.fixture
def mock_db_engine():
    """建立一個只存在於記憶體中的乾淨資料庫，用於隔離測試"""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool
    )
    with engine.connect() as conn:
        conn.execute(text("""
            CREATE TABLE bills_of_lading (
                id INTEGER PRIMARY KEY,
                bl_number TEXT,
                carrier TEXT,
                freight_cost REAL
            )
        """))
        conn.execute(text("""
            INSERT INTO bills_of_lading (bl_number, carrier, freight_cost) 
            VALUES ('BL123', 'EVA Air', 500.0)
        """))
        conn.commit()
    return engine

@pytest.mark.asyncio
async def test_agent_generates_correct_sql_and_summary(mock_db_engine):
    # Act: 餵給 Agent 自然語言與我們的假資料庫
    generator = stream_sql_agent("請問總運費是多少？", mock_db_engine)
    
    events = []
    async for chunk in generator:
        events.append(chunk)
        
    # Assert 1: 驗證「透明化思考過程」是否存在
    thoughts = [e for e in events if e.get("event") == "thought"]
    assert len(thoughts) > 0, "Agent 必須產出至少一個思考軌跡 (例如執行了什麼 SQL)"
    
    # Assert 2: 驗證最終結果是否精準抓到 500 這個數字
    final_message = events[-1]
    assert final_message.get("event") == "message"
    assert "500" in final_message.get("data", "")
