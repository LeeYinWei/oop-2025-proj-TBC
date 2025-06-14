# oop-2025-proj-TBC

本專案為 OOP-2025 課程專案。以下是專案的目錄結構概覽以及主要檔案和資料夾的用途說明。

## 專案結構
---

## 檔案與資料夾說明：

* **`main.py`**: 應用程式的入口點。負責初始化遊戲並啟動遊戲迴圈。
* **`game/`**:
    * `__init__.py`: 這個特殊檔案將 `game` 目錄標記為一個 Python 套件 (package)。它用於控制當 `from game import *` 時會導入哪些內容，通常也用於套件級別的初始化或公開主要元件。
    * `game_loop.py`: 編排遊戲事件的主要序列，包括更新遊戲狀態、處理輸入和渲染畫面。
    * `constants.py`: 儲存不可變的值，例如螢幕尺寸、速度、顏色或其他固定參數。
    * `config_loader.py`: 負責讀取和解析遊戲配置文件（例如 `JSON`, `YAML`），並根據載入的資料設定遊戲參數。
    * `battle_logic.py`: 包含控制戰鬥遭遇戰的演算法和規則。
    * `ui.py`: 處理使用者介面的所有方面，包括繪製選單、記分板、生命條和其他螢幕上的元素。
* **`game/entities/`**:
    * `__init__.py`: 類似於 `game/__init__.py`，這個檔案將 `entities` 標記為一個子套件，可以用於導出特定的實體類別或資料處理器。
    * `cat.py`: 定義 `Cat` 類別，包含其屬性（例如生命值、攻擊力、位置）和行為（例如移動、攻擊動畫）。
    * `cat_data.py`: 儲存或載入不同類型「貓咪」或其變體的特定資料設定，與其核心行為分開。
    * `enemy.py`: 定義基礎 `Enemy` 類別或特定的敵人類型，包含其屬性和動作。
    * `enemy_data.py`: 管理各種敵人類型的資料，例如敵人屬性、掉落率或獨特能力。
    * `level.py`: 定義遊戲關卡的結構和屬性（例如佈局、生成點）。
    * `level_data.py`: 儲存每個遊戲關卡的特定數據集，例如敵人波次、環境危險或背景資源。
    * `tower.py`: 定義 `Tower` 實體，它可能是防禦性建築或中心目標。
    * `smokeeffect.py`: 實現在遊戲中煙霧效果的視覺和可能的功能方面。
    * `shockwaveeffect.py`: 實現在遊戲中衝擊波效果的視覺和功能方面，可能涉及範圍傷害或擊退。
    * `soul.py`: 定義 `Soul` 實體，它可能是可收集物、資源或一種敵人類型。
* **`game/cat_folder/XX`**:
    * `walking`:走路動畫
    * `attacking`:攻擊動畫
    * `config.py`:角色資料
    
* **`game/enemy_folder/XX`**:
    * `walking`:走路動畫
    * `attacking`:攻擊動畫
    * `config.py`:敵人資料
* **`game/level_folder/level_X`**:
    * `config.py`:關卡資料

* **`game/background`**:
    * `background1.png`:背景
    
## 遊戲流程:

## 玩法:
