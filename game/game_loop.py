# game/game_loop.py
import json
import os
import asyncio
import pygame
from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager
from .battle_logic import update_battle
from .ui import draw_level_selection, draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen
# game/game_loop.py
# ... (previous imports and initial code remain the same)

async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 24)
    end_font = pygame.font.SysFont(None, 96)
    game_state = "intro"  # Changed to start with intro
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]  # Initial selection (e.g., first two cat types)
    
    # Load completed levels from file
    completed_levels = set()
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    completed_levels = set(loaded_data)
                else:
                    print(f"Invalid save data format in {save_file}, initializing empty set")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"Error loading completed levels or file not found: {e}, initializing empty set")
    
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    last_budget_increase_time = -333
    total_budget_limitation = 16500
    current_budget = 1000
    budget_rate = 33
    status = 0
    level_start_time = 0

    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    # Map keys 1-0 to up to 10 cats
    cat_key_map = {}
    for i, cat_type in enumerate(selected_cats[:10]):
        cat_key_map[pygame.K_1 + i] = cat_type
    button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}  # Moved to right side

    # Intro animation variables
    intro_start_time = pygame.time.get_ticks()
    intro_duration = 100000  # Increased to 10 seconds for slower movement
    y_offset = screen.get_height()  # Start from bottom

    # 淡入效果的持續時間和當前透明度
    fade_in_duration = 5000  # 5秒淡入
    current_fade_alpha = 0 # 從完全透明開始

    while True:
        current_time = pygame.time.get_ticks()
        if game_state == "intro":
            # 清除螢幕 (每次繪圖前都要做)
            screen.fill((0, 0, 0))

            # 計算淡入透明度
            if current_time - intro_start_time < fade_in_duration:
                fade_progress = (current_time - intro_start_time) / fade_in_duration
                current_fade_alpha = int(255 * fade_progress)
            else:
                current_fade_alpha = 255 # 淡入完成

            # 計算文字滾動進度
            text_scroll_start_time = intro_start_time + fade_in_duration # 文字在圖片淡入後開始滾動
            if current_time >= text_scroll_start_time:
                text_progress_time = current_time - text_scroll_start_time
                text_scroll_duration = intro_duration - fade_in_duration # 故事文字滾動的剩餘時間
                
                # 避免除以零
                if text_scroll_duration <= 0:
                    text_scroll_progress = 1.0
                else:
                    text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                
                # Ease-out effect for smoother sliding
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)
            else:
                y_offset = screen.get_height() # 文字在淡入階段保持在底部

            # 繪製開場畫面，傳入淡入透明度
            skip_rect = draw_intro_screen(screen, font, y_offset, current_fade_alpha)
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if skip_rect.collidepoint(pos):
                        game_state = "level_selection"
                        print("Skipped intro")
            
            # Intro animation total duration check
            if current_time - intro_start_time >= intro_duration:
                game_state = "level_selection"
                print("Intro animation completed")
        elif game_state == "level_selection":
            # --- START MODIFICATION ---
            # 1. 確保每一幀都清除螢幕，避免殘影
            screen.fill((0, 0, 0))

            # 2. 修改 draw_level_selection 的返回值，以接收 quit_rect
            cat_rects, reset_rect, quit_rect = draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels)
            # --- END MODIFICATION ---

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    # 處理關卡選擇
                    for i, level in enumerate(levels):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                print(f"Selected level: {selected_level} ({levels[selected_level].name if i < len(levels) else 'Invalid'})")
                    # 處理貓咪選擇
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            # 重新生成 cat_key_map 和 button_rects
                            cat_key_map = {}
                            for i, cat_type_selected in enumerate(selected_cats[:10]): # 使用 cat_type_selected 避免與外部 cat_type 混淆
                                cat_key_map[pygame.K_1 + i] = cat_type_selected
                            button_rects = {cat_type_selected: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type_selected in enumerate(selected_cats)}
                            print(f"Updated selected_cats: {selected_cats}, cat_key_map: {cat_key_map}")
                    # 處理重置進度按鈕
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        if os.path.exists(save_file):
                            os.remove(save_file)
                            print("Progress reset to initial state")
                        # Reinitialize save file with empty set
                        try:
                            with open(save_file, "w") as f:
                                json.dump(list(completed_levels), f)
                            print(f"Reinitialized {save_file} with empty completed levels")
                        except Exception as e:
                            print(f"Error reinitializing save file: {e}")
                    # --- START MODIFICATION ---
                    # 3. 新增處理 Quit 按鈕點擊的邏輯
                    if quit_rect.collidepoint(pos):
                        print("Quit button clicked. Exiting game.")
                        return # 點擊 Quit 按鈕時，直接從 main_game_loop 返回，結束遊戲
                    # --- END MODIFICATION ---

                elif event.type == pygame.KEYDOWN:
                    print(f"Key pressed in level_selection: {pygame.key.name(event.key)}, game_state: {game_state}")
                    if event.key == pygame.K_RETURN:
                        print(f"Enter pressed, selected_level: {selected_level}, playable: {selected_level == 0 or (selected_level - 1) in completed_levels}, selected_cats: {selected_cats}")
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:  # Ensure at least one cat is selected
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
                                shockwave_effects = []
                                current_budget = 1000
                                last_enemy_spawn_time = {(et["type"], et.get("variant", "default")): -et.get("initial_delay", 0) for et in current_level.enemy_types}
                                last_budget_increase_time = -333
                                last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                                status = 0
                                level_start_time = current_time
                                print(f"Starting level: {current_level.name}, game_state now: {game_state}")
                            else:
                                print("Cannot start: No cats selected!")
            pygame.display.flip()
        elif game_state == "playing":
            current_level = levels[selected_level]
            pause_rect = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pause_rect.collidepoint(pos):
                        game_state = "paused"
                elif event.type == pygame.KEYDOWN:
                    print(f"Playing state key: {pygame.key.name(event.key)}")
                    if event.key in cat_key_map:
                        cat_type = cat_key_map[event.key]
                        cost = cat_costs.get(cat_type, 0)
                        cooldown = cat_cooldowns.get(cat_type, 0)
                        print(f"Attempting to spawn {cat_type}, cost: {cost}, budget: {current_budget}, cooldown: {current_time - last_spawn_time.get(cat_type, 0)} vs {cooldown}")
                        if current_budget >= cost:
                            if current_time - last_spawn_time.get(cat_type, 0) >= cooldown:
                                current_budget -= cost
                                our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                                cat_y, cat_slot = cat_y_manager.get_available_y()
                                cat = cat_types[cat_type](our_tower_center, cat_y)
                                cat.slot_index = cat_slot  # 儲存它使用的 slot
                                start_x = our_tower_center - cat.width / 2 - 90
                                cat.x = start_x
                                cats.append(cat)
                                last_spawn_time[cat_type] = current_time
                                print(f"Spawned {cat_type} at {cat.x}, {cat_y}")
                            else:
                                print(f"Cooldown not elapsed for {cat_type}")
                        else:
                            print(f"Insufficient budget for {cat_type}")
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
                            cfg=config
                        )
                        enemy.slot_index = enemy_slot
                        start_x = enemy_tower_center - enemy.width / 2 + 50
                        enemy.x = start_x
                        enemies.append(enemy)
                        current_level.spawned_counts[key] += 1
                        current_level.last_spawn_times[key] = current_time
            current_level.all_limited_spawned = current_level.check_all_limited_spawned()
            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects)
            souls[:] = [soul for soul in souls if soul.update()]

            draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map)
            our_tower.draw(screen)
            if enemy_tower:
                enemy_tower.draw(screen)

            for soul in souls:
                soul.draw(screen)
            for shockwave in shockwave_effects:
                shockwave.draw(screen)
            for cat in cats:
                cat.draw(screen)
            for enemy in enemies:
                enemy.draw(screen)
            
            pygame.display.flip()

            if our_tower.hp <= 0:
                status = "lose"
                game_state = "end"
                print("Our tower destroyed, game over.")
            elif enemy_tower:
                if enemy_tower.hp <= 0:
                    status = "victory"
                    game_state = "end"
                    completed_levels.add(selected_level)
                    try:
                        with open(save_file, "w") as f:
                            json.dump(list(completed_levels), f)
                    except Exception as e:
                        print(f"Error saving completed levels: {e}")
                    print("Enemy tower destroyed, we win!")
                elif current_level.all_limited_spawned and not any(
                    et["is_limited"] is False for et in current_level.enemy_types
                ) and not enemies:
                    status = "victory"
                    game_state = "end"
                    completed_levels.add(selected_level)
                    try:
                        with open(save_file, "w") as f:
                            json.dump(list(completed_levels), f)
                    except Exception as e:
                        print(f"Error saving completed levels: {e}")
                    print("All enemies defeated, we win!")
        elif game_state == "paused":
            draw_pause_menu(screen, font)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    end_rect, continue_rect = draw_pause_menu(screen, font)
                    if end_rect.collidepoint(pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000
                        print("Battle ended, returning to level selection")
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        print("Resuming battle")
            pygame.display.flip()
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


        