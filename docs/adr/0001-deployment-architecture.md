# 0001. 輕量化分離部署架構 (Vercel + Render)

## 狀態
Accepted (2026-07-13)

## 背景脈絡 (Context)
為了在 FDE 面試中提供一個隨時可用、高可用性的 Demo 系統，我們需要將原本在本地端運行的 Logistics AI Control Tower 部署到雲端。
系統的後端依賴 SQLite 作為資料庫（因為 POC 不需承載高併發，且 SQLite 維護成本最低）。然而，多數的 Serverless 或輕量級 PaaS 服務（如 Heroku, Vercel）都是無狀態 (Stateless) 的，這會導致每次重新部署或機器休眠喚醒時，`logistics.db` 資料庫被清空，這在面試展示中是不可接受的風險。

## 決策 (Decision)
我們決定採用 **前後端分離的輕量化部署架構**，並接受每月約 $7 USD 的小額基礎設施支出：
1. **前端 (Vue 3 + Vite)**：部署至 **Vercel**。Vercel 對於靜態 SPA (Single Page Application) 的支援極佳，部署速度快，且提供全球 CDN 加速，完全免費。
2. **後端 (FastAPI + SQLite)**：部署至 **Render** 的 Web Service。
   - 選用 Render 的原因在於它提供了極度友善的 **Persistent Disk (持久化磁碟)** 掛載功能（每月 $0.25 USD），完美解決了 SQLite 在雲端資料遺失的問題。
   - 我們將為 Render 配置一個 `render.yaml` (Infrastructure as Code) 來自動化後端的建置與磁碟掛載。

## 後果 (Consequences)
- **優點**：架構極度單純，面試官可以隨時透過公開網址存取。前後端解耦，前端享有 Vercel 的極速體驗，後端的 SQLite 資料受到持久化磁碟保護。
- **缺點 / 妥協**：需要綁定信用卡支付 Render 的最低階運算實例費用。由於前後端網域不同，後端的 FastAPI 必須嚴格設定 CORS (Cross-Origin Resource Sharing) 來允許 Vercel 的網域存取。
