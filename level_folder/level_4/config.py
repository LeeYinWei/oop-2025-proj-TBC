level_config = {
    "name": "Level 4",
    "enemy_types": [
        # {
        #     "type": "basic",
        #     "variant": "normal",
        #     "is_boss": False,
        #     "is_limited": False,
        #     "spawn_count": 0,
        #     "weight": 0.4,
        #     "tower_hp_percent": 100,
        #     "initial_delay": 7000,
        #     "spawn_interval_1": 10000,
        #     "hp_multiplier": 1.0,
        #     "damage_multiplier": 1.0,
        # },
        # {
        #     "type": "fast",
        #     "variant": "standard",
        #     "is_boss": False,
        #     "is_limited": True,
        #     "spawn_count": 20,
        #     "weight": 0.3,
        #     "tower_hp_percent": 100,
        #     "initial_delay": 4000,
        #     "spawn_interval_1": 1500,
        #     "hp_multiplier": 1.2,
        #     "damage_multiplier": 1.1,
        # },
        {
            "type": "tank",
            "variant": "boss",
            "is_boss": True,
            "is_limited": True,
            "spawn_count": 1,
            "weight": 0.3,
            "tower_hp_percent": 100,
            "initial_delay": 6000,
            "spawn_interval_1": 4000,
            "hp_multiplier": 2,
            "damage_multiplier": 10,
        }
    ],
    "spawn_interval": 2000,
    "survival_time": 120,
    "background_path": "images/background/background5.png",
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
        "hp": 6000,
        "tower_path": "images/tower/enemy_tower.png"
    },
    "tower_distance": 900,
    "initial_budget": 1000, # <--- ADD THIS LINE with a starting budget for this level
    "music_path": "audio/TBC/178.ogg", # <--- ADD THIS LINE with the path to the level's background music
    "switch_music_on_boss": False, # <--- ADD THIS LINE (set to True if you want music to change when a boss appears)
    "boss_music_path": "audio/TBC/118.ogg" # <--- ADD THIS LINE (path to boss music, only relevant if switch_music_on_boss is True)
}
