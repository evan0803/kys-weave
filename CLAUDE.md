# 遠東經緯島（kys-weave）｜給 Claude Code 的工作指引

版本 2026-11-11（備份：`.claude/backups/CLAUDE.md.bak-20261111`）。
開始工作前，先讀 `docs/HANDOFF.md`（完整交接與決策表）；本檔只列每次都要遵守的規則。兩者衝突時，以 HANDOFF 第 3 節日期較新的決策為準，並告知使用者。

## 專案一句話
FENC 高潛人才班第五組「KYS 採購交易風險管控」的跨部門會診平台原型。六個部門（採購、財務、會計、國際事務、稽核、聯稽）各是一座浮空島，案件送進中央「經緯廣場」後，六部門同步各自依規則提出意見，供採購處參考。

## 三個版本（提到畫面時先確認是哪一版）
| 版本 | 位置 | 原始碼 | 怎麼更新 |
|---|---|---|---|
| 展示版 | https://evan0803.github.io/kys-weave/ （公開） | `index.html` | 推送到 `main` |
| 實測版 | https://claude.ai/artifact/W4St2o7bT4np1AUH1FnG2r （私人） | `tools/live/live.template.html` | `python tools/live/build_live.py` → 用 Artifact 工具發布 `out/live/kys-live.html`（帶上述網址，不要另開新成品） |
| 設計稿 | https://claude.ai/artifact/1KUts5rA63kzVDomaGbnTA （私人） | 成品本身 | 先讀成品再改 |

## 燈號定義（2026-11-09 定案，三個版本一致；HANDOFF 中 10/29 的舊定義已作廢）
各部門**只提意見**，是否採納、何時送出由**採購處決定**。
- 綠＝無意見
- 黃＝建議討論，或有資訊需要補充
- 紅＝強烈建議（事項較嚴重）
畫面文字與給 AI 的指示都不寫「禁止」「退回」「不得」「暫不送」，改用「建議」「請確認」「可考慮」。（給 AI 的指示中，為了告訴它「不要寫這些詞」而引用，不算違反。）

## 使用者與溝通
- 使用者是 Evan（李宗哲），採購處代表，**不是專案主導人**。對小組的提案一律以「供小組討論」包裝。
- 非工程背景：git、儲存庫、prompt 等詞第一次出現時用白話解釋。
- 回覆用臺灣繁體中文，先給結論再給理由；避免翻譯腔與中國用語（品質、影片、軟體、資訊、網路……）。
- 數字一讀就懂、日期寫完整年份；第三方資訊註明來源。
- 畫面偏好圖示化、生活化；較大的畫面改動先做設計稿，確認後再改實測版。
- Evan 在公司只能用 claude.ai 網頁與 Chat 專案。燈號、網址、決策有變動時，主動提議「更新摘要」：產出 `D:\進修課程\遠東新高潛經理班\經緯島_專案背景摘要_YYYYMMDD.md` 供他貼進 Chat 專案。

## 硬性規則
1. **預設不提交、不推送。** 使用者說「提交並推送」才做 git commit／push。實測版發布到 claude.ai 不受此限。
2. **這是公開儲存庫**（GitHub Pages 需要）。只能放虛構個案與示範條目。真實廠商、金額、查核報告、部門原始交件檔一律放 `data/`；含部門規則原文的產出放 `out/`。兩者都已 gitignore，絕不 commit。
3. 不得在網頁或程式中放任何 API 金鑰。實測版的 AI 走 claude.ai 成品內建功能（用開頁者自己的帳號）；正式的 AI 會診要在公司核准平台另外執行。
4. 實測版與測試檔**只放虛構資料**。
5. 各部門交的規則**原文不改**，只能補欄位（觸發標籤、檢核時點）。我方代擬或補充的條目，「來源」欄必須標明。
6. 展示版是單一檔案 `index.html`（Three.js 0.147.0 由 jsDelivr 載入、圖片以 base64 內嵌），改完要能直接用瀏覽器開啟。其中有一行（目前是第 320 行）是約 35 萬字的圖片資料：**不要整檔讀取**，用 Grep 定位後以 offset／limit 讀區段；多處修改用 Python 腳本做精確取代。
7. 決策有變動時，寫進 `docs/HANDOFF.md` 第 3 節（加日期）。

## 常用指令（Windows 用 `python`，不是 `python3`）
- 展示版測試：`npm install` → `npm test`（截圖在 `out/`，主控台錯誤會印出）。Playwright 未列在 package.json，缺少時先 `npm install --no-save playwright`，再 `npx playwright install chromium`
- 知識層確認稿：部門原始檔放進 `data/`（檔名見 HANDOFF 第 6 節）→ `npm run knowledge`，Excel 輸出到 `out/`
- 實測版：`python tools/knowledge/export_rules.py` → `python tools/live/build_live.py` → `node tools/test/live_smoke.js`（假的 AI 回覆跑完整流程）→ 發布
- 簡報離線版：`python tools/build_offline.py` → `node tools/test/offline_smoke.js`，輸出 `out/offline/遠東經緯島_離線版.html`
- 測試案例 Excel 在 `out/test-cases/`（冰水主機、國內備品）；不存在時 `build_live.py` 會失敗，需先請使用者提供或重做

## 發布展示版
推到 `main` 後 1～2 分鐘，公開網址自動更新。commit 訊息用繁體中文，說明改了什麼。
