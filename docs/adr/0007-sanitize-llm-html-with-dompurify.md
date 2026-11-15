# 0007. LLM 回答插入 DOM 前一律用 DOMPurify 過濾

## 狀態
Accepted (2026-11-15)。修正 [ADR-0001](0001-markdown-rendering-for-copilot.md) 第 2 點。

## 背景脈絡 (Context)
ADR-0001 為了開發速度，接受 `marked` 解析後的 HTML 不經過濾、直接以 `v-html` 插入，理由是「內部 POC、信任自己的 prompt」，並註明上正式環境前要重新評估。這個前提已經不成立：

- 戰情室也用同樣方式渲染 SQL Agent 的回答，而回答會帶出資料庫內容，包括使用者上傳提單後 OCR 讀出的文字。
- demo 部署在公開網址，任何人都能上傳提單。

因此可以上傳一張「文字含惡意 HTML」的提單，讓它在老闆打開戰情室時執行（儲存型 XSS）。風險來源是資料，不是 prompt，信任 prompt 擋不住。

## 決策 (Decision)
所有 LLM 回答一律經由 `frontend/src/utils/markdown.ts` 的 `renderMarkdown()`：先用 `marked` 轉 HTML，再用 DOMPurify 過濾，才交給 `v-html`。戰情室 (`BossDashboard.vue`) 與 OP Copilot (`OpCopilotDrawer.vue`) 共用這一個函式。

### 考慮過的選項
- **不用 `v-html`，改成純文字**：最安全，但失去清單、粗體、表格，回到 ADR-0001 想解決的問題。
- **只過濾戰情室**：Copilot 的回答同樣來自 LLM，規則不一致容易漏，不划算。

## 後果 (Consequences)
- 擋掉 `<script>`、行內事件 (`onerror` 等)、`javascript:` 連結；清單、粗體、表格照常呈現（`src/utils/__tests__/markdown.spec.ts`）。
- 前端多一個依賴 `dompurify`。
- 之後若新增其他會渲染 LLM 輸出的地方，要用 `renderMarkdown()`，不要直接 `marked.parse()`。
