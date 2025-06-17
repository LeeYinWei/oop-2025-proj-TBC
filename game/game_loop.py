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

    # 載入已完成關卡
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
            current_level = levels[selected_level]
            pause_rect = draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font)

            any_boss_present = any(enemy.is_boss for enemy in enemies)
            if any_boss_present and not boss_shockwave_played:
                if boss_intro_sfx:
                    boss_intro_sfx.play()
                    boss_shockwave_played = True
                    print("Boss 出場，播放震波音效。")
                if current_level.switch_music_on_boss and not boss_music_active:
                    if current_level.boss_music_path and os.path.exists(current_level.boss_music_path):
                        pygame.mixer.music.load(current_level.boss_music_path)
                        pygame.mixer.music.play(-1)
                        current_bgm_path = current_level.boss_music_path
                        boss_music_active = True
                        print("切換到 Boss 音樂。")
                    else:
                        print(f"警告: 首領音樂 '{current_level.boss_music_path}' 未找到。")

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if pause_rect.collidepoint(event.pos):
                        game_state = "paused"
                        pygame.mixer.music.pause()
                        if key_action_sfx.get('other_button'):
                            key_action_sfx['other_button'].play()
                elif event.type == pygame.KEYDOWN:
                    if event.key in cat_key_map:
                        cat_type = cat_key_map[event.key]
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
                            key_action_sfx['other_button'].play()

            if current_time - last_budget_increase_time >= 333:
                if current_budget < total_budget_limitation:
                    current_budget = min(current_budget + budget_rate, total_budget_limitation)
                    last_budget_increase_time = current_time

            tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100 if enemy_tower else 0
            for et in current_level.enemy_types:
                key = (et["type"], et.get("variant", "default"))
                if (not et.get("is_limited", False) or current_level.spawned_counts.get(key, 0) < et.get("spawn_count", 0)) and tower_hp_percent <= et.get("tower_hp_percent", 100):
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
                        enemy = enemy_types[et["type"]](enemy_tower_center, enemy_y, is_boss=et.get("is_boss", False), cfg=config)
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
            shockwave_effects = update_battle(cats, enemies, our_tower, enemy_tower, current_time, souls, cat_y_manager, enemy_y_manager, shockwave_effects, current_budget, battle_sfx)
            souls = [soul for soul in souls if soul.update()]

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
                if status != "lose":
                    status = "lose"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played = False
                    if defeat_sfx:
                        defeat_sfx.play()
                        print("播放失敗音效。")
                    print("我方塔被摧毀，遊戲結束。")
            elif enemy_tower and enemy_tower.hp <= 0:
                if status != "victory":
                    status = "victory"
                    game_state = "end"
                    pygame.mixer.music.stop()
                    current_bgm_path = None
                    boss_music_active = False
                    boss_shockwave_played = False
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
                    pygame.time.wait(100)
                    busy_channels = sum(pygame.mixer.Channel(i).get_busy() for i in range(pygame.mixer.get_num_channels()))
                    print(f"播放勝利音效，當前使用頻道數: {busy_channels}")

            draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, victory_display_time)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if status == "victory" and is_first_completion:
                            completed_levels.add(selected_level)
                            try:
                                with open(save_file, "w") as f:
                                    json.dump(list(completed_levels), f)
                                print(f"儲存關卡 {selected_level} 完成進度。")
                            except Exception as e:
                                print(f"儲存進度時發生錯誤: {e}")
                        if status == "victory" and is_last_level and is_first_completion:
                            game_state = "ending"
                            pygame.time.ending_start_time = pygame.time.get_ticks()
                            # 音樂初始化移至 ending 狀態
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

            # 音樂初始化
            if not hasattr(pygame.time, "ending_music_initialized") or not pygame.time.ending_music_initialized:
                pygame.mixer.quit()
                pygame.mixer.init()
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
                    pygame.time.wait(200)  # 確保音樂開始
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