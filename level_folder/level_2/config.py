level_config = {
    "name": "Level 2",
    "enemy_types": [
        {"type": "basic", "is_boss": False, "is_limited": True, "spawn_count": 15, "weight": 0.5, "tower_hp_percent": 100},
        {"type": "fast", "is_boss": False, "is_limited": True, "spawn_count": 10, "weight": 0.3, "tower_hp_percent": 90},
        {"type": "tank", "is_boss": True, "is_limited": True, "spawn_count": 3, "weight": 0.2, "tower_hp_percent": 50}
    ],
    "spawn_interval": 2500,
    "survival_time": 90,
    "background_path": "background/background1.png",
    "our_tower": {
        "x": 680,
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 1200,
        "tower_path": "tower/our_tower.png"
        #"color": (100, 100, 255)
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