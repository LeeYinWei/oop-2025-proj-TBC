# game/ui.py (部分修改)
import pygame
import os

from .entities import cat_types, cat_costs, cat_cooldowns
from game.entities.csmokeeffect import CSmokeEffect
from game.entities.tower import Tower
# =============================================================================================================
# 新增一個變數來儲存背景圖片
_intro_background_image = None
_intro_background_image_path = "background/background_intro.jpg"

def load_intro_background_image(screen_width, screen_height):
    """
    載入並縮放開場背景圖片。
    這個函數應該只被調用一次。
    """
    global _intro_background_image
    if _intro_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _intro_background_image_path)
            print(f"Attempting to load intro image from: {image_path}")
            image = pygame.image.load(image_path).convert_alpha()
            _intro_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading intro background image: {e}")
            _intro_background_image = None
        except FileNotFoundError:
            print(f"Intro background image file not found: {image_path}")
            _intro_background_image = None
    return _intro_background_image

# (wrap_text 函數保持不變)
def wrap_text(text, font, max_width):
    """
    將一段文字按指定的最大寬度進行自動換行。
    """
    words = text.split(' ')
    lines = []
    current_line = []
    current_line_width = 0

    for word in words:
        test_line = " ".join(current_line + [word])
        test_width, _ = font.size(test_line)

        if test_width <= max_width:
            current_line.append(word)
            current_line_width = test_width
        else:
            if current_line:
                lines.append(" ".join(current_line))
            word_width, _ = font.size(word)
            if word_width > max_width:
                lines.append(word)
                current_line = []
                current_line_width = 0
            else:
                current_line = [word]
                current_line_width = word_width
    
    if current_line:
        lines.append(" ".join(current_line))
    
    return lines

def draw_intro_screen(screen, font, y_offset, fade_alpha):
    background_image = load_intro_background_image(screen.get_width(), screen.get_height())

    if background_image:
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        temp_surface.blit(background_image, (0, 0))
        temp_surface.set_alpha(fade_alpha)
        screen.blit(temp_surface, (0, 0))
    else:
        screen.fill((0, 0, 0))
        print("Warning: Intro background image not loaded or found, using black background.")

    story_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "background", "backgroundStory.txt")
    raw_story_content = ""
    if os.path.exists(story_file):
        try:
            with open(story_file, "r", encoding="utf-8") as f:
                raw_story_content = f.read()
        except Exception as e:
            print(f"Error reading story file {story_file}: {e}")
            raw_story_content = "Error loading story. Default story: Cats fight invaders!"
    else:
        raw_story_content = "No story file found. Default story: Cats fight invaders!"

    line_height = 40
    larger_font = pygame.font.SysFont(None, 36)
    story_max_width = int(screen.get_width() * 0.8)
    paragraphs = raw_story_content.split('\n')
    wrapped_story_lines = []
    for paragraph in paragraphs:
        if paragraph.strip():
            wrapped_story_lines.extend(wrap_text(paragraph.strip(), larger_font, story_max_width))
            wrapped_story_lines.append("")
    if wrapped_story_lines and wrapped_story_lines[-1] == "":
        wrapped_story_lines.pop()

    story_surface_height = len(wrapped_story_lines) * line_height + 20
    story_surface = pygame.Surface((screen.get_width(), story_surface_height), pygame.SRCALPHA)
    story_surface.fill((0, 0, 0, 0))

    for i, line in enumerate(wrapped_story_lines):
        text = larger_font.render(line, True, (255, 255, 255))
        text_x = (screen.get_width() - story_max_width) // 2 + (story_max_width - text.get_width()) // 2
        text_y = i * line_height
        story_surface.blit(text, (text_x, text_y))

    screen.blit(story_surface, (0, y_offset))

    skip_rect = pygame.Rect(1100, 50, 100, 50)
    pygame.draw.rect(screen, (255, 100, 100), skip_rect)
    skip_text = larger_font.render("Skip", True, (0, 0, 0))
    skip_text_rect = skip_text.get_rect(center=skip_rect.center)
    screen.blit(skip_text, skip_text_rect)

    return skip_rect
