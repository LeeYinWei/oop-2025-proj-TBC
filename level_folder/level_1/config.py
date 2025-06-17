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
            "is_boss": False, # If this is meant to be a boss, set to True. Let's assume for now it's not.
            "is_limited": True,
            "spawn_count": 2,
            "weight": 0.3,
            "tower_hp_percent": 100, # If this variant comes out earlier than a boss, consider its HP % trigger
            "initial_delay": 10000,
            "spawn_interval_1": 2000,
            "hp_multiplier": 2.5,  # Higher HP for version2
            "atk_multiplier": 2.0  # Higher attack for version2
        },
        {
            "type": "fast",
            "variant": "normal",
            "is_boss": False,
            "is_limited": True,
            "spawn_count": 5,
            "weight": 0.3,
            "tower_hp_percent": 80, # This enemy type starts spawning when tower HP is at 80% or below
            "initial_delay": 7000,
            "spawn_interval_1": 2000,
            "hp_multiplier": 1,
            "atk_multiplier": 1
        }
    ],
    "spawn_interval": 3000,
    "survival_time": 60, # Survival time in seconds. Assuming this is milliseconds in your game logic?
                        # If it's 60 seconds, ensure your game loop converts it to milliseconds for comparisons.
    "background_path": "images/background/background3.png", # Corrected path if "background/" means base game folder
    "our_tower": {
        "y": 140,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "images/tower/our_tower.png", # Corrected path
        "color": (100, 100, 255)
    },
    "enemy_tower": {
        "y": 150,
        "width": 350,
        "height": 350,
        "hp": 600,
        "tower_path": "images/tower/enemy_tower.png" # Corrected path
    },
    "tower_distance": 900,
    "initial_budget": 1000, # <--- ADD THIS LINE with a starting budget for this level
    "music_path": "audio/TBC/117.ogg", # <--- ADD THIS LINE with the path to the level's background music
    "switch_music_on_boss": True, # <--- ADD THIS LINE (set to True if you want music to change when a boss appears)
    "boss_music_path": "audio/TBC/118.ogg" # <--- ADD THIS LINE (path to boss music, only relevant if switch_music_on_boss is True)
}