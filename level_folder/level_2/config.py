level_config = {
    "name": "Level 2: Medium",
    "enemy_types": [
        {"type": "basic", "weight": 0.5, "is_limited": True, "spawn_count": 10, "tower_hp_percent": 100, "is_boss": False},
        {"type": "fast", "weight": 0.3, "is_limited": False, "spawn_count": 0, "tower_hp_percent": 100, "is_boss": False},
        {"type": "tank", "weight": 0.2, "is_limited": True, "spawn_count": 5, "tower_hp_percent": 50, "is_boss": False}
    ],
    "spawn_interval": 2000,
    "enemy_tower_hp": 1500,
    "survival_time": 0
}