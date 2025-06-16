# oop-2025-proj-TBC  蝸牛大冒險

本專案為 OOP-2025 課程專案。以下是專案的目錄結構概覽以及主要檔案和資料夾的用途說明。

## 專案結構
oop-2025-proj-TBC/

├── main.py              # 應用程式入口點，初始化並啟動遊戲

├── game/

│   ├── init.py      # 標記為 Python 套件，控制模組導入

│   ├── game_loop.py     # 管理遊戲事件循環、狀態更新和渲染

│   ├── constants.py     # 儲存遊戲常數（如螢幕尺寸、速度、顏色）

│   ├── config_loader.py # 讀取並解析遊戲配置文件（如 JSON）

│   ├── battle_logic.py  # 處理戰鬥邏輯和規則

│   ├── ui.py            # 負責繪製使用者介面（如選單、生命條）

│   └── entities/

│       ├── init.py  # 標記為子套件

│       ├── cat.py       # 定義 Cat 類別及其行為

│       ├── cat_data.py  # 儲存貓咪類型和屬性數據

│       ├── enemy.py     # 定義 Enemy 類別及其行為

│       ├── enemy_data.py # 管理敵人屬性數據

│       ├── level.py     # 定義關卡結構

│       ├── level_data.py # 儲存關卡數據（如敵人波次）

│       ├── tower.py     # 定義 Tower 實體

│       ├── smokeeffect.py # 實現煙霧效果

│       ├── shockwaveeffect.py # 實現衝擊波效果

│       └── soul.py      # 定義 Soul 實體（資源或敵人）

│   ├── cat_folder/

│   │   └── XX/

│   │       ├── walking/ # 走路動畫

│   │       ├── attacking/ # 攻擊動畫

│   │       └── config.py # 角色資料

│   ├── enemy_folder/

│   │   └── XX/

│   │       ├── walking/ # 走路動畫

│   │       ├── attacking/ # 攻擊動畫

│   │       └── config.py # 敵人資料

│   ├── level_folder/

│   │   └── level_X/

│   │       └── config.py # 關卡資料

│   └── background/

│       └── background1.png # 背景圖片

└── background/

└── backgroundStory.txt # 開場動畫故事內容

## 功能特性
- **開場動畫**：從下往上滑動的故事介紹，可點擊 "Skip" 跳過。
- **關卡選擇**：選擇可玩關卡並組建貓咪隊伍（最多 10 隻）。
- **戰鬥系統**：實時部署貓咪，管理預算和冷卻時間，與敵人戰鬥。
- **暫停與結束**：提供暫停選單和遊戲結束畫面。
- **進度保存**：通關關卡後保存到 `completed_levels.json`。
- **視覺效果**：包含煙霧、衝擊波和靈魂收集（未來功能）。

## 玩法:
- **開場**
執行main.py後, 會出現開場畫面, 你可以點擊skip, 或是看完整個~~很唬爛的~~介紹
![開場背景](intro/intro_screen.png "遊戲開場畫面背景")
- **菜單**
到了菜單, 關卡會先鎖住level 2以後的關卡, 確保你有能力通過比較前面簡單的關卡 ~~（可能後面比較簡單, 反正原版遊戲有這個案例）~~, 通過level 1可以玩level 2, 以此類推
另外, 點選可以出擊的角色, 亮綠燈代表你已經帶上, 灰色的話代表你還沒帶, 至多10隻 ~~實際上只有五隻角色~~
![菜單](intro/level_selection.png "菜單畫面")
- **戰鬥**
到了battle畫面, 點選鍵盤上的1出擊basic, 2出擊speedy, 以此類推, 另外可以按暫停鍵暫停遊戲
![戰鬥](intro/battle.png "戰鬥畫面")
- **輸贏**
若敵方塔血=0時, 代表我方勝利
反之, 就是敵方勝利
![win](intro/victory.png "勝利畫面")
![loss](intro/loss.png "失敗畫面")
## 需求與安裝
### 必要依賴
- Python 3.8 或更高版本
- Pygame 2.0 或更高版本

