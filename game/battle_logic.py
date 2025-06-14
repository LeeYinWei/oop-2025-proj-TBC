from .entities import Enemy, Cat, Soul, Tower

def update_battle(cats, enemies, our_tower, enemy_tower, now, souls):
    for cat in cats:
        cat.is_attacking = False
        cat.contact_points = []
    for enemy in enemies:
        enemy.is_attacking = False
        enemy.contact_points = []
    our_tower.contact_points = []
    if enemy_tower:
        enemy_tower.contact_points = []

    for cat in cats:
        cat_attack_zone = cat.get_attack_zone()
        if cat.anim_state in ["windup", "attacking", "recovery"]:
            if cat.done_attack == False and now - cat.anim_start_time >= cat.frame_durations["windup"] * len(cat.anim_frames["windup"]):
                # Windup phase is done -> attack
                cat.done_attack = True# 攻擊完成標誌，在./entities/cat update_animation recovery結束後重製
                if cat.is_aoe:
                    targets = [e for e in enemies if cat_attack_zone.colliderect(e.get_rect())]
                    if enemy_tower and cat_attack_zone.colliderect(enemy_tower.get_rect()):
                        targets.append(enemy_tower)
                    for tar in targets:
                        if isinstance(tar, Enemy):
                            e = tar
                            old_hp = e.hp
                            e.hp -= cat.atk
                            if e.hp > 0:
                                thresholds_crossed = int(old_hp / e.kb_threshold) - int(e.hp / e.kb_threshold)
                                if thresholds_crossed > 0:
                                    e.knock_back()
                            e.last_hp = e.hp
                            contact_rect = cat_attack_zone.clip(e.get_rect())
                            contact_point = contact_rect.center
                            e.contact_points.append(contact_point)
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
                        for enemy in enemies:
                            if cat_attack_zone.colliderect(enemy.get_rect()):
                                old_hp = enemy.hp
                                enemy.hp -= cat.atk
                                if enemy.hp > 0:
                                    thresholds_crossed = int(old_hp / enemy.kb_threshold) - int(enemy.hp / enemy.kb_threshold)
                                    if thresholds_crossed > 0:
                                        enemy.knock_back()
                                enemy.last_hp = enemy.hp
                                contact_rect = cat_attack_zone.clip(enemy.get_rect())
                                contact_point = contact_rect.center
                                cat.contact_points.append(contact_point)
                                enemy.contact_points.append(contact_point)
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
        if enemy.anim_state in ["windup", "attacking", "recovery"]:
            if enemy.anim_state == "attacking" and now - enemy.last_attack_time >= enemy.frame_durations["attacking"] * len(enemy.anim_frames["attacking"]):
                enemy.last_attack_time = now
                if enemy.is_aoe:
                    targets = [c for c in cats if enemy_attack_zone.colliderect(c.get_rect())]
                    if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                        targets.append(our_tower)
                    for tar in targets:
                        if isinstance(tar, Cat):
                            c = tar
                            old_hp = c.hp
                            c.hp -= enemy.atk
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
                                cat.hp -= enemy.atk
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
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                targets.append(our_tower)
            if targets and now - enemy.last_attack_time >= enemy.attack_interval:
                enemy.anim_state = "windup"
                enemy.anim_start_time = now
                enemy.last_attack_time = now
                enemy.is_attacking = True
            elif not targets:
                enemy.move()
        else:
            if not enemy.is_boss and enemy_attack_zone.colliderect(our_tower.get_rect()):
                if now - enemy.last_attack_time >= enemy.attack_interval:
                    enemy.anim_state = "windup"
                    enemy.anim_start_time = now
                    enemy.last_attack_time = now
                    enemy.is_attacking = True
            else:
                for cat in cats:
                    if enemy_attack_zone.colliderect(cat.get_rect()):
                        if now - enemy.last_attack_time >= enemy.attack_interval:
                            enemy.anim_state = "windup"
                            enemy.anim_start_time = now
                            enemy.last_attack_time = now
                            enemy.is_attacking = True
                        break
                else:
                    enemy.move()

    # Centralized soul creation for enemy deaths
    new_enemies = []
    for enemy in enemies:
        if enemy.hp > 0:
            new_enemies.append(enemy)
        else:
            souls.append(Soul(enemy.x + enemy.width // 2, enemy.y))
            # Optional debug: print(f"Soul created for enemy at ({enemy.x}, {enemy.y})")
    enemies[:] = new_enemies

    # Centralized soul creation for cat deaths
    new_cats = []
    for cat in cats:
        if cat.hp > 0:
            new_cats.append(cat)
        else:
            souls.append(Soul(cat.x + cat.width // 2, cat.y))
            # Optional debug: print(f"Soul created for cat at ({cat.x}, {cat.y})")
    cats[:] = new_cats

    if enemy_tower and enemy_tower.hp <= 0:
        enemy_tower.hp = 0
    if our_tower.hp <= 0:
        our_tower.hp = 0
        