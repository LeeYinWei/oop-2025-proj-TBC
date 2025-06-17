import json
import os
import asyncio
import pygame

delayTime = 2000


# --- Pygame 混音器初始化 ---
pygame.mixer.init()
pygame.mixer.music.set_volume(0.5) # 設定預設背景音樂音量 (0.0 到 1.0)

# --- 載入遊戲音效 ---
# 載入貓咪生成音效
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

# 載入遊戲結束音效 (勝利/失敗)
victory_sfx = None
defeat_sfx = None
try:
    if os.path.exists("audio/TBC/008.ogg"):
        victory_sfx = pygame.mixer.Sound("audio/TBC/008.ogg")
        victory_sfx.set_volume(0.8)
    else:
        print("警告: 'audio/TBC/008.ogg' 未找到。勝利音效將不會播放。")

    if os.path.exists("audio/TBC/009.ogg"):
        defeat_sfx = pygame.mixer.Sound("audio/TBC/009.ogg")
        defeat_sfx.set_volume(0.8)
    else:
        print("警告: 'audio/TBC/009.ogg' 未找到。失敗音效將不會播放。")
except pygame.error as e:
    print(f"載入遊戲結束音效時發生錯誤: {e}")
    victory_sfx = None
    defeat_sfx = None

# 載入按鍵操作相關音效
key_action_sfx = {}
try:
    if os.path.exists("audio/TBC/015.ogg"): # 無法出擊音效 (金錢不足/冷卻中)
        key_action_sfx['cannot_deploy'] = pygame.mixer.Sound("audio/TBC/015.ogg")
        key_action_sfx['cannot_deploy'].set_volume(0.6)
    else:
        print("警告: 'audio/TBC/015.ogg' 未找到。無法出擊音效將不會播放。")
    
    if os.path.exists("audio/TBC/014.ogg"): # 可以出擊音效 (成功部署)
        key_action_sfx['can_deploy'] = pygame.mixer.Sound("audio/TBC/014.ogg")
        key_action_sfx['can_deploy'].set_volume(0.6)
    else:
        print("警告: 'audio/TBC/014.ogg' 未找到。可以出擊音效將不會播放。")

    if os.path.exists("audio/TBC/011.ogg"): # 其他按鈕音效 (選單點擊/確認)
        key_action_sfx['other_button'] = pygame.mixer.Sound("audio/TBC/011.ogg")
        key_action_sfx['other_button'].set_volume(0.5)
    else:
        print("警告: 'audio/TBC/011.ogg' 未找到。其他按鈕音效將不會播放。")
except pygame.error as e:
    print(f"載入按鍵音效時發生錯誤: {e}")
    key_action_sfx = {}

# 載入戰鬥相關音效 (傳遞給 battle_logic.py 使用)
battle_sfx = {}
try:
    if os.path.exists("audio/TBC/021.ogg"): # 攻擊到角色音效
        battle_sfx['hit_unit'] = pygame.mixer.Sound("audio/TBC/021.ogg")
        battle_sfx['hit_unit'].set_volume(0.6)
    else:
        print("警告: 'audio/TBC/021.ogg' 未找到。攻擊角色音效將不會播放。")
    
    if os.path.exists("audio/TBC/022.ogg"): # 攻擊到塔音效
        battle_sfx['hit_tower'] = pygame.mixer.Sound("audio/TBC/022.ogg")
        battle_sfx['hit_tower'].set_volume(0.6)
    else:
        print("警告: 'audio/TBC/022.ogg' 未找到。攻擊塔音效將不會播放。")

    if os.path.exists("audio/TBC/023.ogg"): # 角色死亡音效
        battle_sfx['unit_die'] = pygame.mixer.Sound("audio/TBC/023.ogg")
        battle_sfx['unit_die'].set_volume(0.7)
    else:
        print("警告: 'audio/TBC/023.ogg' 未找到。角色死亡音效將不會播放。")
except pygame.error as e:
    print(f"載入戰鬥音效時發生錯誤: {e}")
    battle_sfx = {}

