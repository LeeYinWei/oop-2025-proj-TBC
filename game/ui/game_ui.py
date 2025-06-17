import pygame

from ..entities import cat_types, cat_costs, cat_cooldowns

import pygame

from ..entities import cat_types, cat_costs, cat_cooldowns

def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map, budget_font):
    background_color = (200, 255, 200)
    screen.fill(background_color)
    screen.blit(current_level.background, (0, 0))
    
    # Draw towers, cats, enemies, etc. (assuming this exists in your original code)
    # ... (rest of your existing draw_game_ui logic for towers, cats, enemies)

    budget_text = budget_font.render(f"Budget: {current_budget}", True, (0, 0, 0))
    screen.blit(budget_text, (1080, 10))

    pause_rect = pygame.Rect(1100, 50, 150, 50)
    pygame.draw.rect(screen, (100, 100, 255), pause_rect)
    pause_text = font.render("Pause", True, (0, 0, 0))
    screen.blit(pause_text, (pause_rect.x + 50, pause_rect.y + 15))

    button_x_start = 300
    button_y_start = 50
    button_spacing_x = 120
    button_spacing_y = 70
    max_buttons_per_row = 5

    calculated_button_rects = {}
    for idx, cat_type in enumerate(selected_cats):
        row = idx // max_buttons_per_row
        col = idx % max_buttons_per_row
        rect_x = button_x_start + col * button_spacing_x
        rect_y = button_y_start + row * button_spacing_y
        rect = pygame.Rect(rect_x, rect_y, 100, 60)
        calculated_button_rects[cat_type] = rect

    for idx, cat_type in enumerate(selected_cats):
        if cat_type in calculated_button_rects:
            rect = calculated_button_rects[cat_type]
            cost = cat_costs.get(cat_type, 0)
            color = (0, 255, 0) if current_budget >= cost else (200, 200, 200)
            
            cooldown = cat_cooldowns.get(cat_type, 0)
            time_since_last_spawn = current_time - last_spawn_time.get(cat_type, 0)
            if cooldown > 0 and time_since_last_spawn < cooldown:
                color = (150, 150, 150)
            
            pygame.draw.rect(screen, color, rect)
            screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 5))
            cost_text = font.render(f"Cost: {cost}", True, (0, 0, 0))
            screen.blit(cost_text, (rect.x + 5, rect.y + 20))
            key = next((k for k, v in cat_key_map.items() if v == cat_type), None)
            key_text = font.render(f"Key: {pygame.key.name(key) if key else 'N/A'}", True, (0, 0, 0)) if key else font.render("Key: N/A", True, (0, 0, 0))
            screen.blit(key_text, (rect.x + 5, rect.y + 35))

            if cooldown > 0 and time_since_last_spawn < cooldown:
                cooldown_remaining = max(0, cooldown - time_since_last_spawn)
                cooldown_percentage = cooldown_remaining / cooldown
                bar_height = 10
                bar_width = rect.width
                bar_x = rect.x
                bar_y = rect.y + rect.height + 5
                pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height))
                fill_width = int(bar_width * cooldown_percentage)
                pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
                pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)

    # 更新 button_rects 參數以與 calculated_button_rects 同步
    button_rects.clear()
    button_rects.update(calculated_button_rects)

    return pause_rect, calculated_button_rects  # 返回 pause_rect 和 calculated_button_rects