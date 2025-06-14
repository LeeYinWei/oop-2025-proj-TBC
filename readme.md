# oop-2025-proj-TBC

This repository contains the project for OOP-2025. Below is an overview of the project's directory structure and the purpose of key files and folders.

## Project Structure

---

## File and Folder Explanations:

* **`main.py`**: The entry point of the application. This file is responsible for initializing the game and starting the game loop.
* **`game/`**:
    * `__init__.py`: This special file marks the `game` directory as a Python package. It's used to control what gets imported when `from game import *` is used, often used for package-level initialization or exposing key components.
    * `game_loop.py`: Orchestrates the main sequence of game events, including updating game state, handling input, and rendering.
    * `constants.py`: Stores immutable values such as screen dimensions, speeds, colors, or other fixed parameters. (Note: You had two `constants.py` entries; I've combined them into one logical explanation.)
    * `config_loader.py`: Responsible for reading and parsing game configuration files (e.g., `JSON`, `YAML`), setting up game parameters based on loaded data.
    * `battle_logic.py`: Contains the algorithms and rules governing combat encounters between entities.
    * `ui.py`: Handles all aspects of the User Interface, including drawing menus, scoreboards, health bars, and other on-screen elements.
* **`game/entities/`**:
    * `__init__.py`: Similar to the `game/__init__.py`, this file marks `entities` as a sub-package and can be used to export specific entity classes or data handlers.
    * `cat.py`: Defines the `Cat` class, including its properties (e.g., health, attack, position) and behaviors (e.g., movement, attack animations).
    * `cat_data.py`: Stores or loads specific data profiles for different types of "cats" or their variations, separate from their core behavior.
    * `enemy.py`: Defines the base `Enemy` class or specific enemy types, including their attributes and actions.
    * `enemy_data.py`: Manages data such as enemy stats, drop rates, or unique abilities for various enemy types.
    * `level.py`: Defines the structure and properties of game levels (e.g., layout, spawn points).
    * `level_data.py`: Stores specific data sets for each game level, such as enemy waves, environmental hazards, or background assets.
    * `tower.py`: Defines the `Tower` entity, which might be a defensive structure or a central objective.
    * `smokeeffect.py`: Implements the visual and perhaps functional aspects of smoke effects within the game.
    * `shockwaveeffect.py`: Implements the visual and functional aspects of shockwave effects, potentially involving area-of-effect damage or knockback.
    * `soul.py`: Defines the `Soul` entity, which could be a collectible, a resource, or an enemy type.
* **`game/cat_folder/XX`**:
    * `walking`:走路動畫
    * `attacking`:攻擊動畫
    * `config.py`:角色資料
    
* **`game/enemy_folder/XX`**:
    * `walking`:走路動畫
    * `attacking`:攻擊動畫
    * `config.py`:敵人資料
* **`game/level_folder/level_X`**:
    * `config.py`:關卡資料

* **`game/background`**:
    * `background1.png`:背景
    
## 遊戲流程:

## 玩法: