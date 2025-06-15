import pygame
from .entities import cat_types, cat_costs, cat_cooldowns

def draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels):
    background_color = (200, 255, 200)
    screen.fill(background_color)
    title = font.render("Select Level and Cats", True, (0, 0, 0))
    screen.blit(title, (350, 50))
    cat_rects = {}
    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (0, 255, 0) if i == selected_level and is_playable else (100, 200, 100) if is_playable else (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (0, 0, 0))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))
    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(300 + (idx % 5)  * 120, 100 + (idx // 5) * 60, 100, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 15))
    reset_rect = pygame.Rect(50, 400, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect)
    reset_text = font.render("Reset Progress", True, (0, 0, 0))
    screen.blit(reset_text, (reset_rect.x + 40, reset_rect.y + 15))
    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (0, 0, 0)), (50, 460))
    return cat_rects, reset_rect

def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map):
    background_color = (200, 255, 200)
    screen.fill(background_color)
    screen.blit(current_level.background, (0, 0))
    
    # Draw towers, cats, enemies, etc. (assuming this exists in your original code)
    # ... (rest of your existing draw_game_ui logic for towers, cats, enemies)

    # Draw pause button
    pause_rect = pygame.Rect(1100, 50, 150, 50)
    pygame.draw.rect(screen, (100, 100, 255), pause_rect)
    pause_text = font.render("Pause", True, (0, 0, 0))
    screen.blit(pause_text, (pause_rect.x + 50, pause_rect.y + 15))

    # Draw cat buttons with cooldown progress bars
    for idx, cat_type in enumerate(selected_cats):
        if cat_type in button_rects:
            rect = button_rects[cat_type]
            color = (0, 255, 0) if current_budget >= cat_costs.get(cat_type, 0) else (200, 200, 200)
            pygame.draw.rect(screen, color, rect)
            screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 15))

            # Draw cooldown progress bar (Battle Cats style: right to left)
            cooldown = cat_cooldowns.get(cat_type, 0)
            time_since_last_spawn = current_time - last_spawn_time.get(cat_type, 0)
            if cooldown > 0 and time_since_last_spawn < cooldown:
                cooldown_remaining = max(0, cooldown - time_since_last_spawn)
                cooldown_percentage = cooldown_remaining / cooldown
                bar_height = 10
                bar_width = rect.width
                bar_x = rect.x
                bar_y = rect.y + rect.height + 2  # Place bar just below the button
                # Draw gray background for the bar
                pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height))
                # Draw red fill from right to left
                fill_width = int(bar_width * cooldown_percentage)
                pygame.draw.rect(screen, (255, 0, 0), (bar_x + bar_width - fill_width, bar_y, fill_width, bar_height))
                # Optional: Add a black outline
                pygame.draw.rect(screen, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)

    return pause_rect

def draw_pause_menu(screen, font):
    background_color = (100, 100, 100, 200)
    pause_surface = pygame.Surface((400, 200), pygame.SRCALPHA)
    pause_surface.fill(background_color)
    screen.blit(pause_surface, (440, 200))
    end_rect = pygame.Rect(500, 250, 200, 50)
    continue_rect = pygame.Rect(500, 320, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), end_rect)
    pygame.draw.rect(screen, (100, 255, 100), continue_rect)
    end_text = font.render("End Battle", True, (0, 0, 0))
    continue_text = font.render("Continue", True, (0, 0, 0))
    screen.blit(end_text, (end_rect.x + 50, end_rect.y + 15))
    screen.blit(continue_text, (continue_rect.x + 50, continue_rect.y + 15))
    return end_rect, continue_rect

def draw_end_screen(screen, current_level, status, end_font, font):
    screen.blit(current_level.background, (0, 0))
    if status == "victory":
        text = end_font.render("Victory!", True, (0, 255, 100))
    else:
        text = end_font.render("Defeat!", True, (255, 100, 100))
    screen.blit(text, (350, 250))
    screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (350, 350))

