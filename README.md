# 需求規格書: Fortinet PSIRT 資安漏洞公告自動翻譯系統

## 1. 專案概述
本系統旨在自動擷取 Fortinet 官方 PSIRT（產品安全事件響應團隊）公告，並將公告標題與摘要翻譯為繁體中文，供內部資訊安全團隊及相關單位即時瀏覽與分析使用，提升漏洞資訊的即時性與可讀性。

## 2. 功能需求

### 2.1 資料擷取
- 自動從 Fortinet 官方 PSIRT RSS Feed（https://www.fortiguard.com/rss/ir.xml）定時抓取最新漏洞公告摘要與標題。
- 支援每天定時（可自訂）執行擷取作業。
- 持續更新並存儲擷取過的公告資訊，避免重複處理。

### 2.2 翻譯處理
- 使用 Python 第三方翻譯套件（googletrans）將公告標題與摘要翻譯為繁體中文。
- 提供翻譯緩存功能，已翻譯過的文字不再重複翻譯。
- 提供錯誤處理機制，翻譯失敗時回傳原文並記錄錯誤日誌。

### 2.3 輸出格式
- 將原文與繁體中文翻譯結果以 JSON 格式輸出，包含欄位：
  - 原標題 (title_en)
  - 繁體標題 (title_zh)
  - 原摘要 (summary_en)
  - 繁體摘要 (summary_zh)
  - 公告連結 (link)
  - 發布時間 (published)
- 提供儲存結果到本地檔案，檔名格式可自訂。

### 2.4 排程與自動化
- 支援靠 cron 或類似排程軟體自動執行，並通知執行情況。
- 支援手動觸發功能，便於開發與維護調試。

### 2.5 系統日誌
- 紀錄每次擷取與翻譯的執行結果與錯誤資訊。
- 支持輸出執行紀錄到日誌檔，方便問題追蹤。

## 3. 非功能需求

### 3.1 穩定性
- 系統應能長期穩定運作，遇網路異常有重試機制。
- 翻譯模組應捕獲異常，避免系統崩潰。

### 3.2 性能
- 單次擷取指令能在合理時間（10秒內）完成。
- 支援擴充功能以應付未來大量公告擷取。

### 3.3 可維護性
- 程式碼具備適當註解與文件說明。
- 支援模組化結構，方便測試與功能擴充。

## 4. 系統架構簡圖
- 資料來源：Fortinet PSIRT RSS Feed →  
- 擷取模組：定時抓取 RSS →  
- 翻譯模組：googletrans →  
- 緩存管理：翻譯結果 Cache →  
- 輸出模組：JSON 結果輸出 →  
- 排程工具：Cron 或 Kubernetes CronJob

## 5. 技術堆疊

- 前端程式語言：React 19 + TypeScript
- 後端程式語言：Python 3.10+
- 主要套件：
  - feedparser (RSS解析)
  - googletrans
  - json
  - logging
- 執行環境：任意 Linux Server 或容器環境

## 6. 專案結構與使用方式

### 6.1 專案結構
```
backend/                # FastAPI 與資料處理模組
  app.py                # 提供 REST API 介面
  main.py               # CLI 進入點，適合排程與手動觸發
  psirt_translate/      # 抽象化的抓取、翻譯、快取邏輯
  tests/                # 後端單元測試
frontend/               # React 19 + TypeScript 介面
  src/                  # UI 與 API 呼叫程式碼
  index.html            # 單頁應用程式進入點
data/                   # 快取翻譯結果與公告資料
```

### 6.2 後端服務
1. 建立虛擬環境並安裝依賴：
   ```bash
   cd backend
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 執行 FastAPI 服務：
   ```bash
   uvicorn app:app --reload
   ```
3. CLI 手動觸發擷取與輸出：
   ```bash
   python main.py --output data/psirt_advisories.json
   ```
4. 排程範例（每日 09:00 觸發）：
   ```cron
   0 9 * * * /path/to/python /path/to/backend/main.py --output /path/to/data/psirt_advisories.json >> /var/log/psirt.log 2>&1
   ```

### 6.3 前端介面
1. 安裝依賴並啟動開發伺服器：
   ```bash
   cd frontend
   npm install
   npm run dev
   ```
2. 開啟瀏覽器並造訪 `http://localhost:5173`，即可操作公告翻譯介面。
3. 建置正式版靜態檔案：
   ```bash
   npm run build
   ```

### 6.4 API 介面摘要
- `GET /api/advisories`：取得快取公告資料（可透過 `?refresh=true` 強制重新抓取）。
- `POST /api/advisories/refresh`：立即擷取最新公告並更新快取。
- `GET /api/advisories/export`：下載目前快取的 JSON 結果。

### 6.5 測試
```bash
cd backend
pip install .[test]
pytest
```
