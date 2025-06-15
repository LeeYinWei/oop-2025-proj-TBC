import os
import sys
from game.entities.cat import Cat
from game.config_loader import load_config
from collections import defaultdict


cat_types = {}
cat_cooldowns = {}
cat_costs = {}
cat_button_images = defaultdict(lambda: {
    "idle": None,
    "hover": None,
    "pressed": None
})

cat_folder = "cat_folder"

if os.path.exists(cat_folder):
    for cat_type in os.listdir(cat_folder):
        if os.path.isdir(os.path.join(cat_folder, cat_type)):
            try:
                config = load_config(cat_folder, cat_type)
                cat_types[cat_type] = lambda x, y, cfg=config: Cat(
                    x, y, cfg["hp"], cfg["atk"], cfg["speed"], cfg["color"],
                    cfg["attack_range"], cfg["is_aoe"], cfg["width"], cfg["height"],
                    cfg["kb_limit"], cfg.get("idle_frames"), cfg.get("move_frames"),
                    cfg.get("windup_frames"), cfg.get("attack_frames"), cfg.get("recovery_frames"),
                    cfg.get("kb_frames"), cfg["windup_duration"], cfg["attack_duration"],
                    cfg["recovery_duration"],
                    target_attributes=cfg.get("target_attributes", []),
                    immunities=cfg.get("immunities", {}),
                    boosts=cfg.get("boosts", {}),
                    status_effects_config=cfg.get("status_effects", {}),
                    attack_interval=cfg.get("attack_interval", 1000),
                    delta_y=cfg["delta_y"] if "delta_y" in cfg else 0
                )
                cat_cooldowns[cat_type] = config["cooldown"]
                cat_costs[cat_type] = config["cost"]
                cat_button_images[cat_type]["idle"] = config.get("ibtn_idle")
                cat_button_images[cat_type]["hover"] = config.get("ibtn_hover")
                cat_button_images[cat_type]["pressed"] = config.get("ibtn_pressed")
            except Exception as e:
                print(f"Error loading cat config for '{cat_type}': {e}")
else:
    print(f"Directory '{cat_folder}' not found")
    sys.exit()
