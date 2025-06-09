level_config = {
    "name": "Level 3",
    "enemy_types": [
        {"type": "basic", "is_boss": False, "is_limited": False, "spawn_count": 0, "weight": 0.4, "tower_hp_percent": 100},
        {"type": "fast", "is_boss": False, "is_limited": True, "spawn_count": 20, "weight": 0.3, "tower_hp_percent": 100},
        {"type": "tank", "is_boss": True, "is_limited": True, "spawn_count": 5, "weight": 0.3, "tower_hp_percent": 70}
    ],
    "spawn_interval": 2000,
    "survival_time": 120,
    "background_path": "background/background1.png",
    "our_tower": {
        "x": 860,
        "y": 120,
        "width": 100,
        "height": 450,
        "hp": 1500,
        "color": (100, 100, 255)
    },
    "enemy_tower": {
        "x": 10,
        "y": 360,
        "width": 120,
        "height": 100,
        "hp": 2000,
        "tower_path": "tower/tower1.png"
    }
}