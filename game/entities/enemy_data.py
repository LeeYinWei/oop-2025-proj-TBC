# enemy_data.py
import os
import sys
from game.entities.enemy import Enemy
from game.config_loader import load_config

enemy_types = {}
enemy_folder = "enemy_folder"

if os.path.exists(enemy_folder):
    for enemy_type in os.listdir(enemy_folder):
        if os.path.isdir(os.path.join(enemy_folder, enemy_type)):
            try:
                config = load_config(enemy_folder, enemy_type)
                enemy_types[enemy_type] = lambda x, y, is_boss=False, cfg=config: Enemy(
                    x, y, cfg["hp"], cfg["speed"], cfg["color"], cfg["attack_range"], cfg["is_aoe"],
                    is_boss=is_boss,  # 使用 is_boss 替代 is_b
                    atk=cfg["atk"], kb_limit=cfg["kb_limit"],
                    width=cfg["width"], height=cfg["height"],
                    idle_frames=cfg.get("idle_frames"), move_frames=cfg.get("move_frames"),
                    windup_frames=cfg.get("windup_frames"), attack_frames=cfg.get("attack_frames"),
                    recovery_frames=cfg.get("recovery_frames"), kb_frames=cfg.get("kb_frames"),
                    windup_duration=cfg["windup_duration"], attack_duration=cfg["attack_duration"],
                    recovery_duration=cfg["recovery_duration"],
                    attack_interval=cfg.get("attack_interval", 1000),
                    hp_multiplier=cfg.get("hp_multiplier", 1.0),
                    atk_multiplier=cfg.get("atk_multiplier", 1.0),
                    reward= cfg.get("reward", 0),
                    attack_type=cfg["attack_type"] if "attack_type" in cfg else "gun"
                )
            except Exception as e:
                print(f"Error loading enemy config for '{enemy_type}': {e}")
else:
    print(f"Directory '{enemy_folder}' not found")
    sys.exit()