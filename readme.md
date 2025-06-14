file structure

oop-2025-proj-TBC/
├── main.py
└── game/
├── init.py ← 整合整個遊戲模組對外的公開內容
├── game_loop.py
├── constants.py
├── config_loader.py
├── battle_logic.py
├── ui.py
├── constants.py #新增constants.py 放BOTTOM_Y
└── entities/ #新增
├── init.py ← 整合所有角色、資料等模組
├── cat.py
├── cat_data.py #用cat建立cat相關資料
├── enemy.py
├── enemy_data.py #用enemy建立enemy相關資料
├── level.py
└── level_data.py #用level建立level相關資料
└── tower.py
└── smokeeffect.py
└── shockwaveeffect.py
└── soul.py

