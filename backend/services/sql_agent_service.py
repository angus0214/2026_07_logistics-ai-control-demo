import os
import datetime
from typing import AsyncGenerator, Optional, Sequence
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv

from services.data_dictionary import DictionaryVersion, load_dictionary
from services.sql_guard import GuardedSQLDatabase

load_dotenv()

# 預設白名單；評估的不同對照組 (Arm) 會傳入不同的白名單 (ADR-0005)
DEFAULT_ALLOWED_TABLES = ("bills_of_lading",)
# Agent 整體上限：防止 ReAct 迴圈無止盡地重試
AGENT_MAX_ITERATIONS = 8
AGENT_MAX_EXECUTION_SECONDS = 60


def build_agent_input(query: str, current_date: str, dictionary: Optional[str]) -> str:
    """組出送給 Agent 的輸入：使用者問題＋系統提示＋（依對照組）資料字典全文。"""
    agent_input = (
        f"{query}\n\n"
        f"[系統提示]\n"
        f"1. 今天的日期是 {current_date}。若查詢中提到「今年」，請以此年份為基準。\n"
        f"2. 查詢字串型態的欄位 (例如 destination, shipper) 時，請一律優先使用 `LIKE '%關鍵字%'` 進行模糊比對。因為資料庫中的值常帶有額外括號或全名，例如 'USLAX (Los Angeles)'。\n"
        f"3. 請務必使用「繁體中文 (zh-TW)」回答。若是金額或數量，請加上適當的單位 (如公斤、USD) 以利閱讀。"
    )
    if dictionary:
        agent_input += f"\n\n請依照下列資料字典的欄位意義與業務規則撰寫 SQL。\n[資料字典]\n{dictionary}"
    return agent_input


async def stream_sql_agent(
    query: str,
    engine,
    allowed_tables: Sequence[str] = DEFAULT_ALLOWED_TABLES,
    dictionary: Optional[DictionaryVersion] = None,
) -> AsyncGenerator[dict, None]:
    """
    接收自然語言查詢與 SQLAlchemy Engine，透過 LangChain SQL Agent 分析並串流回傳過程。

    engine 應為唯讀連線 (db.database.readonly_engine)。白名單在每次執行 SQL 前強制檢查，
    不只是把其他資料表從 schema 中藏起來。dictionary 決定注入哪個版本的資料字典
    （None＝不注入），和 allowed_tables 一起由對照組 (Arm) 決定。
    """
    db = GuardedSQLDatabase(engine, include_tables=allowed_tables)

    # 建立具備除錯能力的 SQL Agent
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    agent_executor = create_sql_agent(
        llm,
        db=db,
        agent_type="openai-tools",
        verbose=True,
        max_iterations=AGENT_MAX_ITERATIONS,
        max_execution_time=AGENT_MAX_EXECUTION_SECONDS,
    )
    
    # 在背後加上系統提示（繁體中文、系統日期、模糊比對）與資料字典
    current_date = datetime.datetime.now().strftime("%Y-%m-%d")
    enhanced_query = build_agent_input(
        query, current_date, load_dictionary(dictionary) if dictionary else None
    )

    # 透過 astream 擷取 Agent 的執行步驟與最終產出
    async for chunk in agent_executor.astream(
        {"input": enhanced_query}
    ):
        # 攔截工具使用 (Thought Process)
        if "actions" in chunk:
            for action in chunk["actions"]:
                tool_name = action.tool
                tool_input = action.tool_input
                
                if tool_name == "sql_db_query":
                    # 擷取真實執行的 SQL 語法
                    query_str = tool_input.get("query", str(tool_input)) if isinstance(tool_input, dict) else str(tool_input)
                    yield {
                        "event": "thought",
                        "data": f"執行 SQL 查詢: {query_str}"
                    }
                else:
                    yield {
                        "event": "thought",
                        "data": f"正在使用 {tool_name} 分析資料庫結構..."
                    }
                
        # 攔截最終產出 (Final Message)
        if "output" in chunk:
            yield {
                "event": "message",
                "data": chunk["output"]
            }
