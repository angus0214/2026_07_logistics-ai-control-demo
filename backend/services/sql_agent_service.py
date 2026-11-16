import os
import datetime
from dataclasses import dataclass
from typing import AsyncGenerator, Optional
from langchain_openai import ChatOpenAI
from langchain_community.agent_toolkits import create_sql_agent
from dotenv import load_dotenv

from services.data_dictionary import DictionaryVersion, load_dictionary
from services.sql_guard import DEFAULT_MAX_ROWS, GuardedSQLDatabase, run_guarded_query

load_dotenv()


@dataclass(frozen=True)
class Arm:
    """對照組：Agent 能查哪些表（執行時強制，ADR-0005）＋注入哪個版本的資料字典（None＝不注入）。"""
    allowed_tables: tuple[str, ...]
    dictionary: Optional[DictionaryVersion]


# 戰情室：查整理過的運費 view，帶 View 版資料字典；原始運費帳永遠不在白名單內
WAR_ROOM_ARM = Arm(allowed_tables=("bills_of_lading", "freight_charges"), dictionary="view")

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
        f"3. 請務必使用「繁體中文 (zh-TW)」回答。若是金額或數量，請加上適當的單位 (如公斤、USD) 以利閱讀。\n"
        f"4. 最後執行的那一句 SQL 必須單獨就能回答整個問題：差額、比例、比較都要在同一句 SQL 裡算好，不要分多句查完再自己計算，因為使用者會看到這句 SQL 的結果表格。"
    )
    if dictionary:
        agent_input += f"\n\n請依照下列資料字典的欄位意義與業務規則撰寫 SQL。\n[資料字典]\n{dictionary}"
    return agent_input


def _json_safe(value):
    return value if value is None or isinstance(value, (str, int, float, bool)) else str(value)


def result_event(engine, sql: Optional[str], allowed_tables, max_rows: int = DEFAULT_MAX_ROWS) -> Optional[dict]:
    """
    查詢依據 (Query Evidence)：用同樣的防護重跑 Agent 最後一句 SQL，把結果原樣交給前端渲染成表格。

    表格的數字不經過 LLM，也和評估判分重跑的是同一句 SQL（ADR-0008）。
    沒有 SQL 或重跑失敗時回傳 None，不送出表格。
    """
    if not sql:
        return None
    try:
        columns, rows, truncated = run_guarded_query(engine, sql, allowed_tables, max_rows=max_rows)
    except Exception:
        return None
    return {
        "event": "result",
        "sql": sql,
        "columns": columns,
        "rows": [[_json_safe(v) for v in row] for row in rows],
        "truncated": truncated,
    }


def action_event(tool_name: str, tool_input) -> dict:
    """把 Agent 的一次工具呼叫轉成串流事件；執行 SQL 時另帶原始 SQL（前端只讀 data，評估讀 sql）。"""
    if tool_name == "sql_db_query":
        sql = tool_input.get("query", str(tool_input)) if isinstance(tool_input, dict) else str(tool_input)
        return {"event": "thought", "data": f"執行 SQL 查詢: {sql}", "sql": sql}
    return {"event": "thought", "data": f"正在使用 {tool_name} 分析資料庫結構..."}


async def stream_sql_agent(
    query: str,
    engine,
    arm: Arm = WAR_ROOM_ARM,
) -> AsyncGenerator[dict, None]:
    """
    接收自然語言查詢與 SQLAlchemy Engine，透過 LangChain SQL Agent 分析並串流回傳過程。

    engine 應為唯讀連線 (db.database.readonly_engine)。白名單在每次執行 SQL 前強制檢查，
    不只是把其他資料表從 schema 中藏起來。白名單與資料字典由對照組 (Arm) 決定，預設是戰情室。
    """
    db = GuardedSQLDatabase(engine, include_tables=arm.allowed_tables)

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
        query, current_date, load_dictionary(arm.dictionary) if arm.dictionary else None
    )

    # 透過 astream 擷取 Agent 的執行步驟與最終產出
    last_sql = None
    async for chunk in agent_executor.astream(
        {"input": enhanced_query}
    ):
        # 攔截工具使用 (Thought Process)
        if "actions" in chunk:
            for action in chunk["actions"]:
                event = action_event(action.tool, action.tool_input)
                last_sql = event.get("sql", last_sql)
                yield event

        # 攔截最終產出 (Final Message)
        if "output" in chunk:
            yield {
                "event": "message",
                "data": chunk["output"]
            }

    # 查詢依據：最後一句 SQL 的原始結果，表格由前端直接渲染、不經 LLM（ADR-0008）
    evidence = result_event(engine, last_sql, arm.allowed_tables)
    if evidence:
        yield evidence
