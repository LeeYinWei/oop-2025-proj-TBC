level_config = {
    "name": "Level 3",
    "enemy_types": [
        {
            "type": "basic",
            "variant": "normal",  # 唯一標識
            "is_boss": False,
            "is_limited": False,
            "spawn_count": 0,  # 無限制生成，spawn_count 設為 0 表示無上限
            "weight": 0.4,
            "tower_hp_percent": 100,
            "initial_delay": 2000,  # 2 秒後開始出擊
            "spawn_interval_1": 2000  # 出擊間隔：2 秒
        },
        {
            "type": "fast",
            "variant": "standard",  # 唯一標識
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 20,
            "weight": 0.3,
            "tower_hp_percent": 100,
            "initial_delay": 4000,  # 4 秒後開始出擊
            "spawn_interval_1": 1500  # 出擊間隔：1.5 秒
        },
        {
            "type": "tank",
            "variant": "boss",  # 唯一標識
            "is_boss": True,
            "is_limited": True,
            "spawn_count": 5,
            "weight": 0.3,
            "tower_hp_percent": 70,
            "initial_delay": 6000,  # 6 秒後開始出擊
            "spawn_interval_1": 4000  # 出擊間隔：4 秒
        }
    ],
    "spawn_interval": 2000,  # 保留作為預設間隔（可忽略）
    "survival_time": 120,
    "background_path": "background/background1.png",
    "our_tower": {
        "x": 680,
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 1500,
        "tower_path": "tower/our_tower.png"
        # "color": (100, 100, 255) 註解掉，保持與你提供一致
    },
    "enemy_tower": {
        "x": -50,
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 1000,
        "tower_path": "tower/enemy_tower.png"
    }
}