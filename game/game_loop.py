import json
import os
import asyncio
import pygame

# 延遲時間（單位：毫秒）
DELAY_TIME = 2000

# --- Pygame 混音器初始化 ---
pygame.mixer.init()
print(f"混音器初始化，通道數: {pygame.mixer.get_num_channels()}")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.set_num_channels(16)  # 增加到 16 個頻道
print(f"設置頻道數: {pygame.mixer.get_num_channels()}")

# --- 音效載入 ---
# 貓咪生成音效
cat_spawn_sfx = {}
if os.path.exists("audio/TBC/010.ogg"):
    cat_spawn_sfx['default'] = pygame.mixer.Sound("audio/TBC/010.ogg")
    cat_spawn_sfx['default'].set_volume(0.7)
else:
    print("警告: 'audio/TBC/010.ogg' 未找到，貓咪生成音效將不會播放。")

# 遊戲結束音效 (勝利/失敗)
victory_sfx = pygame.mixer.Sound("audio/TBC/008.ogg") if os.path.exists("audio/TBC/008.ogg") else None
defeat_sfx = pygame.mixer.Sound("audio/TBC/009.ogg") if os.path.exists("audio/TBC/009.ogg") else None
if not victory_sfx:
    print("警告: 'audio/TBC/008.ogg' 未找到，勝利音效將不會播放。")
if not defeat_sfx:
    print("警告: 'audio/TBC/009.ogg' 未找到，失敗音效將不會播放。")

# 按鍵操作音效
key_action_sfx = {
    'cannot_deploy': pygame.mixer.Sound("audio/TBC/015.ogg") if os.path.exists("audio/TBC/015.ogg") else None,
    'can_deploy': pygame.mixer.Sound("audio/TBC/014.ogg") if os.path.exists("audio/TBC/014.ogg") else None,
    'other_button': pygame.mixer.Sound("audio/TBC/011.ogg") if os.path.exists("audio/TBC/011.ogg") else None
}
for key, sfx in key_action_sfx.items():
    if sfx:
        sfx.set_volume(0.6 if key in ['cannot_deploy', 'can_deploy'] else 0.5)
    else:
        print(f"警告: 'audio/TBC/{'015' if key == 'cannot_deploy' else '014' if key == 'can_deploy' else '011'}.ogg' 未找到，{key} 音效將不會播放。")

# 戰鬥音效
battle_sfx = {
    'hit_unit': pygame.mixer.Sound("audio/TBC/021.ogg") if os.path.exists("audio/TBC/021.ogg") else None,
    'hit_tower': pygame.mixer.Sound("audio/TBC/022.ogg") if os.path.exists("audio/TBC/022.ogg") else None,
    'unit_die': pygame.mixer.Sound("audio/TBC/023.ogg") if os.path.exists("audio/TBC/023.ogg") else None
}
for key, sfx in battle_sfx.items():
    if sfx:
        sfx.set_volume(0.6 if key in ['hit_unit', 'hit_tower'] else 0.7)
    else:
        print(f"警告: 'audio/TBC/{'021' if key == 'hit_unit' else '022' if key == 'hit_tower' else '023'}.ogg' 未找到，{key} 音效將不會播放。")

# Boss 震波音效
boss_intro_sfx = pygame.mixer.Sound("audio/TBC/036.ogg") if os.path.exists("audio/TBC/036.ogg") else None
if not boss_intro_sfx:
    print("警告: 'audio/TBC/036.ogg' 未找到，Boss 震波音效將不會播放。")

