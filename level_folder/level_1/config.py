level_config = {
    "name": "Level 1",
    "enemy_types": [
        {
            "type": "basic",
            "variant": "version1",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 5,
            "weight": 0.5,
            "tower_hp_percent": 100,
            "initial_delay": 5000,
            "spawn_interval_1": 3000,
            "hp_multiplier": 1.0,  # Default multiplier for version1
            "atk_multiplier": 1.0   # Default multiplier for version1
        },
        {
            "type": "basic",
            "variant": "version2",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 2,
            "weight": 0.3,
            "tower_hp_percent": 100,
            "initial_delay": 10000,
            "spawn_interval_1": 2000,
            "hp_multiplier": 2.5,  # Higher HP for boss variant
            "atk_multiplier": 2.0  # Higher attack for boss variant
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
            "spawn_interval_1": 2000,
            "hp_multiplier": 1,  # Lower HP for fast variant
            "atk_multiplier": 1  # Slightly higher attack for fast variant
        }
    ],
    "spawn_interval": 3000,
    "survival_time": 60,
    "background_path": "background/background3.png",
    "our_tower": {
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "tower/our_tower.png",
        "color": (100, 100, 255)
    },
    "enemy_tower": {
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "tower/enemy_tower.png"
    },
    "tower_distance": 800
}