# 載入 Boss 震波音效 (獨立音效，不屬於 battle_sfx)
boss_intro_sfx = None
try:
    if os.path.exists("audio/TBC/036.ogg"):
        boss_intro_sfx = pygame.mixer.Sound("audio/TBC/036.ogg")
        boss_intro_sfx.set_volume(0.9)
    else:
        print("警告: 'audio/TBC/036.ogg' 未找到。Boss 震波音效將不會播放。")
except pygame.error as e:
    print(f"載入 Boss 震波音效時發生錯誤: {e}")
    boss_intro_sfx = None

# --- 主遊戲迴圈 ---
async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 25)
    end_font = pygame.font.SysFont(None, 96)
    select_font = pygame.font.SysFont(None, 60)
    square_surface = pygame.Surface((1220, 480), pygame.SRCALPHA)
    square_surface.fill((150, 150, 150, 100))  # 50% 透明
    game_state = "intro" # 遊戲初始狀態
    from .battle_logic import update_battle
    from .ui import draw_level_selection, draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen, draw_ending_animation

    #from .load_images import *
    from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager,CSmokeEffect, load_cat_images

    # 遊戲狀態變數初始化
    selected_level = 0
    selected_cats = list(cat_types.keys())[:2] # 預設選取前兩個貓咪類型
    current_bgm_path = None # 追蹤當前播放的背景音樂路徑
    boss_music_active = False # 追蹤首領特定背景音樂是否正在播放的旗標
    boss_shockwave_played_for_this_boss = False # 追蹤 Boss 震波音效是否已播放

    # 載入已完成的關卡進度
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

    # 遊戲實體與數值變數 (會在開始新關卡時重設)
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    current_budget = 1000 # 初始金錢，將被關卡配置覆寫
    last_budget_increase_time = -333 # 確保第一次金錢增益能立刻觸發
    total_budget_limitation = 16500
    budget_rate = 33
    status = None # 遊戲結束狀態 (勝利/失敗)
    level_start_time = 0 # 關卡開始時間

    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
    button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}

    #load all images
    cat_images = load_cat_images()  # 載入貓咪圖片
    from game.constants import csmoke_images1, csmoke_images2

    # Intro animation variables

    intro_start_time = pygame.time.get_ticks()
    intro_duration = 35000  # 總時長
    fade_in_duration = 5000  # 淡入時長
    
    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((0, 0, 0)) # 清除螢幕每一幀

        # --- 遊戲狀態邏輯 ---
        if game_state == "intro":
            # 播放開場音樂
            intro_music_path = "audio/TBC/000.ogg"
            if current_bgm_path != intro_music_path:
                if os.path.exists(intro_music_path):
                    pygame.mixer.music.load(intro_music_path)
                    pygame.mixer.music.play(-1)
                    current_bgm_path = intro_music_path
                else:
                    print(f"警告: 開場音樂 '{intro_music_path}' 未找到。")

            # 處理開場動畫淡入及文字捲動
            elapsed_intro_time = current_time - intro_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_intro_time / fade_in_duration))
            
            y_offset = screen.get_height()
            if elapsed_intro_time >= fade_in_duration:
                text_progress_time = elapsed_intro_time - fade_in_duration
                text_scroll_duration = intro_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration) if text_scroll_duration > 0 else 1.0
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)

            skip_rect = draw_intro_screen(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect.collidepoint(event.pos):
                        game_state = "level_selection"
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                        print("已跳過開場動畫。")

            if elapsed_intro_time >= intro_duration + delayTime:
                game_state = "level_selection"
                pygame.mixer.music.stop()
                current_bgm_path = None
                print("開場動畫播放完畢。")

        elif game_state == "level_selection":

            # 確保在關卡選擇介面時音樂已停止

            # 確保在關卡選擇介面時沒有背景音樂

            if pygame.mixer.music.get_busy() and current_bgm_path is not None:
                pygame.mixer.music.stop()
                current_bgm_path = None
            boss_music_active = False # 重設首領音樂旗標

            boss_shockwave_played_for_this_boss = False # 重設震波音效旗標



            cat_rects, reset_rect, quit_rect = draw_level_selection(screen, levels, selected_level, selected_cats, font, select_font, completed_levels, cat_images, square_surface)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            # 檢查是否為第一關或前一關已完成，才能選擇該關卡
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                print(f"已選取關卡: {selected_level} ({levels[selected_level].name if i < len(levels) else '無效'})")
                                if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                            else:
                                if key_action_sfx.get('cannot_deploy'): key_action_sfx['cannot_deploy'].play()
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
                            button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                            print(f"已更新選取貓咪: {selected_cats}, 貓咪按鍵映射: {cat_key_map}")
                            if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        if os.path.exists(save_file): os.remove(save_file)
                        try:
                            with open(save_file, "w") as f: json.dump(list(completed_levels), f)
                            print(f"已重新初始化 '{save_file}' 為空集合。")
                        except Exception as e:
                            print(f"重新初始化儲存檔案時發生錯誤: {e}")
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                    if quit_rect.collidepoint(pos):
                        print("已點擊退出按鈕。遊戲即將退出。")
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                        return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                current_level.reset_towers()
                                our_tower = current_level.our_tower
                                enemy_tower = current_level.enemy_tower
                                
                                # 塔生成煙霧效果 (我方塔)
                                our_tower.csmoke_effects.append(CSmokeEffect(our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 - 30, our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 + 30,csmoke_images1, csmoke_images2, 1000))
                                our_tower.csmoke_effects.append(CSmokeEffect(our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 10, our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 20,csmoke_images1, csmoke_images2, 1000))
                                our_tower.csmoke_effects.append(CSmokeEffect(our_tower.x + our_tower.width // 4, our_tower.y + our_tower.height // 2 + 40, our_tower.x + our_tower.width // 5, our_tower.y + our_tower.height // 2,csmoke_images1, csmoke_images2, 1000))
                                # 塔生成煙霧效果 (敵方塔)
                                enemy_tower.csmoke_effects.append(CSmokeEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2 - 20, enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 3 + 20,csmoke_images1, csmoke_images2, 1000))
                                enemy_tower.csmoke_effects.append(CSmokeEffect(enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2 + 30, enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2,csmoke_images1, csmoke_images2, 1000))
                                enemy_tower.csmoke_effects.append(CSmokeEffect(enemy_tower.x + enemy_tower.width // 4, enemy_tower.y + enemy_tower.height // 2 + 50, enemy_tower.x + enemy_tower.width // 5, enemy_tower.y + enemy_tower.height // 2 + 60,csmoke_images1, csmoke_images2, 1000))

                                # 重設遊戲狀態變數
                                current_level.reset_spawn_counts()
                                cats.clear()
                                souls.clear()
                                enemies.clear()
                                shockwave_effects.clear()
                                current_budget = current_level.initial_budget
                                last_budget_increase_time = current_time - 333
                                last_spawn_time = {cat_type: 0 for cat_type in cat_types}
                                status = None
                                level_start_time = current_time

                                # 開始關卡背景音樂
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    if current_bgm_path != current_level.music_path:
                                        pygame.mixer.music.load(current_level.music_path)
                                        pygame.mixer.music.play(-1)
                                        current_bgm_path = current_level.music_path
                                        boss_music_active = False # 重設首領音樂旗標
                                else:
                                    print(f"警告: 關卡音樂 '{current_level.music_path}' 未找到。")
                                    if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
                                    current_bgm_path = None
                                
                                boss_shockwave_played_for_this_boss = False # 確保新關卡 Boss 音效能再次播放
                                if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                                print(f"開始關卡: {current_level.name}")
                            else:
                                print("無法開始: 未選取任何貓咪！")
                                if key_action_sfx.get('cannot_deploy'): key_action_sfx['cannot_deploy'].play()
                        else:
                            if key_action_sfx.get('cannot_deploy'): key_action_sfx['cannot_deploy'].play()

        elif game_state == "playing":
            current_level = levels[selected_level]
            pause_rect = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map)

            # --- 首領音效與音樂邏輯 ---
            any_boss_present = any(enemy.is_boss for enemy in enemies)

            # 階段 1: Boss 出場，播放震波音效 (只播放一次)
            if any_boss_present and not boss_shockwave_played_for_this_boss:
                if boss_intro_sfx:
                    boss_intro_sfx.play()
                    boss_shockwave_played_for_this_boss = True # 標記為已播放，確保只播放一次
                    print("Boss 出場，播放震波音效。")

                # 階段 2: 根據關卡設定，決定是否切換 Boss 背景音樂 (僅在震波音效首次觸發時檢查)
                if current_level.switch_music_on_boss and not boss_music_active:
                    pygame.mixer.music.pause() # 暫停當前背景音樂
                    
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        pygame.mixer.music.load(current_level.boss_music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.boss_music_path
                        boss_music_active = True # 標記 Boss 背景音樂已啟動
                        print("切換到 Boss 音樂。")
                    else:
                        print(f"警告: 首領音樂 '{current_level.boss_music_path}' 未找到，無法播放。")
                        pygame.mixer.music.unpause() # 如果 Boss 音樂缺失，解除背景音樂暫停

            # 階段 3: Boss 消失/被擊敗後音樂處理 (根據需求，這裡不需額外邏輯切換回普通音樂)

            # --- 事件處理 ---
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_rect.collidepoint(event.pos):
                        game_state = "paused"
                        pygame.mixer.music.pause() # 暫停音樂
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map: # 貓咪出擊按鍵
                        cat_type = cat_key_map[event.key]
                        cost = cat_costs.get(cat_type, 0)
                        cooldown = cat_cooldowns.get(cat_type, 0)
                        
                        can_deploy = False
                        if current_budget >= cost and (current_time - last_spawn_time.get(cat_type, 0) >= cooldown):
                            can_deploy = True

                        if can_deploy:
                            current_budget -= cost
                            our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                            cat_y, cat_slot = cat_y_manager.get_available_y()
                            cat = cat_types[cat_type](our_tower_center, cat_y)
                            cat.slot_index = cat_slot
                            start_x = our_tower_center - cat.width / 2 - 90
                            cat.x = start_x
                            cats.append(cat)
                            last_spawn_time[cat_type] = current_time

                            if cat_spawn_sfx.get('default'): cat_spawn_sfx['default'].play()
                            if key_action_sfx.get('can_deploy'): key_action_sfx['can_deploy'].play()
                            print(f"生成了 {cat_type} 在 {cat.x}, {cat.y}")
                        else:
                            if key_action_sfx.get('cannot_deploy'): key_action_sfx['cannot_deploy'].play()
                            if current_budget < cost:
                                print(f"金錢不足，無法生成 '{cat_type}'。")
                            else:
                                print(f"'{cat_type}' 的冷卻時間未到。")
                    else: # 其他按鈕被按下
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()

            # --- 遊戲邏輯更新 ---
            # 更新金錢
            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time

            # 生成敵人
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", "default"))
                if (not et.get("is_limited", False) or current_level.spawned_counts.get(key, 0) < et.get("spawn_count", 0)) \
                   and tower_hp_percent <= et.get("tower_hp_percent", 100):
                    interval = et.get("spawn_interval_1", current_level.spawn_interval)
                    initial_delay = et.get("initial_delay", 0)
                    if current_time - current_level.last_spawn_times.get(key, 0) >= interval and current_time - level_start_time >= initial_delay:
                        enemy_tower_center = current_level.enemy_tower.x + current_level.enemy_tower.width / 2
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

            # 更新所有遊戲實體並處理戰鬥邏輯
            for cat in cats:
                cat.update_status_effects(current_time)
            for enemy in enemies:
                enemy.update_status_effects(current_time)
            # 將 battle_sfx 字典傳遞給 update_battle
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects, current_budget, battle_sfx)
            souls[:] = [soul for soul in souls if soul.update()]

            # --- 繪製所有元素 ---
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

            # --- 檢查勝利/失敗條件 ---
            if our_tower.hp <= 0:
                if status != "lose":
                    status = "lose"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played_for_this_boss = False
                    if defeat_sfx: defeat_sfx.play()
                    print("我方塔被摧毀，遊戲結束。")
            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory":
                    status = "victory"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played_for_this_boss = False
                    # 勝利音效將在 "end" 狀態的開始處播放，確保其能完整播放
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
                        # 重設所有遊戲狀態到預設值
                        our_tower = None; enemy_tower = None
                        cats.clear(); enemies.clear(); souls.clear(); shockwave_effects.clear()
                        current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played_for_this_boss = False
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                        print("戰鬥結束，返回關卡選擇介面。")
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        pygame.mixer.music.unpause() # 解除音樂暫停
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                        print("恢復戰鬥。")

        elif game_state == "end":
            current_level = levels[selected_level]
            is_last_level = selected_level == len(levels) - 1
            # 判斷是否為首次完成當前關卡（僅用於儲存進度）
            is_first_completion_of_current_level = (selected_level not in completed_levels)

            # 處理勝利音效播放和勝利畫面持續時間
            victory_display_time = getattr(pygame.time, "victory_display_time", 0)
            if status == "victory" and victory_display_time == 0: # 勝利畫面首次進入時
                pygame.time.victory_display_time = pygame.time.get_ticks()
                if victory_sfx:
                    victory_sfx.play() # 確保勝利音效只播放一次
                print("勝利音效已播放。") # 確認日誌
            
            victory_duration = 3000 # 勝利畫面顯示 3 秒
            
            # 繪製結局畫面
            draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        # 處理勝利後儲存進度
                        if status == "victory" and is_first_completion_of_current_level:
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"已儲存關卡 {selected_level} 的完成進度。")
                            except Exception as e:
                                print(f"儲存已完成關卡時發生錯誤: {e}")
                        
                        # 只有在勝利且是最後一關且是首次完成時進入結局動畫
                        if status == "victory" and is_last_level and is_first_completion_of_current_level:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            # 播放結局音樂
                            ending_music_path = "audio/TBC/005.ogg"
                            if os.path.exists(ending_music_path):
                                pygame.mixer.music.load(ending_music_path)
                                pygame.mixer.music.play(-1)
                                current_bgm_path = ending_music_path
                            else:
                                print(f"警告: 結局音樂 '{ending_music_path}' 未找到。")
                        else: # 其他情況返回關卡選擇
                            game_state = "level_selection"
                            # 重設所有遊戲狀態到預設值
                            our_tower = None; enemy_tower = None
                            cats.clear(); enemies.clear(); souls.clear(); shockwave_effects.clear()
                            current_budget = 1000
                        
                        # 清理音頻狀態
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played_for_this_boss = False
                        # 重設 victory_display_time，以便下次勝利時能正確觸發
                        setattr(pygame.time, "victory_display_time", 0) 
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
        
        elif game_state == "ending":
            ending_start_time = getattr(pygame.time, "ending_start_time", pygame.time.get_ticks())
            setattr(pygame.time, "ending_start_time", ending_start_time) # 確保結束動畫開始時間被設定
            ending_duration = 35000  # 總時長
            fade_in_duration = 5000  # 淡入時長

            elapsed_time = current_time - ending_start_time

            # 計算淡入透明度
            current_fade_alpha = int(255 * min(1.0, elapsed_time / fade_in_duration))

            # 計算文字捲動進度
            y_offset = screen.get_height()
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
                    if skip_rect and skip_rect.collidepoint(event.pos):
                        game_state = "level_selection"
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        if key_action_sfx.get('other_button'): key_action_sfx['other_button'].play()
                        setattr(pygame.time, "ending_start_time", 0) # 重設結束動畫開始時間
                        print("已跳過結局動畫。")
            
            if elapsed_time >= ending_duration + delayTime:
                game_state = "level_selection"
                pygame.mixer.music.stop()
                current_bgm_path = None
                print("結局動畫播放完畢。")
                setattr(pygame.time, "ending_start_time", 0) # 重設結束動畫開始時間
        
        await asyncio.sleep(0) # 允許其他 asyncio 任務執行 (例如 Pygame 事件處理)
        clock.tick(FPS)