### 安裝步驟
1. 克隆專案到本地：
   ```bash
   git clone https://github.com/yourusername/oop-2025-proj-TBC.git
   cd oop-2025-proj-TBC
2. 設定虛擬環境（如果有意保持整潔）
    ```bash
    python -m venv venv
    source venv/bin/activate  # Linux/Mac
    venv\Scripts\activate     # Windows
3. 安裝pygame
    ```bash
    pip install pygame
4. 執行main.py
    ```bash
    python3 main.py
## class diagram
![classDiagram](https://www.plantuml.com/plantuml/png/hLRDRXit4BxhAVQe8BOVG8SWW14K1T8UclPG10OnMeuaGbnoGGubgqNVlVpPdQKeHqY0NEJbDvp_RuR-w0aSXK6lUWtUTyz0tR-hhdjytNGxRO7IzwNwfik8cywJImS_8ifAU5QI3fjEcNmweDeVY8_A2o22_gZCVjDjhTK91QC6uGc8hJBaI90QSB47NZWaXq0e5miJ9AIAEgP7ZgSMEUn9MSEslBOab97uEaFlYyT9PTrOUvTkX542uThOSr8gc7HmNllU8PfytYE9v6nTQUJyWXUusqM9N_V1EJHLTgnP2YJ-iGQBWS6UqjT_gwa_dmmEb_iTKbvihVTSe5mtFyBP27-m_V4C9wo4OwNQzXFe-BtTRGhweydVB-ETqgGlWYCA2GFiSLt-r5qx6Xlrjb6vBkIVzeok5F9I8hwROLkf0Lx55T1RGz2J66sy7eklbQVxYTsFV8dqozoqJxc2zvkVud8WLV0LA8E3Q_QtmtNBxOufycOAa6D1AS0XhDFjyRA70P_-Y70LkmtwNi3izvl-sDJVlu61_TopBNWKI-C6PSg9Yv3uw1cnVHz6XRB0fJkSoWcKXgsEzd8O54QDNwFYGz9-ITSSQimErmtDg_W-umcdN0qCopR3DB4YhSt9xrUf-cpsiGnbD8Fk17hfJd0d5O7hxPS8l7Ss62b6e0FRjy49IcJU54ulFbiqdtbDik4S1KhHsv2Pcy9Bk0PF8Wjp89K4j1PQ3OfGbWkyZjbtRyrExLadbT0ZbP1yuNv_m3YNRzXYCYp5_GK6_6pjMEfRkC6K-nBS3dfCabx7MM512llfEK59bg3cfV6e2ujrQXvNXE4UQ6vQr7WfSpwC6badYZrcfUhkCz3BN0h5RS-hk_JT1ZsZQK8AE8zvsPHih1d_bn_gUTl4fhlR8FUO-DoxnEzhmf4bqDELqgBh9L8M-Mo4uKd10IscoXF0PS-LQrxukORY8eOow1iUUKxlRM7HEs8IZak6sq1aJLgsDQkZ9sTRtulWPbNkGA9GvbPm4NQtyqWtzSWQeCS3y78T85h8_DFMZfdVlrk32x__-ZKp-xssC15B5196ZwAQV9LVYi9_iRnM3zq4LKzMSj8EIDcjhOF9taDN6FtGNOz5TUw1edXdayTs47XrifkSS51iVYhGRFMQFmzTHM0MvXOzT2rXRaAgQ5xaTVCvueKbpOF58OyGF8e1JU2ea-vjRcYaA3U-bLxXV4fBYkA__Fg3FOj1UPzQEnUnxBjtJ852nf_T-6AsZRk4DTCvdfc_RrJfx60KXA-qJZzvecSB0xoMo3WANfnrsPJP2p1gIDFqNK6aAU7zRnyVFtJFG0sITsk3vHtOOCqoRQKsw0RYBNC5byT-mPwUFdJJVxjR8D8OamyU_IhETPBD5oFiq4XqVfKjL856KIA3zIhLPJNxvOIZlAm-NyauzKgw-XWzX47_3m00 "class diagram")
