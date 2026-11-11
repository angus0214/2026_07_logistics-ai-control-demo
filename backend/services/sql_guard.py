"""
SQL Agent 的執行期防護 (ADR-0005)。

兩道互相獨立的防線：
1. 唯讀連線（見 db/database.py 的 readonly_engine）：擋住所有寫入。
2. 本模組在執行前解析 SQL：只允許單一一句 SELECT / WITH，且引用的資料表都必須在白名單內。

另外在執行時加上筆數上限與單句逾時。
"""
import time
from typing import Any, Dict, Iterable, Literal, Optional, Sequence, Union

import sqlglot
from sqlglot import exp
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from langchain_community.utilities import SQLDatabase

DEFAULT_MAX_ROWS = 200
DEFAULT_TIMEOUT_SECONDS = 5.0
# 每執行這麼多個 SQLite VM 指令就檢查一次是否逾時
_PROGRESS_HANDLER_STEPS = 1000


class UnsafeQueryError(Exception):
    """SQL 未通過防護檢查。訊息會原樣回給 Agent，讓它能自我修正。"""


def validate_sql(sql: str, allowed_tables: Iterable[str]) -> None:
    """
    檢查 SQL 是否為單一一句唯讀查詢，且只引用白名單內的資料表。
    不通過時拋出 UnsafeQueryError。
    """
    allowed = {t.lower() for t in allowed_tables}

    try:
        statements = [s for s in sqlglot.parse(sql, read="sqlite") if s is not None]
    except sqlglot.errors.ParseError as e:
        raise UnsafeQueryError(f"無法解析 SQL：{e}") from e

    if len(statements) != 1:
        raise UnsafeQueryError(f"一次只能執行一句 SQL，收到 {len(statements)} 句。")

    statement = statements[0]
    if not isinstance(statement, exp.Query):
        raise UnsafeQueryError(
            f"只允許 SELECT / WITH 查詢，不允許 {statement.key.upper()}。"
        )

    cte_names = {cte.alias_or_name.lower() for cte in statement.find_all(exp.CTE)}

    for table in statement.find_all(exp.Table):
        # 表值函式（例如 pragma_table_info('x')）沒有一般的資料表名稱
        if not isinstance(table.this, exp.Identifier):
            raise UnsafeQueryError(f"不允許在 FROM 中使用函式：{table.sql(dialect='sqlite')}")
        name = table.name.lower()
        if name in cte_names:
            continue
        if name not in allowed:
            raise UnsafeQueryError(
                f"資料表 {table.name} 不在可查詢範圍內。可查詢的資料表：{', '.join(sorted(allowed))}。"
            )


def run_guarded_query(
    engine,
    sql: str,
    allowed_tables: Iterable[str],
    max_rows: int = DEFAULT_MAX_ROWS,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> tuple[list[str], list[tuple], bool]:
    """
    驗證並執行 SQL。回傳 (欄位名稱, 資料列, 是否被截斷)。

    筆數上限的做法是只抓 max_rows + 1 筆，而不是在外層包 LIMIT，
    以免改變原本就有 ORDER BY / LIMIT 的查詢語意。
    """
    validate_sql(sql, allowed_tables)

    with engine.connect() as conn:
        raw_conn = conn.connection.driver_connection
        deadline = time.monotonic() + timeout_seconds
        # 回傳非 0 會讓 SQLite 中斷目前的查詢 (sqlite3.OperationalError: interrupted)
        raw_conn.set_progress_handler(
            lambda: 1 if time.monotonic() > deadline else 0, _PROGRESS_HANDLER_STEPS
        )
        try:
            result = conn.execute(text(sql))
            columns = list(result.keys())
            rows = [tuple(r) for r in result.fetchmany(max_rows + 1)]
        except SQLAlchemyError as e:
            if "interrupted" in str(e):
                raise UnsafeQueryError(
                    f"查詢超過 {timeout_seconds:g} 秒被中斷，請簡化查詢或加上篩選條件。"
                ) from e
            raise
        finally:
            raw_conn.set_progress_handler(None, 0)

    truncated = len(rows) > max_rows
    return columns, rows[:max_rows], truncated


class GuardedSQLDatabase(SQLDatabase):
    """
    LangChain SQLDatabase 的防護版。

    原本的 include_tables 只會把資料表從 LLM 看到的 schema 中藏起來，
    並不會阻止查詢；這裡在每次執行前強制檢查。
    """

    def __init__(
        self,
        engine,
        *,
        include_tables: Sequence[str],
        max_rows: int = DEFAULT_MAX_ROWS,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        **kwargs: Any,
    ):
        super().__init__(engine, include_tables=list(include_tables), **kwargs)
        self._allowed_tables = list(include_tables)
        self._max_rows = max_rows
        self._timeout_seconds = timeout_seconds

    def run(
        self,
        command: Union[str, Any],
        fetch: Literal["all", "one", "cursor"] = "all",
        include_columns: bool = False,
        *,
        parameters: Optional[Dict[str, Any]] = None,
        execution_options: Optional[Dict[str, Any]] = None,
    ) -> str:
        if not isinstance(command, str):
            raise UnsafeQueryError("只接受文字形式的 SQL。")

        columns, rows, truncated = run_guarded_query(
            self._engine,
            command,
            self._allowed_tables,
            max_rows=self._max_rows,
            timeout_seconds=self._timeout_seconds,
        )
        if fetch == "one":
            rows = rows[:1]

        if not rows:
            return ""

        if include_columns:
            body = str([dict(zip(columns, r)) for r in rows])
        else:
            body = str(rows)

        if truncated:
            body += (
                f"\n[結果已截斷：只顯示前 {self._max_rows} 筆。"
                f"若需要完整答案，請改用彙總 (COUNT / SUM / GROUP BY) 或加上篩選條件。]"
            )
        return body

    def run_no_throw(
        self,
        command: str,
        fetch: Literal["all", "one"] = "all",
        include_columns: bool = False,
        *,
        parameters: Optional[Dict[str, Any]] = None,
        execution_options: Optional[Dict[str, Any]] = None,
    ) -> str:
        # 父類別只攔 SQLAlchemyError；防護錯誤也要以文字回給 Agent，讓它自我修正
        try:
            return self.run(command, fetch, include_columns=include_columns)
        except (UnsafeQueryError, SQLAlchemyError) as e:
            return f"Error: {e}"
