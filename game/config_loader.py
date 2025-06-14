import os
import sys
import importlib.util

def load_config(folder, subfolder, config_name="config"):
    config_path = os.path.join(folder, subfolder, f"{config_name}.py")
    if not os.path.exists(config_path):
        print(f"Config file not found: {config_path}")
        sys.exit()
    spec = importlib.util.spec_from_file_location(config_name, config_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if folder == "level_folder":
        return module.level_config
    return module.cat_config if folder == "cat_folder" else module.enemy_config

