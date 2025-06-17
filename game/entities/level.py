import pygame
import math
import sys
import os
import random
from game.entities.tower import Tower
from game.config_loader import load_config

class Level:
    def __init__(self, name, enemy_types, spawn_interval, survival_time, background_path,
                 our_tower_config, enemy_tower_config, tower_distance,
                 initial_budget, # <--- Added: Initial budget for the level
                 music_path="audio/default_battle_music.ogg", # <--- Added: Default level music path
                 switch_music_on_boss=False, # <--- Added: Flag to switch music for boss
                 boss_music_path="audio/boss_music.ogg"): # <--- Added: Boss music path
        self.name = name
        self.enemy_configs = {et["type"]: load_config("enemy_folder", et["type"]) for et in enemy_types}
        valid_attributes = {"紅", "黑", "天", "鐵", "異", "惡", "死", "古", "無"}
        self.enemy_types = []
        for et in enemy_types:
            et_copy = et.copy()
            enemy_type = et_copy["type"]
            config = self.enemy_configs.get(enemy_type, {})
            et_copy["attributes"] = config.get("attributes", [])
            et_copy["attributes"] = list(dict.fromkeys([attr for attr in et_copy["attributes"] if attr in valid_attributes]))
            self.enemy_types.append(et_copy)
        self.spawn_interval = spawn_interval
        self.survival_time = survival_time
        # Initialize spawned_counts for proper resetting
        self.spawned_counts = {(et["type"], et.get("variant", "default")): 0 for et in self.enemy_types}
        self.all_limited_spawned = False
        self.background = None
        try:
            self.background = pygame.image.load(background_path)
            self.background = pygame.transform.scale(self.background, (1280, 600))
        except pygame.error as e:
            print(f"Cannot load background image '{background_path}': {e}")
            pygame.quit()
            sys.exit()
        self.last_spawn_times = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in self.enemy_types}
        self.our_tower_config = our_tower_config
        self.enemy_tower_config = enemy_tower_config
        self.tower_distance = tower_distance

        # --- New Attributes for Level ---
        self.initial_budget = initial_budget
        self.music_path = music_path
        self.switch_music_on_boss = switch_music_on_boss
        self.boss_music_path = boss_music_path

        self.reset_towers() # Call reset_towers after all configs are set

    def reset_towers(self):
        SCREEN_WIDTH = 1280
        CENTER_X = SCREEN_WIDTH / 2
        our_tower_width = self.our_tower_config["width"]
        enemy_tower_width = self.enemy_tower_config["width"]
        tower_distance = self.tower_distance

        our_tower_center = CENTER_X + tower_distance / 2
        enemy_tower_center = CENTER_X - tower_distance / 2
        our_tower_x = our_tower_center - our_tower_width / 2
        enemy_tower_x = enemy_tower_center - enemy_tower_width / 2

        self.our_tower = Tower(
            x=our_tower_x,
            y=self.our_tower_config["y"],
            hp=self.our_tower_config["hp"],
            color=self.our_tower_config.get("color", (100, 100, 255)),
            tower_path=self.our_tower_config.get("tower_path"),
            width=our_tower_width,
            height=self.our_tower_config["height"]
        )
        self.enemy_tower = Tower(
            x=enemy_tower_x,
            y=self.enemy_tower_config["y"],
            hp=self.enemy_tower_config["hp"],
            tower_path=self.enemy_tower_config["tower_path"],
            width=enemy_tower_width,
            height=self.enemy_tower_config["height"],
            is_enemy=True
        )

    def reset_spawn_counts(self):
        """Resets the spawned counts for all enemy types and their last spawn times."""
        self.spawned_counts = {(et["type"], et.get("variant", "default")): 0 for et in self.enemy_types}
        self.last_spawn_times = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in self.enemy_types}
        self.all_limited_spawned = False # Reset this flag as well

    def check_all_limited_spawned(self):
        """Check if all limited enemies have been spawned."""
        for enemy_type in self.enemy_types:
            if enemy_type.get("is_limited", False):
                key = (enemy_type["type"], enemy_type.get("variant", "default"))
                spawn_count = enemy_type.get("spawn_count", 0)
                if spawn_count > 0 and self.spawned_counts.get(key, 0) < spawn_count:
                    return False
        return True