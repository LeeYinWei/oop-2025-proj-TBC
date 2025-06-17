import json
import os
import asyncio
import pygame
from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager, CSmokeEffect
from .battle_logic import update_battle
from .ui import draw_level_selection, draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen, draw_ending_animation

# 初始化 Pygame 混音器
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5) # 設定預設音樂音量 (0.0 到 1.0)

# 載入貓咪生成音效 (請確認路徑正確且檔案存在)
cat_spawn_sfx = {}
try:
    if os.path.exists("audio/TBC/010.ogg"):
        cat_spawn_sfx['default'] = pygame.mixer.Sound("audio/TBC/010.ogg")
        cat_spawn_sfx['default'].set_volume(0.7)
    else:
        print("警告: 'audio/TBC/010.ogg' 未找到。貓咪生成音效將不會播放。")
except pygame.error as e:
    print(f"載入貓咪生成音效時發生錯誤: {e}")
    cat_spawn_sfx['default'] = None

# 載入勝利與失敗音效 (請確認路徑正確且檔案存在)
victory_sfx = None
defeat_sfx = None
try:
    if os.path.exists("audio/TBC/008.ogg"): # 請替換為你的勝利音效檔案路徑
        victory_sfx = pygame.mixer.Sound("audio/TBC/008.ogg")
        victory_sfx.set_volume(0.8)
    else:
        print("警告: 'audio/TBC/victory.ogg' 未找到。勝利音效將不會播放。")

    if os.path.exists("audio/TBC/009.ogg"): # 請替換為你的失敗音效檔案路徑
        defeat_sfx = pygame.mixer.Sound("audio/TBC/009.ogg")
        defeat_sfx.set_volume(0.8)
    else:
        print("警告: 'audio/TBC/defeat.ogg' 未找到。失敗音效將不會播放。")

except pygame.error as e:
    print(f"載入遊戲結束音效時發生錯誤: {e}")
    victory_sfx = None
    defeat_sfx = None

