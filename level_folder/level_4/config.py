level_config = {
    "name": "Level 4",
    "enemy_types": [
        {
            "type": "tank",
            "variant": "boss",
            "is_boss": True,
            "is_limited": True,
            "spawn_count": 1,
            "weight": 0.3,
            "tower_hp_percent": 100,
            "initial_delay": 6000,
            "spawn_interval_1": 4000
        }
    ],
    "spawn_interval": 2000,
    "survival_time": 120,
    "background_path": "background/background1.png",
    "our_tower": {
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "tower/our_tower.png"
    },
    "enemy_tower": {
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 6000,
        "tower_path": "tower/enemy_tower.png"
    },
    "tower_distance": 800
}