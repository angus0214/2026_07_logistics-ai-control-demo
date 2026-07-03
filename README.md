# Logistics AI Control Tower

這是一個結合 Vue 3 前端與 FastAPI + LangChain 後端的 AI 物流戰情室 POC。

## 🚀 如何啟動專案 (How to run)

你需要開啟兩個終端機 (Terminal) 分別啟動前端與後端。

### 1. 啟動後端 (FastAPI)
請在終端機輸入以下指令：
```bash
cd backend
.venv\Scripts\activate
uvicorn main:app --reload
```
*啟動成功後，可以前往 `http://127.0.0.1:8000/docs` 檢視 API 規格與測試。*

### 2. 啟動前端 (Vue 3 + Vite)
請在**另一個新開的終端機**輸入以下指令：
```bash
cd frontend
npm run dev
```
*啟動成功後，可以前往 `http://localhost:5173` 檢視完整的操作介面。*
