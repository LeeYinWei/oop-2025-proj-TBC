import asyncio
import pygame
from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager
from .battle_logic import update_battle
from .ui import draw_level_selection, draw_game_ui, draw_end_screen

async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 24)
    end_font = pygame.font.SysFont(None, 96)
    game_state = "level_selection"
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]  # Start with 2 cats
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []  # 僅保留 shockwave_effects
    #cat_y = 450
    #enemy_y = 450
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    last_budget_increase_time = -333
    total_budget_limitation = 16500
    current_budget = 1000
    budget_rate = 33
    status = 0
    level_start_time = 0
    cat_y_manager = YManager(base_y=525, min_y=300, max_slots=30)
    enemy_y_manager = YManager(base_y=490, min_y=300, max_slots=30)
    # Map keys 1-0 to up to 10 cats
    cat_key_map = {}
    for i, cat_type in enumerate(selected_cats[:10]):
        cat_key_map[pygame.K_1 + i] = cat_type
    # Initialize buttons for selected cats (120px wide to fit 10)
    button_rects = {cat_type: pygame.Rect(50 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}

    while True:
        current_time = pygame.time.get_ticks()
        if game_state == "level_selection":
            cat_rects = draw_level_selection(screen, levels, selected_level, selected_cats, font)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        if pygame.Rect(50, 100 + i * 60, 200, 50).collidepoint(pos):
                            selected_level = i
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            # Update key mappings for up to 10 cats
                            cat_key_map = {}
                            for i, cat_type in enumerate(selected_cats[:10]):
                                cat_key_map[pygame.K_1 + i] = cat_type
                            # Update button positions (120px spacing)
                            button_rects = {cat_type: pygame.Rect(50 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                    game_state = "playing"
                    current_level = levels[selected_level]
                    current_level.reset_towers()
                    our_tower = current_level.our_tower
                    enemy_tower = current_level.enemy_tower
                    for et in current_level.enemy_types:
                        key = (et["type"], et.get("variant", "default"))
                        current_level.spawned_counts[key] = 0
                    current_level.all_limited_spawned = False
                    cats = []
                    souls = []
                    enemies = []
                    shockwave_effects = []  # 重置 shockwave_effects
                    current_budget = 1000
                    last_enemy_spawn_time = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in current_level.enemy_types}
                    last_budget_increase_time = -333
                    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                    status = 0
                    level_start_time = current_time
            pygame.display.flip()
        elif game_state == "playing":
            current_level = levels[selected_level]

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map and current_budget >= cat_costs[cat_key_map[event.key]]:
                        current_budget -= cat_costs[cat_key_map[event.key]]
                        cat_type = cat_key_map[event.key]
                        if current_time - last_spawn_time[cat_type] >= cat_cooldowns[cat_type]:
                            our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                            cat_y, cat_slot = cat_y_manager.get_available_y()
                            cat = cat_types[cat_type](our_tower_center, cat_y)
                            cat.slot_index = cat_slot  # 儲存它使用的 slot
                            start_x = our_tower_center - cat.width / 2
                            cat.x = start_x
                            cats.append(cat)
                            last_spawn_time[cat_type] = current_time
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", "default"))
                if (not et.get("is_limited", False) or current_level.spawned_counts.get(key, 0) < et.get("spawn_count", 0)) and tower_hp_percent <= et.get("tower_hp_percent", 100):
                    interval = et.get("spawn_interval_1", current_level.spawn_interval)
                    if current_time - current_level.last_spawn_times.get(key, 0) >= interval:
                        enemy_tower_center = current_level.enemy_tower.x + current_level.enemy_tower.width / 2
                        config = current_level.enemy_configs.get(et["type"], {})
                        enemy_y, enemy_slot = enemy_y_manager.get_available_y()
                        enemy = enemy_types[et["type"]](
                            enemy_tower_center, enemy_y,
                            is_b=et.get("is_boss", False),
                            cfg=config  # Pass the config to get multipliers
                        )
                        enemy.slot_index = enemy_slot
                        start_x = enemy_tower_center - enemy.width / 2
                        enemy.x = start_x
                        enemies.append(enemy)
                        current_level.spawned_counts[key] += 1
                        current_level.last_spawn_times[key] = current_time
            current_level.all_limited_spawned = current_level.check_all_limited_spawned()
            # 更新所有角色的狀態效果
            for cat in cats:
                cat.update_status_effects(current_time)
            #print(f"enemies count: {len(enemies)}")
            for enemy in enemies:
                enemy.update_status_effects(current_time)
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects)
            souls[:] = [soul for soul in souls if soul.update()]
            draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map)
            for soul in souls:
                soul.draw(screen)
            for shockwave in shockwave_effects:
                shockwave.draw(screen)
            for cat in cats:
                cat.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            our_tower.draw(screen)
            if enemy_tower:
                enemy_tower.draw(screen)
            pygame.display.flip()

            if our_tower.hp <= 0:
                status = "lose"
                game_state = "end"
                print("Our tower destroyed, game over.")
            elif enemy_tower:
                if enemy_tower.hp <= 0:
                    status = "victory"
                    game_state = "end"
                    print("Enemy tower destroyed, we win!")
                elif current_level.all_limited_spawned and not any(
                    et["is_limited"] is False for et in current_level.enemy_types
                ) and not enemies:
                    status = "victory"
                    game_state = "end"
                    print(enemies)
                    print("All enemies defeated, we win!")
                elif current_level.survival_time > 0 and (current_time - level_start_time) >= current_level.survival_time * 1000:
                    status = "victory"
                    game_state = "end"
                    print("Survival time reached, we win!")
        elif game_state == "end":
            current_level = levels[selected_level]
            draw_end_screen(screen, current_level, status, end_font, font)
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    game_state = "level_selection"
                    our_tower = None
                    enemy_tower = None
        await asyncio.sleep(1 / FPS)

