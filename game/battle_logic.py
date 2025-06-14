from .entities import Enemy, Cat, Soul, Tower, ShockwaveEffect, YManager
import pygame

def update_battle(cats, enemies, our_tower, enemy_tower, now, souls,cat_y_manager,enemy_y_manager, shockwave_effects=None):
    if shockwave_effects is None:
        shockwave_effects = []

    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
        cat.update_smoke_effects()  # 更新煙霧效果
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
        enemy.update_smoke_effects()  # 更新煙霧效果
    our_tower.contact_points = []
    if enemy_tower:
        enemy_tower.contact_points = []

    # 檢查是否有 boss 出現並觸發單次震波
    boss_present = any(enemy.is_boss for enemy in enemies)
    if boss_present and enemy_tower and not shockwave_effects:  # 只在無震波時觸發一次
        shockwave_effects.append(ShockwaveEffect(enemy_tower.x + enemy_tower.width // 2, enemy_tower.y + enemy_tower.height // 2))

    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.anim_state in ["windup", "attacking", "recovery"]:
            if cat.done_attack == False:
                # Windup phase is done -> attack
                cat.done_attack = True# 攻擊完成標誌，在./entities/cat update_animation recovery結束後重製
                print("A cat is attacking!")
                print("cat anim state:", cat.anim_state)
                print("cat attack zone:", cat_attack_zone)
                if cat.is_aoe:
                    targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        targets.append(enemy_tower)
                    for tar in targets:
                        if isinstance(tar, Enemy):
                            enemy = tar
                            old_hp = enemy.hp
                            enemy.take_damage(cat.atk)  # 使用 take_damage 生成煙霧
                            if enemy.hp > 0:
                                thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                if thresholds_crossed > 0:
                                    enemy.knock_back()
                            enemy.last_hp = enemy.hp
                            contact_rect = cat_attack_zone.clip(enemy.get_rect())
                            contact_point = contact_rect.center
                            enemy.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.hp -= cat.atk
                            contact_rect = cat_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                else:
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        tower = enemy_tower
                        tower.hp -= cat.atk
                        contact_rect = cat_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        cat.contact_points.append(contact_point)
                    else:
                        #print("cat attacking enemy")
                        #print("enemies:", enemies)
                        for enemy in enemies:
                            if cat_attack_zone.colliderect(enemy.get_rect()):
                                old_hp = enemy.hp
                                #print("enemy taking damage:", enemy.hp, "->", enemy.hp - cat.atk)
                                enemy.take_damage(cat.atk)  # 使用 take_damage 生成煙霧
                                #print("enemy hp after take_damage:", enemy.hp)
                                if enemy.hp > 0:
                                    thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                    if thresholds_crossed > 0:
                                        print("enemy knock back")
                                        enemy.knock_back()
                                #print("enemy hp after take_damage:", enemy.hp)
                                enemy.last_hp = enemy.hp
                                contact_rect = cat_attack_zone.clip(enemy.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                #print("enemy hp after attack:", enemy.hp)
                                break
        # cat.anim_state in idle or moving                 
        elif cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
            # Check if there are targets in the attack zone
            if targets and now - cat.last_attack_time >= cat.attack_interval:
                cat.anim_state = "windup"
                cat.anim_start_time = now
                cat.last_attack_time = now
                cat.is_attacking = True
            elif targets and now - cat.last_attack_time < cat.attack_interval:
                cat.anim_state = "idle"
            elif not targets:
                cat.move()
        else:
            target_in_range = False
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):# 檢查塔是否在攻擊範圍內
                target_in_range = True
                if now - cat.last_attack_time >= cat.attack_interval:#在範圍內且攻擊間隔已過
                    cat.anim_state = "windup"
                    cat.anim_start_time = now
                    cat.last_attack_time = now
                    cat.is_attacking = True
                else: # 在範圍內但攻擊間隔未過
                    cat.anim_state = "idle"
            else:
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        target_in_range = True
                        # 檢查攻擊間隔是否已過
                        if now - cat.last_attack_time >= cat.attack_interval:
                            cat.anim_state = "windup"
                            cat.anim_start_time = now
                            cat.last_attack_time = now
                            cat.is_attacking = True
                        break  # 只找第一個目標
                    
                if target_in_range == True and cat.is_attacking == False: # 在範圍內但攻擊間隔未過
                    cat.anim_state = "idle"

            if target_in_range == False:
                cat.move()

    for enemy in enemies:
        enemy_attack_zone = enemy.get_attack_zone()
        #print("enemy anim state:", enemy.anim_state)
        if enemy.anim_state in ["windup", "attacking", "recovery"]:
            if enemy.done_attack == False:
                enemy.done_attack = True  # 攻擊完成標誌，在./entities/enemy update_animation recovery結束後重製
                
                print("An enemy is attacking!")
                print("enemy anim state:", enemy.anim_state)
                print("enemy attack zone:", enemy_attack_zone)
                if enemy.is_aoe:
                    targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
                    if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                        targets.append(our_tower)
                    for tar in targets:
                        if isinstance(tar, Cat):
                            c = tar
                            old_hp = c.hp
                            c.take_damage(enemy.atk)  # 使用 take_damage 生成煙霧
                            if c.hp > 0:
                                thresholds_crossed = int(old_hp / c.kb_threshold) - int(c.hp / c.kb_threshold)
                                if thresholds_crossed > 0:
                                    c.knock_back()
                            c.last_hp = c.hp
                            contact_rect = enemy_attack_zone.clip(c.get_rect())
                            contact_point = contact_rect.center
                            c.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                        elif isinstance(tar, Tower):
                            tower = tar
                            tower.hp -= enemy.atk
                            contact_rect = enemy_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                else:
                    if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                        tower = our_tower
                        tower.hp -= enemy.atk
                        contact_rect = enemy_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    else:
                        for cat in cats:
                            if enemy_attack_zone.colliderect(cat.get_rect()):
                                old_hp = cat.hp
                                cat.take_damage(enemy.atk)  # 使用 take_damage 生成煙霧
                                if cat.hp > 0:
                                    thresholds_crossed = int(old_hp / cat.kb_threshold) - int(cat.hp / cat.kb_threshold)
                                    if thresholds_crossed > 0:
                                        cat.knock_back()
                                cat.last_hp = cat.hp
                                contact_rect = cat_attack_zone.clip(cat.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                break
        # enemy.anim_state in idle or moving 
        elif enemy.is_aoe:
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                #print(enemy.is_boss)
                targets.append(our_tower)
                #print("enemy tower in attack zone")
            if targets and now - enemy.last_attack_time >= enemy.attack_interval:
                enemy.anim_state = "windup"
                enemy.anim_start_time = now
                enemy.last_attack_time = now
                enemy.is_attacking = True
            elif targets and now - enemy.last_attack_time < enemy.attack_interval:
                enemy.anim_state = "idle"
            elif not targets:
                enemy.move()
                #print("enemy moving")
        else:
            target_in_range = False
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                target_in_range = True
                if now - enemy.last_attack_time >= enemy.attack_interval:
                    enemy.anim_state = "windup"
                    enemy.anim_start_time = now
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
                else: # 在範圍內但攻擊間隔未過
                    enemy.anim_state = "idle"
            else:
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        target_in_range = True
                        # 檢查攻擊間隔是否已過
                        if now - enemy.last_attack_time >= enemy.attack_interval:
                            enemy.anim_state = "windup"
                            enemy.anim_start_time = now
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                        break
                
                if target_in_range == True and enemy.is_attacking == False: # 在範圍內但攻擊間隔未過
                    enemy.anim_state = "idle"

            
            if target_in_range == False:
                enemy.move()

    # 應用震波擊退效果，所有 Cat 向後退 200 像素，持續 2 秒
    for effect in shockwave_effects:
        if effect.update():
            for cat in cats:
                if not cat.is_attacking and not getattr(cat, 'has_retreated', False):  # 僅在未後退且非攻擊中時執行
                    cat.start_retreat(200)  # 啟動 2 秒後退 50 像素
                    cat.anim_start_time = pygame.time.get_ticks()  # 觸發 walking 動畫
        else:
            shockwave_effects.remove(effect)

    # Centralized soul creation for enemy deaths
    new_enemies = []
    for enemy in enemies:
        #print("enemy hp:", enemy.hp)
        if enemy.hp > 0:
            new_enemies.append(enemy)
        else:
            souls.append(Soul(enemy.x + enemy.width // 2, enemy.y))
            enemy_y_manager.release_y(enemy.slot_index)
    enemies[:] = new_enemies

    # Centralized soul creation for cat deaths
    new_cats = []
    for cat in cats:
        if cat.hp > 0:
            new_cats.append(cat)
        else:
            souls.append(Soul(cat.x + cat.width // 2, cat.y))
            cat_y_manager.release_y(cat.slot_index)
    cats[:] = new_cats

    if enemy_tower and enemy_tower.hp <= 0:
        enemy_tower.hp = 0
    if our_tower.hp <= 0:
        our_tower.hp = 0

    return shockwave_effects

