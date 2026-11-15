# 0002. 老闆戰情室的 Text-to-SQL 架構

## 狀態
Accepted (2026-07-08)。第 1 點（資安與範圍）已由 [ADR-0005](0005-enforce-sql-agent-whitelist-at-execution.md) 修正：`include_tables` 只會隱藏 schema，白名單改為在執行時強制。第 3 點（表格）已由 [ADR-0008](0008-query-evidence-table-from-sql-result.md) 修正：表格改由後端從最後一句 SQL 的結果產生，LLM 只寫摘要。

實作備註：第 4 點最後改用 LangChain 的 `astream()` 逐步取得 Agent 的工具呼叫與最終輸出（而非 `astream_events()`），串流效果相同。

## 背景脈絡 (Context)
我們要為主管（老闆）打造一個「戰情室」儀表板，讓他們用自然語言查詢物流資料 (Text-to-SQL)。這個功能必須穩健、安全，並展現 Forward Deployed Engineer (FDE) 重視的透明度與容錯能力。

## 決策 (Decision)
在設計拷問 (grilling) 中，我們做了四項核心架構決策：

1. **資安與範圍（白名單）**：為避免幻覺或危險存取，用 SQLAlchemy 只把 `bills_of_lading` 列入白名單（排除 `bad_cases` 等內部資料表）。LLM 只能存取唯讀的 schema 切片。
2. **AI 執行方式（ReAct SQL Agent）**：不使用脆弱的單次 SQL chain，改用 LangChain SQL Agent。Agent 產生的 SQL 出錯時，會讀取錯誤訊息並自我修正，大幅提高成功率。
3. **資料呈現（文字 + Markdown 表格）**：最終輸出是一段自然語言摘要加上一個 Markdown 表格（由 ADR-0001 的前端 `marked` + Tailwind Typography 渲染）。
4. **傳輸協定（SSE 串流）**：透過 FastAPI 的 `StreamingResponse` 與 LangChain 的 `astream_events()` 使用 Server-Sent Events。同時串流 Agent 的中間「思考過程」（例如正在執行查詢、正在處理錯誤）與最終摘要，打造 FDE 風格的透明介面。

## 後果 (Consequences)
- **優點**：安全性高、容錯能力強，「透明介面」能建立主管的信任。
- **缺點**：後端實作較複雜（需要非同步串流 Agent 的每個步驟），且 ReAct 迴圈會讓回應時間稍長（5–8 秒）。