# --- 主遊戲迴圈 ---
async def main_game_loop(screen, clock):
    FPS = 60
    font = pygame.font.SysFont(None, 25)
    end_font = pygame.font.SysFont(None, 96)
    select_font = pygame.font.SysFont(None, 60)
    budget_font = pygame.font.SysFont(None, 40)
    square_surface = pygame.Surface((1220, 480), pygame.SRCALPHA)
    square_surface.fill((150, 150, 150, 100))  # 50% 透明

    game_state = "intro"
    from .battle_logic import update_battle
    from .ui import draw_level_selection, draw_game_ui, draw_pause_menu, draw_end_screen, draw_intro_screen, draw_ending_animation
    from .entities import cat_types, cat_costs, cat_cooldowns, levels, enemy_types, YManager, CSmokeEffect, load_cat_images
    from game.constants import csmoke_images1, csmoke_images2

    selected_level = 0
    selected_cats = list(cat_types.keys())[:2]
    current_bgm_path = None
    boss_music_active = False
    boss_shockwave_played = False

    # 臨時禁用本地進度保存（瀏覽器不支援文件 I/O）
    completed_levels = set()
    save_file = "completed_levels.json"
    try:
        if os.path.exists(save_file):
            with open(save_file, "r") as f:
                loaded_data = json.load(f)
                if isinstance(loaded_data, list):
                    completed_levels = set(loaded_data)
                else:
                    print(f"警告: 儲存檔案 '{save_file}' 格式無效，初始化為空集合。")
    except (json.JSONDecodeError, FileNotFoundError) as e:
        print(f"警告: 載入已完成關卡時發生錯誤或檔案未找到: {e}，初始化為空集合。")

    # 遊戲實體與狀態
    cats = []
    enemies = []
    souls = []
    shockwave_effects = []
    our_tower = None
    enemy_tower = None
    last_spawn_time = {cat_type: 0 for cat_type in cat_types}
    current_budget = 1000
    last_budget_increase_time = -333
    total_budget_limitation = 16500
    budget_rate = 33
    status = None
    level_start_time = 0

    cat_y_manager = YManager(base_y=532, min_y=300, max_slots=15)
    enemy_y_manager = YManager(base_y=500, min_y=300, max_slots=15)
    cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
    button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}

    cat_images = load_cat_images()

    intro_start_time = pygame.time.get_ticks()
    intro_duration = 35000
    fade_in_duration = 5000

    while True:
        current_time = pygame.time.get_ticks()
        screen.fill((0, 0, 0))

        if game_state == "intro":
            intro_music_path = "audio/TBC/000.ogg"
            if current_bgm_path != intro_music_path and os.path.exists(intro_music_path):
                pygame.mixer.music.load(intro_music_path)
                pygame.mixer.music.play(-1)
                current_bgm_path = intro_music_path
            elif not os.path.exists(intro_music_path):
                print(f"警告: 開場音樂 '{intro_music_path}' 未找到。")

            elapsed_intro_time = current_time - intro_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_intro_time / fade_in_duration))
            y_offset = screen.get_height()
            if elapsed_intro_time >= fade_in_duration:
                text_progress_time = elapsed_intro_time - fade_in_duration
                text_scroll_duration = intro_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
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
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("已跳過開場動畫。")

            if elapsed_intro_time >= intro_duration + DELAY_TIME:
                game_state = "level_selection"
                pygame.mixer.music.stop()
                current_bgm_path = None
                print("開場動畫播放完畢。")

        elif game_state == "level_selection":
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.stop()
                current_bgm_path = None
            boss_music_active = False
            boss_shockwave_played = False

            cat_rects, reset_rect, quit_rect, start_rect = draw_level_selection(screen, levels, selected_level, selected_cats, font, select_font, completed_levels, cat_images, square_surface)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    for i, level in enumerate(levels):
                        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
                        if rect.collidepoint(pos):
                            if i == 0 or (i - 1) in completed_levels:
                                selected_level = i
                                print(f"已選取關卡: {selected_level} ({levels[selected_level].name})")
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                            else:
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                    for cat_type, rect in cat_rects.items():
                        if rect.collidepoint(pos):
                            if cat_type in selected_cats and len(selected_cats) > 1:
                                selected_cats.remove(cat_type)
                            elif cat_type not in selected_cats and len(selected_cats) < 10:
                                selected_cats.append(cat_type)
                            cat_key_map = {pygame.K_1 + i: cat_type for i, cat_type in enumerate(selected_cats[:10])}
                            button_rects = {cat_type: pygame.Rect(1100 + idx * 120, 50, 100, 50) for idx, cat_type in enumerate(selected_cats)}
                            print(f"已更新選取貓咪: {selected_cats}")
                            if key_action_sfx.get('other_button'):
                                key_action_sfx['other_button'].play()
                    if reset_rect.collidepoint(pos):
                        completed_levels.clear()
                        # 臨時禁用儲存
                        if os.path.exists(save_file):
                            os.remove(save_file)
                        try:
                            with open(save_file, "w") as f:
                                json.dump(list(completed_levels), f)
                            print(f"已重新初始化 '{save_file}'。")
                        except Exception as e:
                            print(f"重新初始化儲存檔案時發生錯誤: {e}")
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                    if quit_rect.collidepoint(pos):
                        print("已點擊退出按鈕，遊戲退出。")
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        return
                    if start_rect.collidepoint(pos):
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                current_level.reset_towers()
                                our_tower = current_level.our_tower
                                enemy_tower = current_level.enemy_tower
                                our_tower.csmoke_effects.extend([
                                    CSmokeEffect(our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 - 30,
                                            our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 + 30,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 10,
                                            our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 20,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(our_tower.x + our_tower.width // 4, our_tower.y + our_tower.height // 2 + 40,
                                            our_tower.x + our_tower.width // 5, our_tower.y + our_tower.height // 2,
                                            csmoke_images1, csmoke_images2, 1000)
                                ])
                                enemy_tower.csmoke_effects.extend([
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2 - 20,
                                            enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 3 + 20,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2 + 30,
                                            enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 4, enemy_tower.y + enemy_tower.height // 2 + 50,
                                            enemy_tower.x + enemy_tower.width // 5, enemy_tower.y + enemy_tower.height // 2 + 60,
                                            csmoke_images1, csmoke_images2, 1000)
                                ])
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
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    pygame.mixer.music.load(current_level.music_path)
                                    pygame.mixer.music.play(-1)
                                    current_bgm_path = current_level.music_path
                                    boss_music_active = False
                                else:
                                    print(f"警告: 關卡音樂 '{current_level.music_path}' 未找到。")
                                    pygame.mixer.music.stop()
                                    current_bgm_path = None
                                boss_shockwave_played = False
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                                print(f"開始關卡: {current_level.name}")
                            else:
                                print("無法開始: 未選取任何貓咪！")
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if selected_level == 0 or (selected_level - 1) in completed_levels:
                            if selected_cats:
                                game_state = "playing"
                                current_level = levels[selected_level]
                                current_level.reset_towers()
                                our_tower = current_level.our_tower
                                enemy_tower = current_level.enemy_tower
                                our_tower.csmoke_effects.extend([
                                    CSmokeEffect(our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 - 30,
                                            our_tower.x + our_tower.width // 2, our_tower.y + our_tower.height // 2 + 30,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 10,
                                            our_tower.x + our_tower.width // 3, our_tower.y + our_tower.height // 2 + 20,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(our_tower.x + our_tower.width // 4, our_tower.y + our_tower.height // 2 + 40,
                                            our_tower.x + our_tower.width // 5, our_tower.y + our_tower.height // 2,
                                            csmoke_images1, csmoke_images2, 1000)
                                ])
                                enemy_tower.csmoke_effects.extend([
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2 - 20,
                                            enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 3 + 20,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2 + 30,
                                            enemy_tower.x + enemy_tower.width // 3, enemy_tower.y + enemy_tower.height // 2,
                                            csmoke_images1, csmoke_images2, 1000),
                                    CSmokeEffect(enemy_tower.x + enemy_tower.width // 4, enemy_tower.y + enemy_tower.height // 2 + 50,
                                            enemy_tower.x + enemy_tower.width // 5, enemy_tower.y + enemy_tower.height // 2 + 60,
                                            csmoke_images1, csmoke_images2, 1000)
                                ])
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
                                if current_level.music_path and os.path.exists(current_level.music_path):
                                    pygame.mixer.music.load(current_level.music_path)
                                    pygame.mixer.music.play(-1)
                                    current_bgm_path = current_level.music_path
                                    boss_music_active = False
                                else:
                                    print(f"警告: 關卡音樂 '{current_level.music_path}' 未找到。")
                                    pygame.mixer.music.stop()
                                    current_bgm_path = None
                                boss_shockwave_played = False
                                if key_action_sfx.get('other_button'):
                                    key_action_sfx['other_button'].play()
                                print(f"開始關卡: {current_level.name}")
                            else:
                                print("無法開始: 未選取任何貓咪！")
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play()
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()



        elif game_state == "playing":
            # --- 遊戲狀態初始化與使用者介面繪製 ---
            # 獲取當前選定關卡的設定。
            current_level = levels[selected_level]
            # 繪製遊戲的使用者介面元素：暫停按鈕、貓咪出擊按鈕，以及與當前關卡、預算、時間相關的其他UI。
            # 函式返回暫停按鈕的矩形區域以及貓咪按鈕的矩形字典。
            pause_rect, button_rects = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font)

            # --- Boss 出場邏輯 ---
            # 檢查目前螢幕上是否有任何Boss敵人。
            any_boss_present = any(enemy.is_boss for enemy in enemies)
            # 如果有Boss出現且Boss出場震波音效尚未播放。
            if any_boss_present and not boss_shockwave_played:
                # 如果Boss出場音效存在，則播放它。
                if boss_intro_sfx:
                    boss_intro_sfx.play()
                    boss_shockwave_played = True # 標記震波音效已播放。
                    print("Boss 出場，播放震波音效。")
                # 如果當前關卡設定為在Boss出現時切換音樂，且Boss音樂尚未啟用。
                if current_level.switch_music_on_boss and not boss_music_active:
                    # 檢查Boss音樂路徑是否存在且檔案有效。
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        # 載入並循環播放Boss音樂 (-1 表示無限循環)。
                        pygame.mixer.music.load(current_level.boss_music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.boss_music_path # 更新當前背景音樂路徑。
                        boss_music_active = True # 標記Boss音樂已啟用。
                        print("切換到 Boss 音樂。")
                    else:
                        # 如果Boss音樂檔案未找到，則發出警告。
                        print(f"警告: 首領音樂 '{current_level.boss_music_path}' 未找到。")

            # --- 事件處理 (滑鼠點擊與按鍵) ---
            # 處理此幀中Pygame事件佇列中的所有事件。
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    # 如果使用者點擊關閉按鈕，則退出遊戲循環。
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    # 獲取滑鼠點擊的位置。
                    pos = event.pos
                    # 檢查是否點擊了暫停按鈕。
                    if pause_rect.collidepoint(pos):
                        game_state = "paused" # 將遊戲狀態切換為「暫停」。
                        pygame.mixer.music.pause() # 暫停背景音樂。
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play() # 播放一個通用按鈕音效。
                    # --- 滑鼠點擊貓咪部署邏輯 ---
                    # 遍歷所有貓咪部署按鈕。
                    for cat_type, rect in button_rects.items():
                        if rect.collidepoint(pos): # 檢查是否點擊了某個貓咪按鈕。
                            # 獲取所選貓咪類型的花費和冷卻時間。
                            cost = cat_costs.get(cat_type, 0)
                            cooldown = cat_cooldowns.get(cat_type, 0)
                            # 判斷貓咪是否可以部署 (預算是否充足且不在冷卻中)。
                            can_deploy = current_budget >= cost and (current_time - last_spawn_time.get(cat_type, 0) >= cooldown)
                            if can_deploy:
                                current_budget -= cost # 從預算中扣除花費。
                                # 計算貓咪相對於我方塔的生成位置。
                                our_tower_center = current_level.our_tower.x + current_level.our_tower.width / 2
                                # 從貓咪Y軸管理器獲取一個可用的Y軸槽位 (用於兵線管理)。
                                cat_y, cat_slot = cat_y_manager.get_available_y()
                                # 創建一個新的貓咪實例，其類型和位置已計算好。
                                cat = cat_types[cat_type](our_tower_center, cat_y)
                                cat.slot_index = cat_slot # 將槽位索引分配給貓咪。
                                # 微調初始X軸位置，使其在塔中心左側。
                                start_x = our_tower_center - cat.width / 2 - 90
                                cat.x = start_x
                                cats.append(cat) # 將新貓咪添加到活動貓咪列表中。
                                last_spawn_time[cat_type] = current_time # 更新此貓咪類型的上次生成時間。
                                if cat_spawn_sfx.get('default'):
                                    cat_spawn_sfx['default'].play() # 播放通用貓咪生成音效。
                                if key_action_sfx.get('can_deploy'):
                                    key_action_sfx['can_deploy'].play() # 播放成功部署音效。
                                print(f"通過滑鼠生成了 {cat_type} 在 ({cat.x}, {cat.y})")
                            else:
                                if key_action_sfx.get('cannot_deploy'):
                                    key_action_sfx['cannot_deploy'].play() # 播放表示無法部署的音效。
                                # 輸出部署失敗的原因。
                                print(f"無法生成 '{cat_type}': {'金錢不足' if current_budget < cost else '冷卻中'}")
                elif event.type == pygame.KEYDOWN:
                    # 檢查按下的鍵是否對應貓咪部署的快捷鍵。
                    if event.key in cat_key_map:
                        cat_type = cat_key_map[event.key] # 獲取與鍵盤按鍵對應的貓咪類型。
                        # 獲取花費和冷卻時間，邏輯與滑鼠點擊類似。
                        cost = cat_costs.get(cat_type, 0)
                        cooldown = cat_cooldowns.get(cat_type, 0)
                        can_deploy = current_budget >= cost and (current_time - last_spawn_time.get(cat_type, 0) >= cooldown)
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
                            if cat_spawn_sfx.get('default'):
                                cat_spawn_sfx['default'].play()
                            if key_action_sfx.get('can_deploy'):
                                key_action_sfx['can_deploy'].play()
                            print(f"生成了 {cat_type} 在 ({cat.x}, {cat.y})")
                        else:
                            if key_action_sfx.get('cannot_deploy'):
                                key_action_sfx['cannot_deploy'].play()
                            print(f"無法生成 '{cat_type}': {'金錢不足' if current_budget < cost else '冷卻中'}")
                    else:
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play() # 對於其他按鍵，播放通用音效。

            # --- 預算增長邏輯 ---
            # 檢查自上次預算增加以來是否已經足夠的時間 (333毫秒)。
            if current_time - last_budget_increase_time >= 333:
                # 如果當前預算未達到總預算上限。
                if current_budget < total_budget_limitation:
                    # 增加預算，但不超過總預算上限。
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time # 更新上次預算增加的時間。

            # --- 敵人生成邏輯 ---
            # 計算敵人塔的生命值百分比。
            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            # 遍歷當前關卡中定義的所有敵人類型。
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", "default")) # 建立敵人類型和變體的唯一鍵。
                # 判斷敵人是否可以生成：
                # 1. 如果不是「有限制」的敵人，或者
                # 2. 是「有限制」的敵人，但已生成的數量尚未達到上限，
                # 並且敵人塔的生命值百分比符合該敵人類型的生成條件。
                if (not et.get("is_limited", False) or current_level.spawned_counts.get(key, 0) < et.get("spawn_count", 0)) and tower_hp_percent <= et.get("tower_hp_percent", 100):
                    # 獲取該敵人的生成間隔，如果未指定則使用關卡預設間隔。
                    interval = et.get("spawn_interval_1", current_level.spawn_interval)
                    # 獲取該敵人的初始延遲生成時間。
                    initial_delay = et.get("initial_delay", 0)
                    # 如果自上次該類型敵人生成以來已經足夠的時間，且遊戲開始已達到初始延遲。
                    if current_time - current_level.last_spawn_times.get(key, 0) >= interval and current_time - level_start_time >= initial_delay:
                        # 計算敵人塔的中心X軸位置。
                        enemy_tower_center = current_level.enemy_tower.x + current_level.enemy_tower.width / 2
                        # 建立敵人基本配置字典，並用關卡特定的敵人配置進行更新。
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
                        # 從敵人Y軸管理器獲取一個可用的Y軸槽位。
                        enemy_y, enemy_slot = enemy_y_manager.get_available_y()
                        # 創建一個新的敵人實例，傳遞配置和Boss狀態。
                        enemy = enemy_types[et["type"]](enemy_tower_center, enemy_y, is_boss=et.get("is_boss", False), cfg=config)
                        enemy.slot_index = enemy_slot # 分配槽位索引。
                        # 微調初始X軸位置，使其在塔中心右側。
                        start_x = enemy_tower_center - enemy.width / 2 + 50
                        enemy.x = start_x
                        enemies.append(enemy) # 將新敵人添加到活動敵人列表中。
                        current_level.spawned_counts[key] += 1 # 增加該類型敵人的生成計數。
                        current_level.last_spawn_times[key] = current_time # 更新該類型敵人的上次生成時間。

            # --- 關卡完成檢查 ---
            # 檢查所有有限制數量的敵人都已經生成 (這不代表他們已被擊敗)。
            current_level.all_limited_spawned = current_level.check_all_limited_spawned()

            # --- 單位狀態更新 ---
            # 更新所有貓咪的狀態效果 (例如，緩速、暈眩等)。
            for cat in cats:
                cat.update_status_effects(current_time)
            # 更新所有敵人的狀態效果。
            for enemy in enemies:
                enemy.update_status_effects(current_time)

            # --- 戰鬥邏輯更新與特效管理 ---
            # 執行核心戰鬥邏輯：貓咪與敵人互動、攻擊、傷害計算等。
            # 函式返回新的震波特效列表。
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects, current_budget, battle_sfx)
            # 更新靈魂 (如果有的話) 的狀態，並移除已完成的靈魂。
            souls = [soul for soul in souls if soul.update()]

            # --- 繪製所有遊戲元素 ---
            # 繪製我方塔。
            our_tower.draw(screen)
            # 如果敵人塔存在，則繪製敵人塔。
            if enemy_tower:
                enemy_tower.draw(screen)
            # 繪製所有靈魂特效。
            for soul in souls:
                soul.draw(screen)
            # 繪製所有震波特效。
            for shockwave in shockwave_effects:
                shockwave.draw(screen)
            # 繪製所有活動貓咪。
            for cat in cats:
                cat.draw(screen)
            # 繪製所有活動敵人。
            for enemy in enemies:
                enemy.draw(screen)
            pygame.display.flip() # 更新整個螢幕以顯示所有繪製的內容。

            # --- 遊戲勝利/失敗條件檢查 ---
            # 檢查我方塔的生命值是否小於或等於0。
            if our_tower.hp <= 0:
                if status != "lose": # 確保只執行一次失敗邏輯。
                    status = "lose" # 設定遊戲狀態為「失敗」。
                    game_state = "end" # 切換主遊戲狀態為「結束」。
                    pygame.mixer.music.stop() # 停止背景音樂。
                    current_bgm_path = None # 清除當前背景音樂路徑。
                    boss_music_active = False # 關閉Boss音樂活躍標記。
                    boss_shockwave_played = False # 重置Boss震波音效標記。
                    if defeat_sfx:
                        defeat_sfx.play() # 播放失敗音效。
                        print("播放失敗音效。")
                    print("我方塔被摧毀，遊戲結束。")
            # 檢查敵人塔是否存在且其生命值是否小於或等於0。
            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory": # 確保只執行一次勝利邏輯。
                    status = "victory" # 設定遊戲狀態為「勝利」。
                    game_state = "end" # 切換主遊戲狀態為「結束」。
                    pygame.mixer.music.stop() # 停止背景音樂。
                    current_bgm_path = None # 清除當前背景音樂路徑。
                    boss_music_active = False # 關閉Boss音樂活躍標記。
                    boss_shockwave_played = False # 重置Boss震波音效標記。
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
                        current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("戰鬥結束，返回關卡選擇。")
                    elif continue_rect.collidepoint(pos):
                        game_state = "playing"
                        pygame.mixer.music.unpause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("恢復戰鬥。")

        elif game_state == "end":
            current_level = levels[selected_level]
            is_last_level = selected_level == len(levels) - 1
            is_first_completion = selected_level not in completed_levels

            victory_display_time = getattr(pygame.time, "victory_display_time", 0)
            if status == "victory" and victory_display_time == 0:
                pygame.time.victory_display_time = pygame.time.get_ticks()
                if victory_sfx:
                    victory_sfx.set_volume(0.8)
                    victory_sfx.play(loops=0, maxtime=0)
                    # 註解掉 pygame.time.wait，因為瀏覽器不支援
                    # pygame.time.wait(100)
                    busy_channels = sum(pygame.mixer.Channel(i).get_busy() for i in range(pygame.mixer.get_num_channels()))
                    print(f"播放勝利音效，當前使用頻道數: {busy_channels}")

            # 使用 draw_end_screen 返回的 continue_rect
            continue_rect = draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            # 臨時禁用儲存
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"儲存關卡 {selected_level} 完成進度。")
                            except Exception as e:
                                print(f"儲存進度時發生錯誤: {e}")
                        if status == "victory" and is_last_level and is_first_completion:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            print("準備進入結局動畫。")
                        else:
                            game_state = "level_selection"
                            our_tower = None
                            enemy_tower = None
                            cats.clear()
                            enemies.clear()
                            souls.clear()
                            shockwave_effects.clear()
                            current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        setattr(pygame.time, "victory_display_time", 0)
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    pos = event.pos
                    if continue_rect and continue_rect.collidepoint(pos):
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            # 臨時禁用儲存
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"儲存關卡 {selected_level} 完成進度。")
                            except Exception as e:
                                print(f"儲存進度時發生錯誤: {e}")
                        if status == "victory" and is_last_level and is_first_completion:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            print("準備進入結局動畫。")
                        else:
                            game_state = "level_selection"
                            our_tower = None
                            enemy_tower = None
                            cats.clear()
                            enemies.clear()
                            souls.clear()
                            shockwave_effects.clear()
                            current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        setattr(pygame.time, "victory_display_time", 0)
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()

        elif game_state == "ending":
            ending_start_time = getattr(pygame.time, "ending_start_time", pygame.time.get_ticks())
            setattr(pygame.time, "ending_start_time", ending_start_time)
            ending_duration = 35000
            fade_in_duration = 5000

            # 避免重新初始化混音器，註解掉 pygame.mixer.quit()
            if not hasattr(pygame.time, "ending_music_initialized") or not pygame.time.ending_music_initialized:
                # pygame.mixer.quit()  # 註解掉
                # pygame.mixer.init()  # 註解掉
                pygame.mixer.set_num_channels(16)
                pygame.mixer.music.set_volume(0.5)
                print(f"重新初始化混音器，頻道數: {pygame.mixer.get_num_channels()}")
                ending_music_path = "audio/TBC/005.ogg"
                pygame.mixer.music.stop()
                pygame.mixer.music.unload()
                if os.path.exists(ending_music_path):
                    pygame.mixer.music.load(ending_music_path)
                    pygame.mixer.music.set_volume(0.5)
                    pygame.mixer.music.play(-1)
                    # 註解掉 pygame.time.wait，因為瀏覽器不支援
                    # pygame.time.wait(200)  # 確保音樂開始
                    current_bgm_path = ending_music_path
                    pygame.time.ending_music_initialized = True
                    print(f"播放結局音樂: {ending_music_path}, 當前音樂狀態: {pygame.mixer.music.get_busy()}")
                else:
                    print(f"警告: 結局音樂 '{ending_music_path}' 未找到。")
                    pygame.time.ending_music_initialized = False

            elapsed_time = current_time - ending_start_time
            current_fade_alpha = int(255 * min(1.0, elapsed_time / fade_in_duration))
            y_offset = screen.get_height()
            if elapsed_time >= fade_in_duration:
                text_progress_time = elapsed_time - fade_in_duration
                text_scroll_duration = ending_duration - fade_in_duration
                text_scroll_progress = min(1.0, text_progress_time / text_scroll_duration)
                y_offset = screen.get_height() * (1 - text_scroll_progress * text_scroll_progress)

            skip_rect = draw_ending_animation(screen, font, y_offset, current_fade_alpha)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if skip_rect and skip_rect.collidepoint(event.pos):
                        game_state = "level_selection"
                        our_tower = None
                        enemy_tower = None
                        cats.clear()
                        enemies.clear()
                        souls.clear()
                        shockwave_effects.clear()
                        current_budget = 1000
                        pygame.mixer.music.stop()
                        current_bgm_path = None
                        boss_music_active = False
                        boss_shockwave_played = False
                        setattr(pygame.time, "ending_start_time", 0)
                        delattr(pygame.time, "ending_music_initialized")  # 重置音樂初始化標記
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                        print("已跳過結局動畫。")

            if elapsed_time >= ending_duration + DELAY_TIME:
                game_state = "level_selection"
                our_tower = None
                enemy_tower = None
                cats.clear()
                enemies.clear()
                souls.clear()
                shockwave_effects.clear()
                current_budget = 1000
                pygame.mixer.music.stop()
                current_bgm_path = None
                boss_music_active = False
                boss_shockwave_played = False
                setattr(pygame.time, "ending_start_time", 0)
                delattr(pygame.time, "ending_music_initialized")  # 重置音樂初始化標記
                print("結局動畫播放完畢。")

        await asyncio.sleep(0)
        clock.tick(FPS)