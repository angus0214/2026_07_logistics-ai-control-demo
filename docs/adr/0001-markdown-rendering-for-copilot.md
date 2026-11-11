# 0001. Law Copilot 的 Markdown 渲染

## 狀態
Accepted (2026-07-08)

## 背景脈絡 (Context)
Law Copilot 的回覆是 Markdown 格式（例如用粗體強調重點、用清單列出規則、換行）。目前 Vue 3 前端用文字插值 (text interpolation) 直接顯示原始文字，幾乎無法閱讀。我們需要把 Markdown 解析成 HTML、插入 DOM，並在 Tailwind CSS 環境中呈現良好的排版。

## 決策 (Decision)
1. **解析器**：採用 `marked`，因為它輕量、快速，且容易整合進 Vue 3。
2. **資安**：由於這是內部 POC，且我們信任自己的 LLM prompt，目前**不**使用 `DOMPurify` 過濾輸出，直接以 `v-html` 插入解析後的 HTML。這是為了開發速度而刻意做的取捨，上正式環境前必須重新評估。
3. **樣式**：安裝 `@tailwindcss/typography` 並套用 `prose prose-invert` class，替 `marked` 產生的無樣式 HTML 恢復正常排版（標題、清單、粗體），以抵銷 Tailwind 強力的 CSS reset (Preflight)。

## 後果 (Consequences)
- 可以快速交付美觀、易讀的 Copilot 介面。
- 接受 LLM 幻覺產生惡意 script 標籤時的 XSS 風險（在 POC 階段可接受）。
- 新增依賴會讓前端 bundle 略為變大。
