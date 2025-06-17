# entities/__init__.py

# 匯入主要 class
from .cat import Cat
from .enemy import Enemy
from .level import Level
from .ymanager import YManager

# 匯入輔助 class
from .gaseffect import GasEffect
from .electriceffect import ElectricEffect
from .physiceffect import PhysicEffect
from .smokeeffect import SmokeEffect
from .csmokeeffect import CSmokeEffect
from .shockwaveeffect import ShockwaveEffect


from .soul import Soul
# 匯入常數

# 匯入其他模組
from .tower import Tower

# 匯入資料 (變數)
from .cat_data import cat_types, cat_costs, cat_cooldowns, load_cat_images
from .enemy_data import enemy_types
from .level_data import levels

# __all__ 是可選的，但推薦寫清楚導出內容
__all__ = [
    "Cat", "Enemy", "Level",
    "cat_types", "cat_costs", "cat_cooldowns",
    "enemy_types", "levels"
]
