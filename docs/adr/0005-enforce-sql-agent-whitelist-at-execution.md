# 0005. SQL Agent 的資料表白名單改在執行時強制，而非只靠 Prompt

## 狀態
Accepted (2026-11-11)。修正 [ADR-0002](0002-text-to-sql-architecture.md) 第 1 點。

## 背景脈絡 (Context)
ADR-0002 承諾了唯讀、有白名單的 schema，但 `SQLDatabase(include_tables=...)` 只會把資料表從 LLM 看到的 schema 中藏起來。Agent 若產生 `SELECT * FROM bad_cases`，照樣能執行，而且用的是應用程式共用的讀寫 engine。白名單實際上沒有被強制。

## 決策 (Decision)
改用兩道互相獨立的防線：

1. **獨立的唯讀連線**：Agent 使用自己的 SQLite 唯讀連線 (`mode=ro`)，負責擋住所有寫入。
2. **執行前解析 SQL**：每一句 SQL 執行前先解析，只允許單一一句 `SELECT`／`WITH`，且引用的資料表都必須在白名單內（提單主表加上整理過的運費 view；原始的運費帳永遠不在其中）。這一層負責擋住多句查詢、`ATTACH`／`PRAGMA` 等手法，以及讀取白名單以外的表。

兩道防線各自擋住對方擋不到的東西。

### 考慮過的選項
- **只用唯讀連線**：能擋寫入，但 Agent 仍能讀任何資料表，包括 `bad_cases`（含 base64 的文件圖片）。
- **再加上 `PRAGMA query_only`**：和唯讀連線的作用重複。

## 後果 (Consequences)
- 查詢結果上限 200 筆：實際抓 N+1 筆，超過時告訴 Agent 結果已截斷。不採用在外層包 `LIMIT`，因為那會改變原本就有排序或 limit 的查詢語意。Agent 收到截斷提示後可依 ADR-0002 的 ReAct 迴圈自行修正查詢。
- SQLite 沒有內建的單句逾時，改用 progress handler 在 5 秒後中斷查詢；Agent 整體另有 8 步、60 秒的上限。
- 白名單會依評估的對照組 (Arm) 不同而改變（Raw 組放原始運費帳，不放 view），所以它是設定值，不是常數。
