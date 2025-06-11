level_config = {
    "name": "Level 2",
    "enemy_types": [
        {
            "type": "basic",
            "variant": "normal",  # 唯一標識
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 15,
            "weight": 0.5,
            "tower_hp_percent": 100,
            "initial_delay": 3000,  # 3 秒後開始出擊
            "spawn_interval_1": 2500  # 出擊間隔：2.5 秒
        },
        {
            "type": "fast",
            "variant": "standard",  # 唯一標識
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 10,
            "weight": 0.3,
            "tower_hp_percent": 90,
            "initial_delay": 5000,  # 5 秒後開始出擊
            "spawn_interval_1": 2000  # 出擊間隔：2 秒
        },
        {
            "type": "tank",
            "variant": "boss",  # 唯一標識
            "is_boss": True,
            "is_limited": True,
            "spawn_count": 3,
            "weight": 0.2,
            "tower_hp_percent": 50,
            "initial_delay": 7000,  # 7 秒後開始出擊
            "spawn_interval_1": 5000  # 出擊間隔：5 秒
        }
    ],
    "spawn_interval": 2500,  # 保留作為預設間隔（可忽略）
    "survival_time": 90,
    "background_path": "background/background1.png",
    "our_tower": {
        "x": 680,
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 1200,
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