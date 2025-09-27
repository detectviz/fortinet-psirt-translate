# Fortinet PSIRT 資安漏洞公告自動翻譯系統

## 1. 專案概述
本系統旨在自動擷取 Fortinet 官方 PSIRT（產品安全事件響應團隊）公告，並將公告標題與摘要翻譯為繁體中文，供內部資訊安全團隊及相關單位即時瀏覽與分析使用，提升漏洞資訊的即時性與可讀性。

### 1.1 核心特色
- **自動化翻譯**：使用 Google 翻譯服務將英文公告轉換為繁體中文
- **智能術語保護**：自動識別技術術語（如 RADIUS、CVE、FortiGate），避免錯誤翻譯
- **動態配置**：支援即時新增技術術語，無需重新啟動服務
- **高效快取**：智慧快取機制，避免重複翻譯，提升效能
- **RESTful API**：提供完整的 API 介面，支援公告管理與術語配置

## 2. 功能需求

### 2.1 資料擷取
- 自動從 Fortinet 官方 PSIRT RSS Feed（https://www.fortiguard.com/rss/ir.xml）定時抓取最新漏洞公告摘要與標題。
- 支援每天定時（可自訂）執行擷取作業。
- 持續更新並存儲擷取過的公告資訊，避免重複處理。

### 2.2 翻譯處理
- 使用 Python 第三方翻譯套件（googletrans）將公告標題與摘要翻譯為繁體中文。
- **智能技術術語保護**：自動識別並保護技術術語（如 RADIUS、CVE、FortiGate 等），避免錯誤翻譯。
- 提供翻譯緩存功能，已翻譯過的文字不再重複翻譯。
- 提供錯誤處理機制，翻譯失敗時回傳原文並記錄錯誤日誌。
- 支援動態管理技術術語清單，無需修改程式碼即可新增或更新保護詞彙。

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
  - googletrans (Google翻譯服務)
  - json
  - logging
  - re (正則表達式，用於技術術語匹配)
- 設定檔：`technical_terms.json` (技術術語保護清單)
- 執行環境：任意 Linux Server 或容器環境

## 6. 專案結構與使用方式

### 6.1 專案結構
```
backend/                    # FastAPI 與資料處理模組
  app.py                    # 提供 REST API 介面
  main.py                   # CLI 進入點，適合排程與手動觸發
  psirt_translate/          # 抽象化的抓取、翻譯、快取邏輯
    translator.py           # 翻譯服務與技術術語保護
    technical_terms.json    # 技術術語保護清單設定檔
    service.py              # 業務邏輯整合
    fetcher.py              # RSS資料擷取
    storage.py              # 快取與資料持久化
    config.py               # 系統設定
  tests/                    # 後端單元測試
frontend/                   # React 19 + TypeScript 介面
  src/                      # UI 與 API 呼叫程式碼
  index.html                # 單頁應用程式進入點
data/                       # 快取翻譯結果與公告資料
  translation_cache.json    # 翻譯結果快取
  advisories.json           # 公告資料快取
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

#### 公告管理
- `GET /api/advisories`：取得快取公告資料（可透過 `?refresh=true` 強制重新抓取，`?limit=N` 限制數量）。
- `POST /api/advisories/refresh`：立即擷取最新公告並更新快取。
- `GET /api/advisories/export`：下載目前快取的 JSON 結果。

#### 技術術語管理
- `POST /api/technical-terms/reload`：重新載入技術術語設定檔。
- `POST /api/technical-terms/add?term=TERM`：新增自訂技術術語。
- `GET /api/technical-terms/count`：取得載入的技術術語總數。

### 6.5 技術術語管理

系統內建智能技術術語保護功能，能自動識別並保護 100+ 種技術術語，避免翻譯時被錯誤轉換。

#### 6.5.1 預設保護術語分類
- **網路協議**：RADIUS、LDAP、SSH、TCP/IP 等
- **安全標準**：AES、RSA、SSL、TLS、CVE、CWE 等
- **Fortinet 產品**：FortiGate、FortiManager、FortiWeb 等
- **作業系統**：Windows、Linux、macOS 等
- **程式語言**：Python、Java、JavaScript 等
- **通用縮寫**：API、URL、VPN、CLI 等

#### 6.5.2 自訂技術術語
```bash
# 新增自訂技術術語
curl -X POST "http://127.0.0.1:8000/api/technical-terms/add?term=YOUR_TERM"

# 重新載入設定檔（修改 technical_terms.json 後使用）
curl -X POST "http://127.0.0.1:8000/api/technical-terms/reload"

# 查看術語總數
curl "http://127.0.0.1:8000/api/technical-terms/count"
```

#### 6.5.3 設定檔編輯
直接編輯 `backend/psirt_translate/technical_terms.json` 檔案來管理術語清單：

```json
{
  "network_protocols": ["RADIUS", "LDAP", "SSH"],
  "security_protocols": ["AES", "RSA", "SSL"],
  "custom_terms": ["YOUR_CUSTOM_TERM"]
}
```

### 6.6 演示版本部署

專案支援一鍵部署到 GitHub Pages 作為演示版本，展示翻譯功能和介面。

#### 6.6.1 自動部署（推薦）
專案已配置 GitHub Actions，推送到 main/master 分支時會自動部署：

```bash
# 推送到 GitHub
git add .
git commit -m "Deploy demo to GitHub Pages"
git push origin main
```

#### 6.6.2 手動部署
```bash
# 執行部署腳本
./deploy-demo.sh

# 或手動執行
cp data/advisories.json frontend/public/data/
cd frontend
npm ci
npm run build

# 將 frontend/dist 的內容部署到 GitHub Pages
```

#### 6.6.3 演示版本特色
- 📊 展示示例翻譯數據
- 🎨 完整的 UI 介面
- 🔒 技術術語保護展示
- 📱 響應式設計
- ⚡ 靜態資源，載入快速

### 6.7 常見問題與故障排除

#### Q: 為什麼有些術語沒有被翻譯？
A: 系統會自動保護技術術語。如果您發現某些術語應該被翻譯但沒有，請檢查：
1. 確認術語是否在 `technical_terms.json` 中列出
2. 使用 API 新增術語：`POST /api/technical-terms/add?term=YOUR_TERM`
3. 重新載入設定：`POST /api/technical-terms/reload`

#### Q: 如何新增更多技術術語？
A: 有三種方式：
1. **API方式**：`POST /api/technical-terms/add?term=NEW_TERM`
2. **設定檔編輯**：直接編輯 `technical_terms.json` 並重新載入
3. **分類管理**：在設定檔的適當分類中新增術語

#### Q: 翻譯結果包含奇怪的符號是什麼問題？
A: 這通常是因為翻譯緩存中殘留了舊的資料。請刪除 `data/translation_cache.json` 檔案並重新翻譯。

#### Q: 如何驗證術語保護是否正常工作？
A: 測試翻譯一段包含已知術語的文字：
```bash
curl -X POST "http://127.0.0.1:8000/api/advisories/refresh?limit=1"
```
檢查結果中的 `title_zh` 和 `summary_zh` 欄位，確認技術術語保持原文。

### 6.8 測試
```bash
cd backend
pip install .[test]
pytest
```

#### 前端測試
```bash
cd frontend
npm test  # 如果有測試配置
npm run preview  # 預覽生產建置
```
