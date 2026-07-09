import os
from typing import AsyncGenerator
from langchain_community.utilities import SQLDatabase
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv

load_dotenv()

async def stream_sql_agent(query: str, engine) -> AsyncGenerator[dict, None]:
    """
    接收自然語言查詢與 SQLAlchemy Engine，透過 LangChain SQL Agent 分析並串流回傳過程。
    """
    # 根據 PRD 的資安規範：使用白名單嚴格限制只能存取 bills_of_lading
    db = SQLDatabase(engine, include_tables=["bills_of_lading"])
    
    # 建立具備除錯能力的 SQL Agent
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent_executor = create_sql_agent(llm, db=db, agent_type="openai-tools", verbose=True)
    
    # 在背後偷偷加上強制繁體中文與語氣的 Prompt 限制
    enhanced_query = f"{query}\n\n請務必使用「繁體中文 (zh-TW)」回答。如果是金額或數量，請加上適當的單位以利閱讀。"

    # 透過 astream 擷取 Agent 的執行步驟與最終產出
    async for chunk in agent_executor.astream(
        {"input": enhanced_query}
    ):
        # 攔截工具使用 (Thought Process)
        if "actions" in chunk:
            for action in chunk["actions"]:
                yield {
                    "event": "thought",
                    "data": f"正在使用 {action.tool} 分析資料庫結構或執行查詢..."
                }
                
        # 攔截最終產出 (Final Message)
        if "output" in chunk:
            yield {
                "event": "message",
                "data": chunk["output"]
            }
