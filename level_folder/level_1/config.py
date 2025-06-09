level_config = {
    "name": "Level 1: Easy",
    "enemy_types": [
        {"type": "basic", "weight": 0.8, "is_limited": True, "spawn_count": 8, "tower_hp_percent": 100, "is_boss": False},
        {"type": "fast", "weight": 0.2, "is_limited": True, "spawn_count": 2, "tower_hp_percent": 100, "is_boss": False}
    ],
    "spawn_interval": 3000,
    "enemy_tower_hp": 1000,
    "survival_time": 0  # 不限定存活時間
}