# =============================================================================================================
_level_selection_background_image = None
_level_selection_background_image_path = "background/level_selection_bg.png"

def load_level_selection_background_image(screen_width, screen_height):
    """
    載入並縮放關卡選擇背景圖片。
    這個函數應該只被調用一次。
    """
    global _level_selection_background_image
    if _level_selection_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _level_selection_background_image_path)
            image = pygame.image.load(image_path).convert()
            _level_selection_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading level selection background image: {e}")
            _level_selection_background_image = None
    return _level_selection_background_image

def draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels):
    background_image = load_level_selection_background_image(screen.get_width(), screen.get_height())
    if background_image:
        screen.blit(background_image, (0, 0))
    else:
        screen.fill((0, 0, 0))

    title = font.render("Select Level and Cats", True, (255, 255, 255))
    screen.blit(title, (350, 50))
    cat_rects = {}

    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (0, 255, 0) if i == selected_level and is_playable else (100, 200, 100) if is_playable else (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (255, 255, 255))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))

    for idx, cat_type in enumerate(cat_types.keys()):
        rect = pygame.Rect(300 + (idx % 5) * 120, 100 + (idx // 5) * 60, 100, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        screen.blit(font.render(cat_type, True, (255, 255, 255)), (rect.x + 5, rect.y + 15))
        cost = cat_costs.get(cat_type, 0)
        cost_text = font.render(f"Cost: {cost}", True, (255, 255, 255))
        screen.blit(cost_text, (rect.x + 5, rect.y + 30))

    reset_rect = pygame.Rect(50, 400, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect)
    reset_text = font.render("Reset Progress", True, (255, 255, 255))
    screen.blit(reset_text, (reset_rect.x + 40, reset_rect.y + 15))

    quit_rect = pygame.Rect(50, 470, 200, 50)
    pygame.draw.rect(screen, (200, 50, 50), quit_rect)
    quit_text = font.render("Quit", True, (255, 255, 255))
    screen.blit(quit_text, (quit_rect.x + 70, quit_rect.y + 15))

    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (255, 255, 255)), (50, 540))

    return cat_rects, reset_rect, quit_rect
# =============================================================================================================
def draw_game_ui(screen, current_level, current_budget, enemy_tower, current_time, level_start_time, selected_cats, last_spawn_time, button_rects, font, cat_key_map):
    background_color = (200, 255, 200)
    screen.fill(background_color)
    screen.blit(current_level.background, (0, 0))
    
    # Draw towers, cats, enemies, etc. (assuming this exists in your original code)
    # ... (rest of your existing draw_game_ui logic for towers, cats, enemies)

    budget_text = font.render(f"Budget: {current_budget}", True, (0, 0, 0))
    screen.blit(budget_text, (50, 10))

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
        rect = pygame.Rect(rect_x, rect_y, 100, 50)
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

    return pause_rect
# =============================================================================================================
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
# =============================================================================================================
_mission_complete_background_image = None
_mission_complete_background_image_path = "background/mission_complete_bg.jpg"

def load_mission_complete_background_image(screen_width, screen_height):
    """
    載入並縮放首通背景圖片。
    這個函數應該只被調用一次。
    """
    global _mission_complete_background_image
    if _mission_complete_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _mission_complete_background_image_path)
            image = pygame.image.load(image_path).convert_alpha()
            _mission_complete_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading mission complete background image: {e}")
            _mission_complete_background_image = None
    return _mission_complete_background_image
# =============================================================================================================
_ending_background_image = None
_ending_background_image_path = "background/1a901572-aa72-4382-b64f-b0d60c1b9cc3.jpg"

def load_ending_background_image(screen_width, screen_height):
    """
    載入並縮放結尾背景圖片。
    這個函數應該只被調用一次。
    """
    global _ending_background_image
    if _ending_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _ending_background_image_path)
            image = pygame.image.load(image_path).convert_alpha()
            _ending_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading ending background image: {e}")
            _ending_background_image = None
    return _ending_background_image



