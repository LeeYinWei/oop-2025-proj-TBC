import pygame

def draw_pause_menu(screen, font, current_level):
    screen.blit(current_level.background, (0, 0))
    # 新增一層透明的遮罩
    overlay = pygame.Surface(screen.get_size(), pygame.SRCALPHA)  # 建立與螢幕同大小的透明 surface
    overlay.fill((50, 50, 50, 100))  # RGBA：深藍色、透明度約 100/255
    screen.blit(overlay, (0, 0))  # 疊加上去
    background_color = (100, 100, 100, 240)
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