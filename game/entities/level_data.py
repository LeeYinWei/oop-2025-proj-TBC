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
                level_index = extract_level_number(level_subfolder) - 1  # Convert to 0-based index

                levels.append(Level(
                    config["name"],
                    config["enemy_types"],
                    config["spawn_interval"],
                    config["survival_time"],
                    config["background_path"],
                    config["our_tower"],
                    config["enemy_tower"],
                    config["tower_distance"],
                    # --- ADD THESE NEW ARGUMENTS ---
                    config["initial_budget"],
                    config.get("music_path", "audio/default_battle_music.ogg"), # Use .get() with default for optional keys
                    config.get("switch_music_on_boss", False),
                    config.get("boss_music_path", "audio/boss_music.ogg")
                ))
                print(f"Loaded level: {config['name']} at index {level_index}")
            except KeyError as e:
                # This error means a critical key like 'initial_budget' is missing in config.json
                print(f"Missing required config key '{e}' for level '{level_subfolder}', skipping this level")
            except Exception as e:
                print(f"Error loading level config for '{level_subfolder}': {e}, skipping this level")
else:
    print(f"Directory '{level_folder}' not found")
    sys.exit()

# Optional: Add a function to validate levels against completed_levels (if needed elsewhere)
def get_level_index_by_name(level_name):
    """Return the 0-based index of a level by its name."""
    for i, level in enumerate(levels):
        if level.name == level_name:
            return i
    return -1