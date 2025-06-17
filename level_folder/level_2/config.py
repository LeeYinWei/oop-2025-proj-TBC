level_config = {
    "name": "Level 2",
    "enemy_types": [
        {
            "type": "basic",
            "variant": "normal",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 15,
            "weight": 0.5,
            "tower_hp_percent": 100,
            "initial_delay": 3000,
            "spawn_interval_1": 5000
        },
        {
            "type": "fast",
            "variant": "standard",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 10,
            "weight": 0.3,
            "tower_hp_percent": 90,
            "initial_delay": 5000,
            "spawn_interval_1": 10000
        },
        {
            "type": "tank",
            "variant": "boss",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 1,
            "weight": 0.2,
            "tower_hp_percent": 50,
            "initial_delay": 7000,
            "spawn_interval_1": 5000
        }
    ],
    "spawn_interval": 2500,
    "survival_time": 90,
    "background_path": "images/background/background4.png",
    "our_tower": {
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "images/tower/our_tower.png"
    },
    "enemy_tower": {
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "images/tower/enemy_tower.png"
    },
    "tower_distance": 900,
    "initial_budget": 1000, # <--- ADD THIS LINE with a starting budget for this level
    "music_path": "audio/TBC/118.ogg", # <--- ADD THIS LINE with the path to the level's background music
    "switch_music_on_boss": False, # <--- ADD THIS LINE (set to True if you want music to change when a boss appears)
    "boss_music_path": "audio/TBC/119.ogg" # <--- ADD THIS LINE (path to boss music, only relevant if switch_music_on_boss is True)
}