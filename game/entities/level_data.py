import os
import sys
from game.entities.level import Level
from game.config_loader import load_config

levels = []
level_folder = "level_folder"

if os.path.exists(level_folder):
    for level_subfolder in os.listdir(level_folder):
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
