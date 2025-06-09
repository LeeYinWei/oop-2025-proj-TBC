level_config = {
    "name": "Level 3: Boss Fight",
    "enemy_types": [
        {"type": "fast", "weight": 0.4, "is_limited": False, "spawn_count": 0, "tower_hp_percent": 100, "is_boss": False},
        {"type": "tank", "weight": True, "is_limited": True, "spawn_count": 1, "tower_hp_percent": 30, "is_boss": True}
    ],
    "spawn_interval": 1500,
    "enemy_tower_hp": 2000,
    "survival_time": 60000  # 無限模式，存活60秒
}