# 🚢 Logistics AI Control Tower (物流 AI 戰情室)

> 將傳統海空運承攬業的紙本作業，轉化為具備 RAG 與 Text-to-SQL 能力的企業級 AI 數據中樞。

[![Python](https://img.shields.io/badge/Python-3.11-3776AB?logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Vue3](https://img.shields.io/badge/Vue.js-3.0-4FC08D?logo=vue.js&logoColor=white)](https://vuejs.org/)
[![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)](https://www.docker.com/)

🔗 **Live Demo (Vercel Frontend)**: [https://2026-07-logistics-ai-control-demo.vercel.app](https://2026-07-logistics-ai-control-demo.vercel.app)

---

## 📖 專案背景與痛點 (Background & Pain Points)

> **💡 專案緣起 (Genesis)**：本專案源自於我過去親自參與的一項物流業諮詢案。在深入了解第一線的作業流程後，我將當時的諮詢洞見與後續展望，轉化為這份以**最小可行性產品 (MVP)** 為基準開發的 **概念驗證 (POC)**。儘管部分邊界功能尚在迭代，但核心架構已完整展示了 Agentic AI 解決產業痛點的潛力。

在傳統海空運承攬業 (Freight Forwarder) 的實務運作中，往往面臨以下兩大痛點：
1. **非結構化資料的噩夢**：每天收到來自全球各地、格式不一的提單 (Bill of Lading, B/L) 圖片或 PDF。OP (業務) 需要耗費大量時間人工辨識、打字輸入系統。
2. **缺乏即時決策數據**：管理層想知道「這季亞洲線的總營收」，往往需要依賴工程師寫 SQL 撈資料，或等財務部門月底的報表，存在嚴重的資料孤島與時間差。

**💡 解決方案：**
本 POC 專案透過導入 Agentic AI 解決上述問題。以 OpenAI Vision 進行文件辨識，以 RAG 技術輔助業務審單，並透過 SQL Agent 賦能管理層使用「自然語言」直接查詢營收數據。

---

## 🚀 快速啟動 (Quick Start)

專案採用「前端本地啟動 + 後端 Docker 容器化」的混合開發模式。

### 先決條件
* 安裝 [Docker Desktop](https://www.docker.com/products/docker-desktop)
* 安裝 [Node.js](https://nodejs.org/) (建議 v18+)

### 1. 後端啟動 (Docker)
後端環境與資料庫 (SQLite / ChromaDB) 已完整容器化，免除 Python 環境設定的煩惱。

```bash
# 1. 複製並設定環境變數
cp backend/.env.example backend/.env
# 請在 backend/.env 中填寫您的 OPENAI_API_KEY

# 2. 啟動後端容器 (背景執行)
docker-compose up -d
```
> 後端 API 啟動於 `http://localhost:8000`  
> Swagger 測試文件：`http://localhost:8000/docs`

### 2. 前端啟動 (Vite + Vue 3)
前端使用 Vite 建立，為了避免 Windows Hyper-V 常見的 Port 佔用問題，開發 Port 已預設改為 `3000`。

```bash
# 1. 進入前端目錄
cd frontend

# 2. 安裝依賴套件
npm install

# 3. 啟動開發伺服器
npm run dev
```
> 前端畫面啟動於 `http://localhost:3000`

---

## ✨ 核心功能 (Features)

### 1. Op Copilot (業務副駕)
* **智慧 OCR 擷取**：上傳提單圖片，自動識別提單號碼、寄件人、收件人與貨物描述。
* **RAG 檢索問答**：結合 ChromaDB 向量庫，業務可以直接詢問副駕：「這份提單的卸貨港在哪裡？」，AI 將根據文件內容給予精準答覆。

### 2. Boss Dashboard (老闆戰情室)
* **歷史提單總覽**：視覺化呈現所有已確認寫入資料庫的提單紀錄。
* **Text-to-SQL (AI 營運特助)**：管理層可直接在對話框輸入：「*幫我查一下前 5 筆金額最高的提單*」，SQL Agent 會自動分析資料表結構、轉譯為 SQL 語法、查詢 SQLite，並以自然語言回報結果（透過 SSE 串流顯示思考軌跡）。

### 3. Data Flywheel (資料飛輪與 Bad Case 收集)
* **自動糾錯收集機制**：當 AI (OCR) 辨識結果有誤，且經由業務端人工覆核修改後，系統會自動將該筆紀錄標記為 Bad Case，並連同原始圖片與錯誤輸出，獨立寫入資料庫。
* **持續微調基石**：這套機制為工程團隊提供了最真實的 Edge Case 資料集，供未來 Fine-tuning 模型使用，形成完善的 Data Flywheel 閉環。

---

## 🏗️ 架構與資料流程圖 (Architecture & Data Flow)

本系統將架構分為清晰的表現層、AI 邏輯層與資料持久層。前端透過 RESTful API 與 SSE (Server-Sent Events) 與後端進行通訊。

```mermaid
graph TD
    subgraph "Frontend (Vue 3)"
        UI_Upload[提單上傳介面]
        UI_Chat[Op Copilot 聊天室]
        UI_Boss[Boss 戰情室 Dashboard]
    end

    subgraph "Backend (FastAPI in Docker)"
        API_Upload[POST /api/upload_bl]
        API_RAG[POST /api/chat/op_rag]
        API_SQL[POST /api/boss_sql]
        
        OCR[OpenAI Vision API]
        Agent_RAG[LangChain RAG Engine]
        Agent_SQL[LangChain SQL Agent]
    end

    subgraph "Data Storage"
        DB_SQL[(SQLite \n 關聯式資料)]
        DB_Vect[(ChromaDB \n 向量資料庫)]
    end
    
    %% 提單上傳與解析流程
    UI_Upload -->|上傳圖片| API_Upload
    API_Upload -->|呼叫| OCR
    OCR -->|回傳結構化 JSON| API_Upload
    API_Upload -.->|業務覆核 (正確)| DB_SQL
    API_Upload -.->|業務覆核 (修改)| DB_SQL_Bad[Bad Case 資料表]
    DB_SQL_Bad -.->|Data Flywheel| DB_SQL_Bad
    
    %% RAG 流程
    UI_Chat -->|詢問文件細節| API_RAG
    API_RAG --> Agent_RAG
    Agent_RAG <-->|檢索相關 Context| DB_Vect
    Agent_RAG -->|Text 串流| UI_Chat
    
    %% SQL Agent 流程
    UI_Boss -->|自然語言查詢營收| API_SQL
    API_SQL --> Agent_SQL
    Agent_SQL <-->|自動產生並執行 SQL| DB_SQL
    Agent_SQL -->|SSE 串流 (Thought + Answer)| UI_Boss

    classDef default fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef frontend fill:#e1f5fe,stroke:#0288d1,stroke-width:2px;
    classDef backend fill:#e8f5e9,stroke:#388e3c,stroke-width:2px;
    classDef storage fill:#fff3e0,stroke:#f57c00,stroke-width:2px;
    
    class UI_Upload,UI_Chat,UI_Boss frontend;
    class API_Upload,API_RAG,API_SQL,OCR,Agent_RAG,Agent_SQL backend;
    class DB_SQL,DB_Vect storage;
```