async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 24)
    end_font = pygame.font.SysFont(None, 96)
    game_state = "intro" # 遊戲初始狀態為 "intro"
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2] # 預設選取前兩個貓咪類型

    # 音訊變數
    current_bgm_path = None
    boss_music_active = False # 追蹤首領音樂是否正在播放的旗標

    # 從檔案載入已完成的關卡
    completed_levels = set()
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    completed_levels = set(loaded_data)
                else:
                    print(f"儲存檔案 '{save_file}' 格式無效，初始化為空集合。")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"載入已完成關卡時發生錯誤或檔案未找到: {e}，初始化為空集合。")

    # 遊戲實體與狀態變數初始化
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    last_budget_increase_time = -333 # 確保第一次金錢增益能立刻觸發
    total_budget_limitation = 16500
    current_budget = 1000 # 初始金錢，將被關卡配置覆寫
    budget_rate = 33
    status = None # 遊戲結束狀態 (勝利/失敗)
    level_start_time = 0 # 關卡開始時間

    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
    button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}

    # 開場動畫變數
    intro_start_time = pygame.time.get_ticks()
    intro_duration = 35000  # 總時長 35 秒
    fade_in_duration = 5000  # 淡入時長 5 秒
    y_offset = screen.get_height()
    current_fade_alpha = 0

    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((0, 0, 0)) # 清除螢幕每一幀

        # --- 音訊管理邏輯 ---
        if game_state == "intro":
            # 播放開場音樂 (只播放一次)
            intro_music_path = "audio/TBC/000.ogg" # 你的開場音樂路徑
            if current_bgm_path != intro_music_path:
                if os.path.exists(intro_music_path):
                    pygame.mixer.music.load(intro_music_path)
                    pygame.mixer.music.play(-1) # 無限循環播放
                    current_bgm_path = intro_music_path
                else:
                    print(f"警告: 開場音樂 '{intro_music_path}' 未找到。")

            # 計算淡入透明度
            if current_time - intro_start_time < fade_in_duration:
                fade_progress = (current_time - intro_start_time) / fade_in_duration
                current_fade_alpha = int(255 * fade_progress)
            else:
                current_fade_alpha = 255

            # 計算文字捲動進度
            text_scroll_start_time = intro_start_time + fade_in_duration
            if current_time >= text_scroll_start_time:
                text_progress_time = current_time - text_scroll_start_time
                text_scroll_duration = intro_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration) if text_scroll_duration > 0 else 1.0
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)
            else:
                y_offset = screen.get_height()

            # 繪製開場畫面 (淡入與捲動)
            skip_rect = draw_intro_screen(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if skip_rect.collidepoint(pos):
                        game_state = "level_selection"
                        pygame.mixer.music.stop() # 停止開場音樂
                        current_bgm_path = None # 重設 BGM 路徑
                        print("已跳過開場動畫。")

            if current_time - intro_start_time >= intro_duration:
                game_state = "level_selection"
                pygame.mixer.music.stop() # 停止開場音樂
                current_bgm_path = None # 重設 BGM 路徑
                print("開場動畫播放完畢。")

        elif game_state == "level_selection":
            # 確保在關卡選擇介面時音樂已停止
            if pygame.mixer.music.get_busy() and current_bgm_path is not None:
                pygame.mixer.music.stop()
                current_bgm_path = None
            boss_music_active = False # 重設首領音樂旗標

            cat_rects, reset_rect, quit_rect = draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            # 檢查是否為第一關或前一關已完成
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                print(f"已選取關卡: {selected_level} ({levels[selected_level].name if i < len(levels) else '無效'})")
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
                            button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                            print(f"已更新選取貓咪: {selected_cats}, 貓咪按鍵映射: {cat_key_map}")
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        if os.path.exists(save_file):
                            os.remove(save_file)
                            print("進度已重置為初始狀態。")
                        try:
                            with open(save_file, "w") as f:
                                json.dump(list(completed_levels), f)
                            print(f"已重新初始化 '{save_file}' 為空集合。")
                        except Exception as e:
                            print(f"重新初始化儲存檔案時發生錯誤: {e}")
                    if quit_rect.collidepoint(pos):
                        print("已點擊退出按鈕。遊戲即將退出。")
                        return
                elif event.type == pygame.KEYDOWN:
                    print(f"在關卡選擇介面按下按鍵: {pygame.key.name(event.key)}, 遊戲狀態: {game_state}")
                    if event.key == pygame.K_RETURN:
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                current_level.reset_towers() # 重設塔的狀態
                                our_tower = current_level.our_tower
                                # 塔生成煙霧效果
                                cs1 = CSmokeEffect(our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2-30, our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2+30, 1000)
                                cs2 = CSmokeEffect(our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2+10, our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2+20, 1000)
                                cs3 = CSmokeEffect(our_tower.x + our_tower.width // 4, our_tower.y + our_tower.height // 2+40, our_tower.x + our_tower.width // 5, our_tower.y + our_tower.height // 2, 1000)
                                our_tower.csmoke_effects.append(cs1)
                                our_tower.csmoke_effects.append(cs2)
                                our_tower.csmoke_effects.append(cs3)
                                enemy_tower = current_level.enemy_tower
                                cs1 = CSmokeEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2-20, enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 3+20, 1000)
                                cs2 = CSmokeEffect(enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2+30, enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2, 1000)
                                cs3 = CSmokeEffect(enemy_tower.x + enemy_tower.width // 4, enemy_tower.y + enemy_tower.height // 2+50, enemy_tower.x + enemy_tower.width // 5, enemy_tower.y + enemy_tower.height // 2+60, 1000)
                                enemy_tower.csmoke_effects.append(cs1)
                                enemy_tower.csmoke_effects.append(cs2)
                                enemy_tower.csmoke_effects.append(cs3)
                                # 重設敵人和金錢狀態
                                current_level.reset_spawn_counts() # 使用 Level 類別內建的方法重設生成計數和時間
                                cats.clear()
                                souls.clear()
                                enemies.clear()
                                shockwave_effects.clear()
                                current_budget = current_level.initial_budget # 使用關卡設定的初始金錢
                                last_budget_increase_time = current_time - 333 # 確保金錢增益能立刻觸發
                                last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                                status = None # 重設遊戲結束狀態
                                level_start_time = current_time

                                # --- 開始關卡音樂 ---
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    if current_bgm_path != current_level.music_path:
                                        pygame.mixer.music.load(current_level.music_path)
                                        pygame.mixer.music.play(-1) # 無限循環播放
                                        current_bgm_path = current_level.music_path
                                        boss_music_active = False # 重設首領音樂旗標
                                else:
                                    print(f"警告: 關卡音樂 '{current_level.music_path}' 未找到。")
                                    if pygame.mixer.music.get_busy():
                                        pygame.mixer.music.stop()
                                    current_bgm_path = None

                                print(f"開始關卡: {current_level.name}, 目前遊戲狀態: {game_state}")
                            else:
                                print("無法開始: 未選取任何貓咪！")

        elif game_state == "playing":
            current_level = levels[selected_level]
            pause_rect = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map)

            # --- 首領音樂邏輯 ---
            if current_level.switch_music_on_boss:
                any_boss_present = any(enemy.is_boss for enemy in enemies)
                if any_boss_present and not boss_music_active:
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        pygame.mixer.music.load(current_level.boss_music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.boss_music_path
                        boss_music_active = True
                    else:
                        print(f"警告: 首領音樂 '{current_level.boss_music_path}' 未找到。")
                elif not any_boss_present and boss_music_active:
                    # 如果首領消失/被擊敗，切換回普通關卡音樂
                    if current_level.music_path and os.path.exists(current_level.music_path):
                        pygame.mixer.music.load(current_level.music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.music_path
                        boss_music_active = False
                    else:
                        print(f"警告: 返回普通關卡音樂 '{current_level.music_path}' 時未找到。")
                        if pygame.mixer.music.get_busy():
                            pygame.mixer.music.stop()
                        current_bgm_path = None

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if pause_rect.collidepoint(pos):
                        game_state = "paused"
                        pygame.mixer.music.pause() # 暫停音樂
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map:
                        cat_type = cat_key_map[event.key]
                        cost = cat_costs.get(cat_type, 0)
                        cooldown = cat_cooldowns.get(cat_type, 0)
                        if current_budget >= cost:
                            if current_time - last_spawn_time.get(cat_type, 0) >= cooldown:
                                current_budget -= cost
                                our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                                cat_y, cat_slot = cat_y_manager.get_available_y()
                                cat = cat_types[cat_type](our_tower_center, cat_y)
                                cat.slot_index = cat_slot
                                start_x = our_tower_center - cat.width / 2 - 90
                                cat.x = start_x
                                cats.append(cat)
                                last_spawn_time[cat_type] = current_time

                                # --- 播放貓咪生成音效 ---
                                if cat_spawn_sfx.get('default'):
                                    cat_spawn_sfx['default'].play()

                                print(f"生成了 {cat_type} 在 {cat.x}, {cat.y}")
                            else:
                                print(f"'{cat_type}' 的冷卻時間未到。")
                        else:
                            print(f"金錢不足，無法生成 '{cat_type}'。")

            # 更新金錢
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time

            # 生成敵人
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", "default"))
                # 檢查是否為無限生成或未達到生成上限，以及是否符合塔血量百分比條件
                if (not et.get("is_limited", False) or current_level.spawned_counts.get(key, 0) < et.get("spawn_count", 0)) and tower_hp_percent <= et.get("tower_hp_percent", 100):
                    interval = et.get("spawn_interval_1", current_level.spawn_interval)
                    initial_delay = et.get("initial_delay", 0)
                    if current_time - current_level.last_spawn_times.get(key, 0) >= interval and current_time - level_start_time >= initial_delay:
                        enemy_tower_center = current_level.enemy_tower.x + current_level.enemy_tower.width / 2
                        # 敵人配置，從 config_loader 載入的屬性會覆寫預設值
                        config = {
                            "hp": 100, "speed": 1, "atk": 10, "attack_range": 50,
                            "width": 50, "height": 50, "hp_multiplier": et.get("hp_multiplier", 1.0),
                            "atk_multiplier": et.get("damage_multiplier", 1.0), "kb_limit": 1,
                            "attack_interval": 1000, "windup_duration": 200, "attack_duration": 100,
                            "recovery_duration": 50, "is_aoe": et.get("is_aoe", False),
                            "color": (255, 0, 0), "idle_frames": [], "move_frames": [],
                            "windup_frames": [], "attack_frames": [], "recovery_frames": [], "kb_frames": []
                        }
                        config.update(current_level.enemy_configs.get(et["type"], {}))
                        enemy_y, enemy_slot = enemy_y_manager.get_available_y()
                        enemy = enemy_types[et["type"]](
                            enemy_tower_center, enemy_y,
                            is_boss=et.get("is_boss", False),
                            cfg=config
                        )
                        enemy.slot_index = enemy_slot
                        start_x = enemy_tower_center - enemy.width / 2 + 50
                        enemy.x = start_x
                        enemies.append(enemy)
                        current_level.spawned_counts[key] += 1
                        current_level.last_spawn_times[key] = current_time

            current_level.all_limited_spawned = current_level.check_all_limited_spawned()

            # 更新實體
            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects, current_budget)
            souls[:] = [soul for soul in souls if soul.update()]

            # 繪製所有元素
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

            # 檢查勝利/失敗條件
            if our_tower.hp <= 0:
                if status != "lose": # 僅在狀態首次變為 "lose" 時播放音效
                    status = "lose"
                    game_state = "end"
                    pygame.mixer.music.stop() # 停止音樂
                    current_bgm_path = None
                    if defeat_sfx: # 播放失敗音效
                        defeat_sfx.play()
                    print("我方塔被摧毀，遊戲結束。")
            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory": # 僅在狀態首次變為 "victory" 時播放音效
                    status = "victory"
                    game_state = "end"
                    
                    pygame.mixer.music.stop() # 停止音樂
                    current_bgm_path = None
                    if victory_sfx: # 播放勝利音效
                        victory_sfx.play()
                    print("敵方塔被摧毀，我方獲勝！")

        elif game_state == "paused":
            end_rect, continue_rect = draw_pause_menu(screen, font, current_level)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if end_rect.collidepoint(pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000 # 回到選關介面時金錢重置
                        pygame.mixer.music.stop() # 停止音樂
                        current_bgm_path = None
                        print("戰鬥結束，返回關卡選擇介面。")
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        pygame.mixer.music.unpause() # 解除音樂暫停
                        print("恢復戰鬥。")

        elif game_state == "end":
            current_level = levels[selected_level]
            is_last_level = selected_level == len(levels) - 1
            is_first_completion = selected_level not in completed_levels and is_last_level
            # print(is_first_completion, selected_level, completed_levels, is_last_level)
            # completed_levels.add(selected_level)
            # try:
            #     with open(save_file, "w") as f:
            #         json.dump(list(completed_levels), f)
            # except Exception as e:
            #     print(f"儲存已完成關卡時發生錯誤: {e}")
            # 獲取或設定勝利畫面顯示時間
            victory_display_time = getattr(pygame.time, "victory_display_time", 0)
            if victory_display_time == 0 and status == "victory":
                pygame.time.victory_display_time = pygame.time.get_ticks()
                victory_duration = 3000  # 3 秒顯示勝利畫面

            if status == "victory" and pygame.time.get_ticks() - victory_display_time < victory_duration:
                # 顯示勝利畫面
                draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
            else:
                # 顯示最終結束畫面 (包括失敗或勝利畫面結束後的下一步提示)
                draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time)
                pygame.display.flip()
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                    elif event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_RETURN:
                            # 只有在勝利且是最後一關且是第一次完成時進入結局動畫
                            if status == "victory" and is_first_completion:
                                game_state = "ending"
                                pygame.time.ending_start_time = pygame.time.get_ticks()
                                # 播放結局音樂
                                ending_music_path = "audio/TBC/005.ogg" # 你的結局音樂路徑
                                if os.path.exists(ending_music_path):
                                    pygame.mixer.music.load(ending_music_path)
                                    pygame.mixer.music.play(-1) # 無限循環播放
                                    current_bgm_path = ending_music_path
                                else:
                                    print(f"警告: 結局音樂 '{ending_music_path}' 未找到。")
                            else:
                                game_state = "level_selection"
                                our_tower = None
                                enemy_tower = None
                                cats.clear()
                                enemies.clear()
                                souls.clear()
                                shockwave_effects.clear()
                                current_budget = 1000 # 回到選關介面時金錢重置

                                # 如果勝利且是第一次完成該關卡，則儲存進度
                                if status == "victory" and selected_level not in completed_levels:
                                    completed_levels.add(selected_level)
                                    try:
                                        with open(save_file, "w") as f:
                                            json.dump(list(completed_levels), f)
                                    except Exception as e:
                                        print(f"儲存已完成關卡時發生錯誤: {e}")
                                
                                pygame.mixer.music.stop() # 停止音樂
                                current_bgm_path = None

        elif game_state == "ending":
            ending_start_time = getattr(pygame.time, "ending_start_time", 0)
            if ending_start_time == 0:
                pygame.time.ending_start_time = pygame.time.get_ticks()
            ending_duration = 35000  # 總時長 35 秒
            fade_in_duration = 5000  # 淡入時長 5 秒
            y_offset = screen.get_height()
            current_fade_alpha = 0

            current_time = pygame.time.get_ticks()
            elapsed_time = current_time - ending_start_time

            if elapsed_time < fade_in_duration:
                fade_progress = elapsed_time / fade_in_duration
                current_fade_alpha = int(255 * fade_progress)
            else:
                current_fade_alpha = 255

            text_scroll_start_time = ending_start_time + fade_in_duration
            if elapsed_time >= fade_in_duration:
                text_progress_time = elapsed_time - fade_in_duration
                text_scroll_duration = ending_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration) if text_scroll_duration > 0 else 1.0
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)

            skip_rect = draw_ending_animation(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if skip_rect and skip_rect.collidepoint(pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000
                        # 確保最後一關在勝利時被標記為完成
                        if selected_level not in completed_levels and status == "victory":
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                            except Exception as e:
                                print(f"儲存已完成關卡時發生錯誤: {e}")
                        pygame.time.ending_start_time = 0
                        pygame.mixer.music.stop() # 停止結局音樂
                        current_bgm_path = None

            if elapsed_time >= ending_duration:
                game_state = "level_selection"
                our_tower = None
                enemy_tower = None
                cats.clear()
                enemies.clear()
                souls.clear()
                shockwave_effects.clear()
                current_budget = 1000
                # 確保最後一關在勝利時被標記為完成
                if selected_level not in completed_levels and status == "victory":
                    completed_levels.add(selected_level)
                    try:
                        with open(save_file, "w") as f:
                            json.dump(list(completed_levels), f)
                    except Exception as e:
                        print(f"儲存已完成關卡時發生錯誤: {e}")
                pygame.time.ending_start_time = 0
                pygame.mixer.music.stop() # 停止結局音樂
                current_bgm_path = None

        await asyncio.sleep(1 / FPS)