# 壁球影片分析 Squash Video Analysis

從壁球比賽影片自動偵測擊球時機,分類為正手 (forehand) / 反手 (backhand) / 發球 (serve),並統計回合數與擊球分布 —— 概念上類似 [Rally Vision](https://www.rallyvision.co) 這類運動影片分析工具的 MVP 版本。

## 兩種版本

同一套分析邏輯(擊球偵測 / 分類規則 / 統計)實作了兩次,分別對應兩種部署方式:

| | `docs/`(純前端) | `backend/` + `frontend/`(Python 後端) |
|---|---|---|
| 執行環境 | 完全在瀏覽器裡執行(MediaPipe WASM) | 需要跑 Python 伺服器(FastAPI + OpenCV + MediaPipe) |
| 部署方式 | **可直接放 GitHub Pages**,零伺服器成本 | 需要有伺服器/容器可以跑 Python(Render、Fly.io、自架主機等) |
| 影片隱私 | 影片完全不會離開使用者的裝置 | 影片會上傳到後端暫存處理 |
| 適合情境 | 想公開分享一個可以直接玩的網頁連結 | 想要更好控制運算資源,或以後要接更重的模型(如自訓練的分類器) |

兩邊的擊球偵測/分類/統計邏輯是刻意寫成一致的兩份實作(Python 在 `backend/app/pipeline/`,JavaScript 在 `docs/js/pipeline/`),兩邊都各自有對應的單元測試,調整門檻值時記得兩邊一起改。

### 部署到 GitHub Pages

1. 到這個 repo 的 GitHub 頁面 → **Settings → Pages**。
2. Source 選擇 **Deploy from a branch**,Branch 選這個分支、資料夾選 **/docs**,儲存。
3. 幾分鐘後 GitHub 會給一個 `https://<你的帳號>.github.io/<repo>/` 的網址,開啟就能直接上傳影片使用,不需要跑任何伺服器。

`docs/index.html` 會從 CDN(cdnjs 載入 Chart.js、jsdelivr 載入 MediaPipe Tasks Vision、Google 的 storage.googleapis.com 載入姿勢模型檔)抓取所需資源,所以使用者的瀏覽器需要能連上這些網域。

## 目前的分析方式

這是一個 **v1 啟發式規則版本**,還不是訓練過的機器學習模型(目前沒有已標註的壁球影片資料集)。流程如下(下面路徑以 Python 版為例;JS 版邏輯在 `docs/js/pipeline/` 底下同名檔案):

1. **抽幀** (`app/pipeline/video_io.py`):用 OpenCV 讀取影片,依 `SAMPLE_FPS`(預設 15fps)抽樣畫面,不需要每一幀都做姿勢估計。JS 版則是用 `<video>` 元素 seek 到對應時間點抽樣(`docs/js/pose.js`)。
2. **姿勢估計** (`app/pipeline/pose.py`):用 MediaPipe Pose(Tasks API)取得球員的關鍵點(手腕、手肘、肩膀、髖部)。JS 版用同一套 MediaPipe 模型,但透過瀏覽器內的 WASM 執行。
3. **擊球偵測** (`app/pipeline/hit_detection.py`):計算手腕移動速度,速度出現局部峰值且高於門檻值時視為一次擊球,並用 refractory period 避免同一次揮拍被算成多次。
4. **擊球分類** (`app/pipeline/classifier.py`):
   - 擊球瞬間手腕若「跨過」軀幹中線 → 反手,否則 → 正手。
   - 若是該回合第一顆球,且擊球點高於肩膀 → 發球。
5. **統計聚合** (`app/pipeline/stats.py`):兩次擊球間隔超過 `RALLY_GAP_SECONDS`(預設 4 秒)視為新的一回合,並統計各類型擊球次數。

### 已知限制

- 準確度會受鏡頭角度、球員遮擋、慣用手、多人同框等因素影響很大,`config.py`/`config.js` 中的門檻值需要依實際場地/攝影機重新校調。
- 目前假設畫面中只有一位主要球員(`num_poses=1`);雙人或多人比賽畫面需要另外處理球員身分辨識。
- 這是幾何規則分類,不是學習到的動作辨識模型。下一步若要提升準確度,建議收集實際壁球影片並標註正手/反手/發球/切球等動作,訓練一個以姿勢序列為輸入的分類模型(例如簡單的 LSTM 或 1D-CNN),取代 `classifier.py` 中的規則。

## 專案結構

```
backend/
  app/
    main.py              # FastAPI 應用程式(/health, /analyze)
    models.py             # API 回傳的 pydantic schema
    pipeline/
      video_io.py         # OpenCV 抽幀
      pose.py              # MediaPipe Pose 姿勢估計
      features.py          # 手腕速度等特徵計算
      hit_detection.py     # 擊球事件偵測
      classifier.py        # 正手/反手/發球分類規則
      stats.py             # 回合切分與統計聚合
      config.py            # 可調參數
  scripts/analyze_video.py  # 命令列工具,不透過網頁也能分析影片
  tests/                     # pytest 單元測試(不需要真實影片)
frontend/
  index.html                 # 上傳影片 + 圖表儀表板(呼叫 backend API,單一靜態頁面)
docs/                          # 純前端版本,可直接部署到 GitHub Pages
  index.html                   # 上傳影片 + 圖表儀表板(分析全部在瀏覽器內執行)
  js/
    pose.js                    # MediaPipe Tasks Vision(瀏覽器 WASM)姿勢估計 + 影片抽幀
    app.js                     # UI 邏輯與圖表渲染
    pipeline/                  # 與 backend/app/pipeline 對應的 JS 版本
      features.js / hit_detection.js / classifier.js / stats.js / config.js / index.js
  tests/                        # Node 內建測試(node --test),對齊 backend 的 pytest 測試
```

## 安裝與執行(Python 後端版:`backend/` + `frontend/`)

需要 Python 3.11+,以及系統的 OpenGL/EGL 函式庫(MediaPipe 執行期需要):

```bash
sudo apt-get install -y libegl1 libgl1 libgles2

cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

第一次執行分析時,`pose.py` 會自動下載 MediaPipe 的 pose landmarker 模型檔(約 6MB)到 `backend/models/`(已加入 `.gitignore`,不會進版本控制)。

### 啟動網頁服務

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

開啟 http://127.0.0.1:8000/static/index.html 上傳影片並查看分析結果。

### 命令列分析

```bash
cd backend
source .venv/bin/activate
python scripts/analyze_video.py path/to/match.mp4 --out result.json
```

### 執行測試

```bash
cd backend
source .venv/bin/activate
python -m pytest
```

核心邏輯(擊球偵測、分類規則、統計聚合)的測試使用合成的姿勢關鍵點資料,不需要真實影片或安裝 MediaPipe/OpenCV 也能跑;只有 `pose.py`/`video_io.py` 這層才真的呼叫 OpenCV/MediaPipe。

## 安裝與執行(純前端版:`docs/`)

不需要安裝任何東西,`docs/` 本身就是靜態網站:

```bash
cd docs
python3 -m http.server 8000   # 或任何你習慣的靜態伺服器
```

開啟 http://127.0.0.1:8000/,上傳影片即可(第一次執行會從 CDN 下載 MediaPipe 的 WASM 執行檔與姿勢模型,約數 MB,之後瀏覽器會快取)。部署到 GitHub Pages 的方式見上方「部署到 GitHub Pages」段落。

### 執行測試(`docs/`)

```bash
cd docs
npm test   # 等同 node --test tests/*.test.js
```

這些測試對齊 `backend/tests/` 的 pytest 測試,同樣只用合成資料驗證擊球偵測/分類/統計邏輯,不需要瀏覽器或 MediaPipe。瀏覽器內 MediaPipe WASM 的整合(影片解碼、姿勢估計呼叫)已用 Playwright 手動驗證過,能正常載入模型並產生分析結果。

## Roadmap

- [ ] 收集標註過的壁球影片,訓練學習型動作分類器取代目前的幾何規則
- [ ] 支援多球員追蹤(目前只處理畫面中最主要的一位)
- [ ] 球體偵測與軌跡視覺化(熱區圖 / shot placement)
- [ ] 依偵測到的擊球時間自動剪輯精華回合(rally highlight clipping)
