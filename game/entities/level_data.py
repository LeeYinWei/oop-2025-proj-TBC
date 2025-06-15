# game/entities/level_data.py
import os
import sys
from game.entities.level import Level
from game.config_loader import load_config
import re

levels = []
level_folder = "level_folder"

def extract_level_number(subfolder):
    """Extract numeric part from subfolder name (e.g., 'level_2' -> 2)."""
    match = re.match(r'level_(\d+)', subfolder)
    return int(match.group(1)) if match else float('inf')

if os.path.exists(level_folder):
    # Sort subfolders by level number
    subfolders = sorted(
        [f for f in os.listdir(level_folder) if os.path.isdir(os.path.join(level_folder, f))],
        key=extract_level_number
    )
    for level_subfolder in subfolders:
        if os.path.isdir(os.path.join(level_folder, level_subfolder)):
            try:
                config = load_config(level_folder, level_subfolder)
                levels.append(Level(
                    config["name"],
                    config["enemy_types"],
                    config["spawn_interval"],
                    config["survival_time"],
                    config["background_path"],
                    config["our_tower"],
                    config["enemy_tower"],
                    config["tower_distance"]
                ))
            except Exception as e:
                print(f"Error loading level config for '{level_subfolder}': {e}")
else:
    print(f"Directory '{level_folder}' not found")
    sys.exit()