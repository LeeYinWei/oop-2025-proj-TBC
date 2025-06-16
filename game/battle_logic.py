from .entities import Enemy, Cat, Soul, Tower, ShockwaveEffect, YManager
import pygame

def update_battle(cats, enemies, our_tower, enemy_tower, now, souls, cat_y_manager, enemy_y_manager, shockwave_effects=None, current_budget=0):
    if shockwave_effects is None:
        shockwave_effects = []

    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
        cat.update_smoke_effects()
        cat.update_physic_effects()
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
        enemy.update_smoke_effects()
        enemy.update_physic_effects()
    our_tower.contact_points = []
    if enemy_tower:
        enemy_tower.contact_points = []
    # 更新塔樓的煙霧和物理特效
    our_tower.update_smoke_effects()
    our_tower.update_physic_effects()
    if enemy_tower:
        enemy_tower.update_smoke_effects()
        enemy_tower.update_physic_effects()

    # 檢查新生成的 boss，觸發出場震波
    for enemy in enemies:
        if enemy.is_boss and not getattr(enemy, 'has_spawn_shockwave', False):
            shockwave_x = enemy.x + enemy.width // 2
            shockwave_y = enemy.y + enemy.height // 2-150
            shockwave = ShockwaveEffect(shockwave_x, shockwave_y, duration=1000, scale=1.0)
            shockwave_effects.append(shockwave)
            enemy.has_spawn_shockwave = True  # 標記已觸發，避免重複
            #print(f"Boss {enemy} spawned with shockwave at ({shockwave_x}, {shockwave_y})")

    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.anim_state in ["windup", "attacking", "recovery"]:
            if not cat.done_attack:
                cat.done_attack = True
                #print(f"Cat attacking, anim_state: {cat.anim_state}, zone: {cat_attack_zone}")
                if cat.is_aoe:
                    targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        targets.append(enemy_tower)
                    for tar in targets:
                        if isinstance(tar, Enemy):
                            enemy = tar
                            old_hp = enemy.hp
                            enemy.take_damage(cat.atk, cat.attack_type)
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
                            tower.take_damage(cat.atk, cat.attack_type)
                            contact_rect = cat_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            cat.contact_points.append(contact_point)
                else:
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        tower = enemy_tower
                        tower.take_damage(cat.atk, cat.attack_type)
                        contact_rect = cat_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        cat.contact_points.append(contact_point)
                    else:
                        for enemy in enemies:
                            if cat_attack_zone.colliderect(enemy.get_rect()):
                                old_hp = enemy.hp
                                enemy.take_damage(cat.atk, cat.attack_type)
                                if enemy.hp > 0:
                                    thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                    if thresholds_crossed > 0:
                                        enemy.knock_back()
                                enemy.last_hp = enemy.hp
                                contact_rect = cat_attack_zone.clip(enemy.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                
        elif cat.is_aoe:
            targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                targets.append(enemy_tower)
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
            if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                target_in_range = True
                if now - cat.last_attack_time >= cat.attack_interval:
                    cat.anim_state = "windup"
                    cat.anim_start_time = now
                    cat.last_attack_time = now
                    cat.is_attacking = True
                else:
                    cat.anim_state = "idle"
            else:
                for enemy in enemies:
                    if cat_attack_zone.colliderect(enemy.get_rect()):
                        target_in_range = True
                        if now - cat.last_attack_time >= cat.attack_interval:
                            cat.anim_state = "windup"
                            cat.anim_start_time = now
                            cat.last_attack_time = now
                            cat.is_attacking = True
                        break
                if target_in_range and not cat.is_attacking:
                    cat.anim_state = "idle"
            if not target_in_range:
                cat.move()

    for enemy in enemies:
        enemy_attack_zone = enemy.get_attack_zone()
        if enemy.anim_state in ["windup", "attacking", "recovery"]:
            if not enemy.done_attack:
                enemy.done_attack = True
                #print(f"Enemy attacking, anim_state: {enemy.anim_state}, zone: {enemy_attack_zone}")
                if enemy.is_aoe:
                    targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
                    if enemy_attack_zone.colliderect(our_tower.get_rect()):
                        targets.append(our_tower)
                    for tar in targets:
                        if isinstance(tar, Cat):
                            c = tar
                            old_hp = c.hp
                            c.take_damage(enemy.atk, enemy.attack_type)
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
                            tower.take_damage(enemy.atk, enemy.attack_type)
                            contact_rect = enemy_attack_zone.clip(tower.get_rect())
                            contact_point = contact_rect.center
                            tower.contact_points.append(contact_point)
                            enemy.contact_points.append(contact_point)
                else:
                    if enemy_attack_zone.colliderect(our_tower.get_rect()):
                        tower = our_tower
                        tower.take_damage(enemy.atk, enemy.attack_type)
                        contact_rect = enemy_attack_zone.clip(tower.get_rect())
                        contact_point = contact_rect.center
                        tower.contact_points.append(contact_point)
                        enemy.contact_points.append(contact_point)
                    else:
                        for cat in cats:
                            if enemy_attack_zone.colliderect(cat.get_rect()):
                                old_hp = cat.hp
                                cat.take_damage(enemy.atk, enemy.attack_type)
                                if cat.hp > 0:
                                    thresholds_crossed = int(old_hp / cat.kb_threshold) - int(cat.hp / cat.kb_threshold)
                                    if thresholds_crossed > 0:
                                        cat.knock_back()
                                cat.last_hp = cat.hp
                                contact_rect = enemy_attack_zone.clip(cat.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
                                break
        elif enemy.is_aoe:
            targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            if targets and now - enemy.last_attack_time >= enemy.attack_interval:
                enemy.anim_state = "windup"
                enemy.anim_start_time = now
                enemy.last_attack_time = now
                enemy.is_attacking = True
            elif targets and now - enemy.last_attack_time < enemy.attack_interval:
                enemy.anim_state = "idle"
            elif not targets:
                enemy.move()
        else:
            target_in_range = False
            if enemy_attack_zone.colliderect(our_tower.get_rect()):
                target_in_range = True
                if now - enemy.last_attack_time >= enemy.attack_interval:
                    enemy.anim_state = "windup"
                    enemy.anim_start_time = now
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
                else:
                    enemy.anim_state = "idle"
            else:
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        target_in_range = True
                        if now - enemy.last_attack_time >= enemy.attack_interval:
                            enemy.anim_state = "windup"
                            enemy.anim_start_time = now
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                        break
                if target_in_range and not enemy.is_attacking:
                    enemy.anim_state = "idle"
            if not target_in_range:
                enemy.move()

    # Apply shockwave retreat effect (200 pixels back for 2 seconds)
    for effect in shockwave_effects[:]:
        if effect.update(now):
            for cat in cats:
                if not cat.is_attacking and not getattr(cat, 'has_retreated', False):
                    cat.start_retreat(50)
                    cat.anim_start_time = now
                    cat.has_retreated = True
        else:
            shockwave_effects.remove(effect)

    # Centralized soul creation for enemy deaths
    # 中央處理敵人死亡和獎勵
    new_enemies = []
    for enemy in enemies:
        if enemy.hp > 0:
            new_enemies.append(enemy)
        else:
            souls.append(Soul(enemy.x + enemy.width // 2, enemy.y))
            enemy_y_manager.release_y(enemy.slot_index)
            # 將敵人的獎勵加到 current_budget 中
            current_budget = current_budget+enemy.reward
            #print(f"Enemy defeated! Gained {enemy.reward} budget. Current budget: {current_budget}") # 可選：打印日誌
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