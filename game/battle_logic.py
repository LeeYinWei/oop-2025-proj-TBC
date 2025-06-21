from .entities import Enemy, Cat, Soul, Tower, ShockwaveEffect, YManager
import pygame

# 在函式簽名中加入 battle_sfx 參數，並給予預設值 None，以防止舊的呼叫報錯。
# 但請務必確保在 main_game_loop.py 中呼叫時傳入 battle_sfx。
def update_battle(cats, enemies, our_tower, enemy_tower, now, souls, cat_y_manager, enemy_y_manager, shockwave_effects=None, current_budget=0, battle_sfx=None):
    # 如果 shockwave_effects 列表為 None（表示首次呼叫），則初始化為空列表。
    if shockwave_effects is None:
        shockwave_effects = []

    # 確保 battle_sfx 字典存在且是字典，避免在音效未載入時出錯。
    if battle_sfx is None:
        battle_sfx = {}

    # --- 重置單位狀態和更新特效 ---
    # 遍歷所有貓咪，重置其攻擊狀態和接觸點，並更新所有視覺特效。
    for cat in cats:
        cat.is_attacking = False  # 假設貓咪本回合不攻擊，除非後續邏輯確認其正在攻擊。
        cat.contact_points = []   # 清除上次攻擊的接觸點。
        cat.update_smoke_effects()    # 更新煙霧特效。
        cat.update_physic_effects()   # 更新物理特效。
        cat.update_electric_effects() # 更新電擊特效。
        cat.update_gas_effects()      # 更新氣體特效。
    
    # 遍歷所有敵人，重置其攻擊狀態和接觸點，並更新所有視覺特效。
    for enemy in enemies:
        enemy.is_attacking = False  # 假設敵人本回合不攻擊。
        enemy.contact_points = []   # 清除上次攻擊的接觸點。
        enemy.update_smoke_effects()
        enemy.update_physic_effects()
        enemy.update_electric_effects()
        enemy.update_gas_effects()

    # 重置我方塔樓的接觸點。
    our_tower.contact_points = []
    # 如果敵人塔樓存在，重置其接觸點。
    if enemy_tower:
        enemy_tower.contact_points = []

    # 更新塔樓的所有視覺特效。
    our_tower.update_smoke_effects()
    our_tower.update_physic_effects()
    our_tower.update_electric_effects()
    our_tower.update_gas_effects()
    if enemy_tower:
        enemy_tower.update_smoke_effects()
        enemy_tower.update_physic_effects()
        enemy_tower.update_electric_effects()
        enemy_tower.update_gas_effects()

    # --- Boss 出場震波特效觸發 ---
    # 檢查新生成的 Boss，觸發出場震波特效。
    for enemy in enemies:
        # 如果敵人是 Boss 且尚未觸發過出生震波。
        if enemy.is_boss and not getattr(enemy, 'has_spawn_shockwave', False):
            # 計算震波的中心位置。
            shockwave_x = enemy.x + enemy.width // 2
            shockwave_y = enemy.y + enemy.height // 2 - 150 # 微調Y軸位置。
            # 創建一個新的震波特效實例。
            shockwave = ShockwaveEffect(shockwave_x, shockwave_y, duration=1000, scale=1.0)
            shockwave_effects.append(shockwave) # 將震波加入特效列表。
            enemy.has_spawn_shockwave = True  # 標記已觸發，避免重複生成震波。
            # print(f"Boss {enemy} spawned with shockwave at ({shockwave_x}, {shockwave_y})") # 偵錯用。

    # --- 貓咪行為邏輯 (移動與攻擊) ---
    for cat in cats:
        # 重新定義貓咪的攻擊範圍矩形，以貓咪中心點為基準，並涵蓋其攻擊範圍。
        cat_center_x = cat.x + cat.width // 2
        cat_attack_zone = pygame.Rect(
            cat_center_x - cat.attack_range // 2,     # 攻擊範圍的起始 X 點。
            cat.y - cat.height // 2,                  # 攻擊範圍的起始 Y 點 (從中心向上擴展)。
            cat.attack_range,                         # 攻擊範圍的寬度。
            cat.height + cat.attack_range             # 攻擊範圍的高度 (涵蓋角色高度和攻擊範圍)。
        )
        
        # 如果貓咪處於「蓄力」、「攻擊」或「恢復」動畫狀態。
        if cat.anim_state in ["windup", "attacking", "recovery"]:
            # 如果貓咪尚未完成當前攻擊動作。
            if not cat.done_attack:
                cat.done_attack = True # 標記攻擊動作已完成 (只觸發一次傷害)。
                # print(f"Cat attacking, anim_state: {cat.anim_state}, zone: {cat_attack_zone}") # 偵錯用。
                
                # --- 貓咪 AOE (範圍攻擊) 邏輯 ---
                if cat.is_aoe:
                    # 找出所有與貓咪攻擊範圍重疊的敵人。
                    targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
                    # 如果敵人塔樓存在且與攻擊範圍重疊，則將其也加入目標。
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        targets.append(enemy_tower)
                    
                    # 對每個目標進行攻擊。
                    for tar in targets:
                        # 如果目標是敵人單位。
                        if isinstance(tar, Enemy):
                            enemy = tar
                            old_hp = enemy.hp # 記錄攻擊前的生命值。
                            enemy.take_damage(cat.atk, cat.attack_type) # 敵人受到傷害。
                            
                            # 如果敵人還有生命值 (未被擊敗)。
                            if enemy.hp > 0:
                                # 計算跨越了多少個擊退生命值閾值。
                                # `min` 確保不會超過最大閾值索引。
                                thresholds_crossed = min(int(old_hp / enemy.kb_threshold), int(enemy.max_hp / enemy.kb_threshold) - 1) - int(enemy.hp / enemy.kb_threshold)
                                
                                print("enemy", old_hp// enemy.kb_threshold,  enemy.max_hp // enemy.kb_threshold, enemy.hp //enemy.kb_threshold, thresholds_crossed) # 偵錯用。
                                
                                # 如果跨越了閾值，觸發擊退。
                                if thresholds_crossed > 0:
                                    print("enemy knock back") # 偵錯用。
                                    enemy.knock_back()
                            enemy.last_hp = enemy.hp # 更新敵人的上次生命值。
                            
                            # 計算攻擊接觸點，用於顯示特效。
                            contact_rect = cat_attack_zone.clip(tar.get_rect())
                            contact_point = contact_rect.center
                            enemy.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                            
                            # 播放攻擊到敵方角色的音效 (021.ogg)。
                            if battle_sfx.get('hit_unit'):
                                battle_sfx['hit_unit'].play()
                        # 如果目標是塔樓。
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.take_damage(cat.atk, cat.attack_type) # 塔樓受到傷害。
                            
                            # 計算攻擊接觸點。
                            contact_rect = cat_attack_zone.clip(tar.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                            
                            # 播放攻擊到敵方塔樓的音效 (022.ogg)。
                            if battle_sfx.get('hit_tower'):
                                battle_sfx['hit_tower'].play()
                
                # --- 貓咪單體攻擊邏輯 ---
                else: # 非 AOE 攻擊。
                    # 首先檢查是否攻擊到敵人塔樓。
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        tower = enemy_tower
                        tower.take_damage(cat.atk, cat.attack_type) # 塔樓受到傷害。
                        
                        # 計算攻擊接觸點。
                        contact_rect = cat_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        cat.contact_points.append(contact_point)
                        
                        # 播放攻擊到敵方塔樓的音效 (022.ogg)。
                        if battle_sfx.get('hit_tower'):
                            battle_sfx['hit_tower'].play()
                    else:
                        # 遍歷所有敵人，尋找第一個被命中的敵人。
                        for enemy in enemies:
                            if cat_attack_zone.colliderect(enemy.get_rect()):
                                old_hp = enemy.hp # 記錄攻擊前的生命值。
                                enemy.take_damage(cat.atk, cat.attack_type) # 敵人受到傷害。
                                
                                # 如果敵人還有生命值 (未被擊敗)。
                                if enemy.hp > 0:
                                    # 計算跨越了多少個擊退生命值閾值。
                                    thresholds_crossed = min(int(old_hp / enemy.kb_threshold), int(enemy.max_hp / enemy.kb_threshold) - 1)  - int(enemy.hp / enemy.kb_threshold)
                                    print("enemy", old_hp// enemy.kb_threshold,  enemy.max_hp // enemy.kb_threshold, enemy.hp //enemy.kb_threshold, thresholds_crossed) # 偵錯用。
                                    
                                    # 如果跨越了閾值，觸發擊退。
                                    if thresholds_crossed > 0:
                                        print("enemy knock back") # 偵錯用。
                                        enemy.knock_back()
                                enemy.last_hp = enemy.hp # 更新敵人的上次生命值。
                                
                                # 計算攻擊接觸點。
                                contact_rect = cat_attack_zone.clip(enemy.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                
                                # 播放攻擊到敵方角色的音效 (021.ogg)。
                                if battle_sfx.get('hit_unit'):
                                    battle_sfx['hit_unit'].play()
                                break  # 非 AOE 攻擊，命中一個敵人後就停止，不再檢查其他敵人。
        
        # --- 貓咪 AOE (範圍攻擊) 的判斷與動畫觸發 ---
        elif cat.is_aoe:
            # 找出攻擊範圍內的所有目標。
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
            
            # 如果有目標且攻擊冷卻已過，則觸發攻擊動畫。
            if targets and now - cat.last_attack_time >= cat.attack_interval:
                cat.anim_state = "windup"       # 進入蓄力動畫狀態。
                cat.anim_start_time = now       # 記錄動畫開始時間。
                cat.last_attack_time = now      # 更新上次攻擊時間。
                cat.is_attacking = True         # 標記貓咪正在攻擊。
            # 如果有目標但攻擊仍在冷卻中，則保持待機狀態。
            elif targets and now - cat.last_attack_time < cat.attack_interval:
                cat.anim_state = "idle"
            # 如果沒有目標，則貓咪移動。
            elif not targets:
                cat.move()
        
        # --- 貓咪單體攻擊的判斷與動畫觸發 ---
        else: # 非 AOE 貓咪的行為邏輯。
            target_in_range = False # 標記是否有目標在攻擊範圍內。
            # 首先檢查敵人塔樓是否在攻擊範圍內。
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                target_in_range = True
                # 如果敵人塔樓在範圍內且攻擊冷卻已過，則觸發攻擊動畫。
                if now - cat.last_attack_time >= cat.attack_interval:
                    cat.anim_state = "windup"
                    cat.anim_start_time = now
                    cat.last_attack_time = now
                    cat.is_attacking = True
                else: # 否則保持待機。
                    cat.anim_state = "idle"
            else:
                # 遍歷所有敵人，檢查是否有敵人在攻擊範圍內。
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        target_in_range = True
                        # 如果敵人在範圍內且攻擊冷卻已過，則觸發攻擊動畫。
                        if now - cat.last_attack_time >= cat.attack_interval:
                            cat.anim_state = "windup"
                            cat.anim_start_time = now
                            cat.last_attack_time = now
                            cat.is_attacking = True
                        break # 找到目標就停止遍歷。
                # 如果有目標在範圍內但貓咪不在攻擊狀態，則保持待機。
                if target_in_range and not cat.is_attacking:
                    cat.anim_state = "idle"
            # 如果沒有任何目標在攻擊範圍內，則貓咪移動。
            if not target_in_range:
                cat.move()

    # --- 敵人行為邏輯 (移動與攻擊) ---
    for enemy in enemies:
        # 重新定義敵人的攻擊範圍矩形，以敵人中心點為基準。
        enemy_center_x = enemy.x + enemy.width // 2
        enemy_attack_zone = pygame.Rect(
            enemy_center_x - enemy.attack_range // 2,
            enemy.y - enemy.height // 2,
            enemy.attack_range,
            enemy.height + enemy.attack_range
        )
        
        # 如果敵人處於「蓄力」、「攻擊」或「恢復」動畫狀態。
        if enemy.anim_state in ["windup", "attacking", "recovery"]:
            # 如果敵人尚未完成當前攻擊動作。
            if not enemy.done_attack:
                enemy.done_attack = True # 標記攻擊動作已完成。
                # print(f"Enemy attacking, anim_state: {enemy.anim_state}, zone: {enemy_attack_zone}") # 偵錯用。
                
                # --- 敵人 AOE (範圍攻擊) 邏輯 ---
                if enemy.is_aoe:
                    # 找出所有與敵人攻擊範圍重疊的貓咪。
                    targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
                    # 如果我方塔樓與攻擊範圍重疊，則將其也加入目標。
                    if enemy_attack_zone.colliderect(our_tower.get_rect()):
                        targets.append(our_tower)
                    
                    # 對每個目標進行攻擊。
                    for tar in targets:
                        # 如果目標是貓咪單位。
                        if isinstance(tar, Cat):
                            c = tar
                            old_hp = c.hp # 記錄攻擊前的生命值。
                            c.take_damage(enemy.atk, enemy.attack_type) # 貓咪受到傷害。
                            
                            # 如果貓咪還有生命值。
                            if c.hp > 0:
                                # 計算跨越了多少個擊退生命值閾值。
                                thresholds_crossed = min(int(old_hp / c.kb_threshold), int(c.max_hp / c.kb_threshold) - 1) - int(c.hp / c.kb_threshold)
                                
                                print("cataoe", old_hp// c.kb_threshold,  c.max_hp // c.kb_threshold, c.hp //c.kb_threshold, thresholds_crossed) # 偵錯用。
                                
                                # 如果跨越了閾值，觸發擊退。
                                if thresholds_crossed > 0:
                                    print("cat knock back") # 偵錯用。
                                    c.knock_back()
                            c.last_hp = c.hp # 更新貓咪的上次生命值。
                            
                            # 計算攻擊接觸點。
                            contact_rect = enemy_attack_zone.clip(tar.get_rect())
                            contact_point = contact_rect.center
                            c.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                            
                            # 播放攻擊到我方角色的音效 (021.ogg)。
                            if battle_sfx.get('hit_unit'):
                                battle_sfx['hit_unit'].play()
                        # 如果目標是塔樓。
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.take_damage(enemy.atk, enemy.attack_type) # 塔樓受到傷害。
                            
                            # 計算攻擊接觸點。
                            contact_rect = enemy_attack_zone.clip(tar.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                            
                            # 播放攻擊到我方塔樓的音效 (022.ogg)。
                            if battle_sfx.get('hit_tower'):
                                battle_sfx['hit_tower'].play()
                
                # --- 敵人單體攻擊邏輯 ---
                else: # 非 AOE 攻擊。
                    # 首先檢查是否攻擊到我方塔樓。
                    if enemy_attack_zone.colliderect(our_tower.get_rect()):
                        tower = our_tower
                        tower.take_damage(enemy.atk, enemy.attack_type) # 塔樓受到傷害。
                        
                        # 計算攻擊接觸點。
                        contact_rect = enemy_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                        
                        # 播放攻擊到我方塔樓的音效 (022.ogg)。
                        if battle_sfx.get('hit_tower'):
                            battle_sfx['hit_tower'].play()
                    else:
                        # 遍歷所有貓咪，尋找第一個被命中的貓咪。
                        for cat in cats:
                            if enemy_attack_zone.colliderect(cat.get_rect()):
                                old_hp = cat.hp # 記錄攻擊前的生命值。
                                cat.take_damage(enemy.atk, enemy.attack_type) # 貓咪受到傷害。
                                
                                # 如果貓咪還有生命值。
                                if cat.hp > 0:
                                    # 計算跨越了多少個擊退生命值閾值。
                                    thresholds_crossed = min(int(old_hp / cat.kb_threshold), int(cat.max_hp / cat.kb_threshold)- 1) - int(cat.hp / cat.kb_threshold)
                                    print("cat", old_hp// cat.kb_threshold,  cat.max_hp // cat.kb_threshold, cat.hp //cat.kb_threshold, thresholds_crossed) # 偵錯用。
                                    
                                    # 如果跨越了閾值，觸發擊退。
                                    if thresholds_crossed > 0:
                                        print("cat knock back") # 偵錯用。
                                        cat.knock_back()
                                cat.last_hp = cat.hp # 更新貓咪的上次生命值。
                                
                                # 計算攻擊接觸點。
                                contact_rect = enemy_attack_zone.clip(cat.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                
                                # 播放攻擊到我方角色的音效 (021.ogg)。
                                if battle_sfx.get('hit_unit'):
                                    battle_sfx['hit_unit'].play()
                                break # 命中一個貓咪就停止。
        
        # --- 敵人 AOE (範圍攻擊) 的判斷與動畫觸發 ---
        elif enemy.is_aoe:
            # 找出攻擊範圍內的所有目標。
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            
            # 如果有目標且攻擊冷卻已過，則觸發攻擊動畫。
            if targets and now - enemy.last_attack_time >= enemy.attack_interval:
                enemy.anim_state = "windup"
                enemy.anim_start_time = now
                enemy.last_attack_time = now
                enemy.is_attacking = True
            # 如果有目標但攻擊仍在冷卻中，則保持待機狀態。
            elif targets and now - enemy.last_attack_time < enemy.attack_interval:
                enemy.anim_state = "idle"
            # 如果沒有目標，則敵人移動。
            elif not targets:
                enemy.move()
        
        # --- 敵人單體攻擊的判斷與動畫觸發 ---
        else: # 非 AOE 敵人的行為邏輯。
            target_in_range = False # 標記是否有目標在攻擊範圍內。
            # 首先檢查我方塔樓是否在攻擊範圍內。
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
                target_in_range = True
                # 如果我方塔樓在範圍內且攻擊冷卻已過，則觸發攻擊動畫。
                if now - enemy.last_attack_time >= enemy.attack_interval:
                    enemy.anim_state = "windup"
                    enemy.anim_start_time = now
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
                else: # 否則保持待機。
                    enemy.anim_state = "idle"
            else:
                # 遍歷所有貓咪，檢查是否有貓咪在攻擊範圍內。
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        target_in_range = True
                        # 如果貓咪在範圍內且攻擊冷卻已過，則觸發攻擊動畫。
                        if now - enemy.last_attack_time >= enemy.attack_interval:
                            enemy.anim_state = "windup"
                            enemy.anim_start_time = now
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                        break # 找到目標就停止遍歷。
                # 如果有目標在範圍內但敵人不在攻擊狀態，則保持待機。
                if target_in_range and not enemy.is_attacking:
                    enemy.anim_state = "idle"
            # 如果沒有任何目標在攻擊範圍內，則敵人移動。
            if not target_in_range:
                enemy.move()

    # --- 震波擊退效果處理 ---
    # 遍歷當前所有震波特效，並處理其效果。
    for effect in shockwave_effects[:]: # 使用[:]建立副本以避免在迭代時修改列表導致問題。
        # 如果震波特效仍在活動 (update 返回 True)。
        if effect.update(now):
            # 讓所有貓咪執行擊退效果 (後退 50 像素)。
            for cat in cats:
                # 確保貓咪不在攻擊狀態且尚未被震波擊退過。
                if not cat.is_attacking and not getattr(cat, 'has_retreated', False):
                    cat.start_retreat(50) # 貓咪開始後退。
                    cat.anim_start_time = now # 更新動畫開始時間。
                    cat.has_retreated = True  # 標記貓咪已因震波而後退。
        else:
            shockwave_effects.remove(effect) # 如果震波特效已結束，則從列表中移除。

    # --- 中央處理敵人死亡與獎勵 ---
    new_enemies = [] # 用於存放存活的敵人。
    for enemy in enemies:
        if enemy.hp > 0:
            new_enemies.append(enemy) # 如果敵人還有生命值，則加入新列表。
        else:
            souls.append(Soul(enemy.x + enemy.width // 2, enemy.y)) # 敵人死亡時生成一個靈魂。
            enemy_y_manager.release_y(enemy.slot_index) # 釋放該敵人佔用的Y軸槽位。
            current_budget += enemy.reward # 將敵人的獎勵加到當前預算中。
            # 播放敵人死亡音效 (023.ogg)。
            if battle_sfx.get('unit_die'):
                battle_sfx['unit_die'].play()
            # print(f"Enemy defeated! Gained {enemy.reward} budget. Current budget: {current_budget}") # 可選：打印日誌。
    enemies[:] = new_enemies # 更新敵人列表，移除已死亡的敵人。

    # --- 中央處理貓咪死亡 ---
    new_cats = [] # 用於存放存活的貓咪。
    for cat in cats:
        if cat.hp > 0:
            new_cats.append(cat) # 如果貓咪還有生命值，則加入新列表。
        else:
            souls.append(Soul(cat.x + cat.width // 2, cat.y)) # 貓咪死亡時生成一個靈魂。
            cat_y_manager.release_y(cat.slot_index) # 釋放該貓咪佔用的Y軸槽位。
            # 播放貓咪死亡音效 (023.ogg)。
            if battle_sfx.get('unit_die'):
                battle_sfx['unit_die'].play()
    cats[:] = new_cats # 更新貓咪列表，移除已死亡的貓咪。

    # --- 塔樓生命值檢查與修正 ---
    # 如果敵人塔樓生命值小於或等於0，將其生命值設為0 (防止負數)。
    if enemy_tower and enemy_tower.hp <= 0:
        enemy_tower.hp = 0
    # 如果我方塔樓生命值小於或等於0，將其生命值設為0。
    if our_tower.hp <= 0:
        our_tower.hp = 0

    # 返回更新後的震波特效列表。
    return shockwave_effects