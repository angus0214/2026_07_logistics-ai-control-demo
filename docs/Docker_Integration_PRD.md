# PRD: 後端 Docker 容器化整合 (Backend Docker Integration)

## 問題陳述 (Problem Statement)

Logistics AI Control Tower POC 目前前端部署於 Vercel，後端部署於 Render 的原生 Python 環境。雖然這個架構在目前的雲端設置下運作良好，但它缺乏了 FDE (Forward Deployed Engineer) 面試所需的「企業級軟體交付 (Enterprise Software Delivery)」能力的明確證明。
此外，本地開發環境目前需要手動設定 Python 虛擬環境、手動安裝套件（像是 ChromaDB 這類需要 C++ 編譯環境的複雜依賴很容易報錯），還要手動下指令啟動服務。
我們需要一種方式向招募主管證明我們具備容器化 (Containerization) 的能力，同時優化本地開發流程，而且「不能破壞」前端在 Vercel 上既有的高度優化部署。

## 解決方案 (Solution)

導入「混合式容器化戰略 (Hybrid Containerization Strategy)」。我們將只針對 FastAPI 後端進行容器化，並使用 `docker-compose` 進行本地端服務編排；同時，刻意將 Vue 前端保留在 Vercel 的 Edge Network 上。這不僅滿足了企業對於後端環境可重現性 (Reproducibility) 的要求，解決了本地開發的「相依性地獄」，還保留了 Vercel 為前端帶來的全球 CDN 優勢。

## 用戶故事 (User Stories)

1. 身為一名 **招募主管 (Hiring Manager)** 審查 GitHub Repo 時，我希望看到後端目錄中有 `Dockerfile`，以便我能驗證候選人知道如何將應用程式打包，部署到企業內部受限或斷網 (Air-gapped) 的地端環境中。
2. 身為一名 **開發者 (Developer)** 在本地設定專案時，我希望只要執行一行 `docker-compose up` 指令，就能讓包含 Python、FastAPI 與所有套件的後端環境一鍵啟動，以便我不用管作業系統的差異就能立刻開始寫扣。
3. 身為一名 **開發者 (Developer)** 在使用 ChromaDB 時，我希望 C++ 編譯等依賴環境都已經在預先設定好的 Docker Image 裡處理完畢，以便我不會在不同的電腦上遇到千奇百怪的編譯錯誤。
4. 身為一名 **FDE 求職者 (FDE Applicant)**，我希望前端能繼續保留在 Vercel 上進行原生部署 (不使用 Docker)，以便我能利用 Vercel 強大的 Edge Network，並展示我「依據場景選擇最適工具」的務實架構思維。

## 實作決策 (Implementation Decisions)

- **前端範疇 (Frontend Scope)**：保持現狀。Vue 3 前端「不會」被 Docker 化。它將繼續透過 Vercel 的原生構建系統部署，以保留 Edge 優化。
- **後端 Dockerfile (`backend/Dockerfile`)**：使用官方的 Python slim image 建立 Dockerfile。它必須處理 ChromaDB 所需的系統依賴 (例如 `build-essential`)，複製應用程式碼，並對外曝露 FastAPI 埠號 (例如 8000)。
- **本地端編排 (`docker-compose.yml`)**：在根目錄建立 compose 檔案以定義後端服務。必須將本地目錄掛載 (Mount) 進去以達成開發時的熱更新 (Hot-reloading)，並映射正確的對外埠號。
- **Render 部署更新**：更新 Render 配置 (透過 Dashboard 或是修改 `render.yaml`)，將後端環境從 `python` 切換為 `docker`。必須確保 SQLite 的持久化硬碟 (`/data`) 被正確映射到容器內的工作目錄。

## 測試決策 (Testing Decisions)

- **本地建置測試 (Local Build Test)**：確保在一個全新的環境中 (沒有本地 python `venv`)，執行 `docker-compose build` 與 `docker-compose up` 能成功啟動 FastAPI 伺服器，且能在 `http://localhost:8000/docs` 看到 API 說明檔。
- **API 功能測試 (API Functionality Test)**：發送測試請求給在 Docker 容器內運行的 `/api/chat/boss_sql` 與 `/api/chat/op_rag` 端點，驗證 ChromaDB 與 SQLite 在隔離的容器環境中是否正常運作。
- **Render 部署測試 (Render Deployment Test)**：推送 `Dockerfile` 後，監控 Render 的部署 Log，確認 Render 能成功建置 Docker 映像檔，且持久化硬碟被正確掛載並可寫入。

## 範圍外 (Out of Scope)

- 將 Vue 3 前端 Docker 化 (Vercel 依然是首選目標)。
- 建立複雜的 Kubernetes (K8s) 叢集或 Helm charts (對於這個 PoV 來說，簡單的 `docker-compose` 已經足以證明能力)。
- 實作進階的 Docker 多階段建置 (Multi-stage builds) 來追求極致的映像檔縮小，除非建置時間真的成為嚴重的瓶頸。

## 補充說明 (Further Notes)

這份 PRD 對應了面試戰略的技術執行細節。透過將 Docker 視為「解決特定問題 (本地依賴地獄與企業信任度) 的工具」，而非「盲目要求所有組件都必須套用」的教條，我們能突顯出一種成熟、務實的架構師心智模型。
