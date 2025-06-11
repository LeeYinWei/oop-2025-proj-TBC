import pygame
from .entities import cat_types, cat_costs, cat_cooldowns

def draw_level_selection(screen, levels, selected_level, selected_cats, font):
    background_color = (200, 255, 200)
    screen.fill(background_color)
    title = font.render("Select Level and Cats", True, (0, 0, 0))
    screen.blit(title, (350, 50))
    cat_rects = {}
    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        color = (0, 255, 0) if i == selected_level else (100, 200, 100)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name, True, (0, 0, 0))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))
    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(300 + idx * 150, 100, 100, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 15))
    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (0, 0, 0)), (50, 400))
    return cat_rects

def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map):
    screen.blit(current_level.background, (0, 0))
    budget_text = font.render(f"Money: {current_budget}", True, (0, 0, 0))
    screen.blit(budget_text, (800, 10))
    if enemy_tower:
        tower_hp_percent = (enemy_tower.hp / enemy_tower.max_hp) * 100
        hp_text = font.render(f"Enemy Tower HP: {tower_hp_percent:.2f}%", True, (0, 0, 0))
        screen.blit(hp_text, (800, 50))
    if current_level.survival_time > 0:
        elapsed_time = (current_time - level_start_time) / 1000
        time_text = font.render(f"Time: {elapsed_time:.1f}s", True, (0, 0, 0))
        screen.blit(time_text, (800, 30))
    button_colors = {"normal": (100, 200, 100), "cooldown": (180, 180, 180)}
    for cat_id, rect in button_rects.items():
        time_since = current_time - last_spawn_time[cat_id]
        cooldown = cat_cooldowns[cat_id]
        is_ready = time_since >= cooldown
        color = button_colors["normal"] if is_ready else button_colors["cooldown"]
        pygame.draw.rect(screen, color, rect)
        name_label = font.render(f"{cat_id} ({pygame.key.name(list(cat_key_map.keys())[list(cat_key_map.values()).index(cat_id)])})", True, (0, 0, 0))
        cost_label = font.render(f"Cost: ${cat_costs[cat_id]}", True, (255, 50, 50))
        screen.blit(name_label, (rect.x + 10, rect.y + 5))
        screen.blit(cost_label, (rect.x + 10, rect.y + 25))
        if not is_ready:
            ratio = time_since / cooldown
            bar_width = rect.width * ratio
            pygame.draw.rect(screen, (50, 255, 50), (rect.x, rect.y + rect.height - 5, bar_width, 5))
    screen.blit(font.render(f"Level: {current_level.name}", True, (0, 0, 0)), (10, 10))

def draw_end_screen(screen, current_level, status, end_font, font):
    screen.blit(current_level.background, (0, 0))
    if status == "victory":
        text = end_font.render("Victory!", True, (0, 255, 100))
    else:
        text = end_font.render("Defeat!", True, (255, 100, 100))
    screen.blit(text, (350, 250))
    screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (350, 350))