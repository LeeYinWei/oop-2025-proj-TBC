level_config = {
    "name": "Level 1",
    "enemy_types": [
        {
            "type": "basic",
            "variant": "version1",  # 唯一標識
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 5,
            "weight": 0.5,
            "tower_hp_percent": 100,
            "initial_delay": 5000,
            "spawn_interval_1": 3000
        },
        {
            "type": "basic",
            "variant": "version2",  # 唯一標識
            "is_boss": True,
            "is_limited": True,
            "spawn_count": 2,
            "weight": 0.3,
            "tower_hp_percent": 100,
            "initial_delay": 7000,
            "spawn_interval_1": 2000,
        },
        {
            "type": "fast",
            "variant": "normal",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 5,
            "weight": 0.3,
            "tower_hp_percent": 80,
            "initial_delay": 7000,
            "spawn_interval_1": 2000
        }
    ],
    "spawn_interval": 3000,
    "survival_time": 60,
    "background_path": "background/background1.png",
    "our_tower": {
        "x": 680,
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 1000,
        "tower_path": "tower/our_tower.png",
        "color": (100, 100, 255)
    },
    "enemy_tower": {
        "x": -60,
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 1000,
        "tower_path": "tower/enemy_tower.png"
    }
}