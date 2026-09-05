# 壁球影片分析 Squash Video Analysis

從壁球比賽影片自動偵測擊球時機,分類為正手 (forehand) / 反手 (backhand) / 發球 (serve),並統計回合數與擊球分布 —— 概念上類似 [Rally Vision](https://www.rallyvision.co) 這類運動影片分析工具的 MVP 版本。

## 目前的分析方式

這是一個 **v1 啟發式規則版本**,還不是訓練過的機器學習模型(目前沒有已標註的壁球影片資料集)。流程如下:

1. **抽幀** (`app/pipeline/video_io.py`):用 OpenCV 讀取影片,依 `SAMPLE_FPS`(預設 15fps)抽樣畫面,不需要每一幀都做姿勢估計。
2. **姿勢估計** (`app/pipeline/pose.py`):用 MediaPipe Pose(Tasks API)取得球員的關鍵點(手腕、手肘、肩膀、髖部)。
3. **擊球偵測** (`app/pipeline/hit_detection.py`):計算手腕移動速度,速度出現局部峰值且高於門檻值時視為一次擊球,並用 refractory period 避免同一次揮拍被算成多次。
4. **擊球分類** (`app/pipeline/classifier.py`):
   - 擊球瞬間手腕若「跨過」軀幹中線 → 反手,否則 → 正手。
   - 若是該回合第一顆球,且擊球點高於肩膀 → 發球。
5. **統計聚合** (`app/pipeline/stats.py`):兩次擊球間隔超過 `RALLY_GAP_SECONDS`(預設 4 秒)視為新的一回合,並統計各類型擊球次數。

### 已知限制

- 準確度會受鏡頭角度、球員遮擋、慣用手、多人同框等因素影響很大,`app/pipeline/config.py` 中的門檻值需要依實際場地/攝影機重新校調。
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
  index.html                 # 上傳影片 + 圖表儀表板(單一靜態頁面)
```

## 安裝與執行

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

## Roadmap

- [ ] 收集標註過的壁球影片,訓練學習型動作分類器取代目前的幾何規則
- [ ] 支援多球員追蹤(目前只處理畫面中最主要的一位)
- [ ] 球體偵測與軌跡視覺化(熱區圖 / shot placement)
- [ ] 依偵測到的擊球時間自動剪輯精華回合(rally highlight clipping)