def draw_end_screen(screen, current_level, status, end_font, font, our_tower, enemy_tower, start_time):
    # 背景
    screen.blit(current_level.background, (0, 0))

    # 時間差，用於動畫進度（最大1秒內完成）
    elapsed = pygame.time.get_ticks() - start_time
    scale_progress = min(1.0, elapsed / 1500.0)  # 0~1 之間

    # 動畫縮放參數
    base_font_size = 40
    max_font_size = 120
    animated_font_size = int(base_font_size + (max_font_size - base_font_size) * scale_progress)

    # 建立縮放字體物件
    animated_font = pygame.font.SysFont("Arial", animated_font_size)

    if status == "victory":
        enemy_tower.draw_collapse(screen)
        text_surface = animated_font.render("Victory!", True, (0, 255, 100))
        text_rect = text_surface.get_rect(center=(640, 300))  # 螢幕中央
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            screen.blit(font.render("Press Enter to continue", True, (0, 0, 0)), (460, 400))

    elif status == "lose":
        our_tower.draw_collapse(screen)
        text_surface = animated_font.render("Defeat!", True, (255, 100, 100))
        text_rect = text_surface.get_rect(center=(640, 300))
        screen.blit(text_surface, text_rect)
        if scale_progress == 1.0:
            screen.blit(font.render("Press any key to return to level selection", True, (0, 0, 0)), (460, 400))

# =============================================================================================================
def draw_ending_animation(screen, font, y_offset, fade_alpha):
    """
    繪製遊戲結尾動畫，包含淡入和文字滾動效果。
    """
    background_image = load_ending_background_image(screen.get_width(), screen.get_height())

    if background_image:
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        temp_surface.blit(background_image, (0, 0))
        temp_surface.set_alpha(fade_alpha)
        screen.blit(temp_surface, (0, 0))
    else:
        screen.fill((0, 0, 0))
        print("Warning: Ending background image not loaded or found, using black background.")

    # Load ending story from file
    story_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "background", "mission_complete_story.txt")
    raw_story_content = ""
    if os.path.exists(story_file):
        try:
            with open(story_file, "r", encoding="utf-8") as f:
                raw_story_content = f.read()
        except Exception as e:
            print(f"Error reading ending story file {story_file}: {e}")
            raw_story_content = "Thank you for playing! The cats celebrate their eternal victory!"
    else:
        raw_story_content = "Thank you for playing! The cats celebrate their eternal victory!"

    line_height = 40
    larger_font = pygame.font.SysFont(None, 36)
    story_max_width = int(screen.get_width() * 0.8)
    paragraphs = raw_story_content.split('\n')
    wrapped_story_lines = []
    for paragraph in paragraphs:
        if paragraph.strip():
            wrapped_story_lines.extend(wrap_text(paragraph.strip(), larger_font, story_max_width))
            wrapped_story_lines.append("")
    if wrapped_story_lines and wrapped_story_lines[-1] == "":
        wrapped_story_lines.pop()

    story_surface_height = len(wrapped_story_lines) * line_height + 20
    story_surface = pygame.Surface((screen.get_width(), story_surface_height), pygame.SRCALPHA)
    story_surface.fill((0, 0, 0, 0))

    for i, line in enumerate(wrapped_story_lines):
        text = larger_font.render(line, True, (255, 255, 255))
        text_x = (screen.get_width() - story_max_width) // 2 + (story_max_width - text.get_width()) // 2
        text_y = i * line_height
        story_surface.blit(text, (text_x, text_y))

    screen.blit(story_surface, (0, y_offset))

    skip_rect = pygame.Rect(1100, 50, 100, 50)
    pygame.draw.rect(screen, (255, 100, 100), skip_rect)
    skip_text = larger_font.render("Skip", True, (0, 0, 0))
    skip_text_rect = skip_text.get_rect(center=skip_rect.center)
    screen.blit(skip_text, skip_text_rect)

    return skip_rect