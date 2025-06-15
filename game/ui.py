# game/ui.py
import pygame
import os

from .entities import cat_types, cat_costs, cat_cooldowns

# 新增一個變數來儲存背景圖片
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
            # 確保圖片路徑正確
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _level_selection_background_image_path)
            
            image = pygame.image.load(image_path).convert() # 不需要 alpha 如果背景圖沒有透明度
            _level_selection_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading level selection background image: {e}")
            _level_selection_background_image = None # 載入失敗則設為 None
    return _level_selection_background_image

def draw_level_selection(screen, levels, selected_level, selected_cats, font, completed_levels):
    # 載入並縮放背景圖片 (只在第一次載入)
    background_image = load_level_selection_background_image(screen.get_width(), screen.get_height())
    if background_image:
        screen.blit(background_image, (0, 0))  # 畫在左上角起始點
    else:
        screen.fill((0, 0, 0)) # 如果圖片載入失敗，則填充黑色背景

    title = font.render("Select Level and Cats", True, (0, 0, 0))
    # 將標題文字設定為白色，因為黑色背景上黑色文字看不清
    # 如果你的背景圖顏色會讓黑色文字看不清，考慮改成白色或其他對比色
    screen.blit(title, (350, 50))
    cat_rects = {}

    for i, level in enumerate(levels):
        rect = pygame.Rect(50, 100 + i * 60, 200, 50)
        is_playable = i == 0 or (i - 1) in completed_levels
        color = (0, 255, 0) if i == selected_level and is_playable else (100, 200, 100) if is_playable else (180, 180, 180)
        pygame.draw.rect(screen, color, rect)
        level_text = font.render(level.name if is_playable else f"{level.name} (Locked)", True, (0, 0, 0))
        screen.blit(level_text, (rect.x + 5, rect.y + 15))

    for idx, cat_type in enumerate(cat_types.keys()): # 確保 cat_types 可用
        rect = pygame.Rect(300 + (idx % 5) * 120, 100 + (idx // 5) * 60, 100, 50)
        cat_rects[cat_type] = rect
        color = (0, 255, 0) if cat_type in selected_cats else (200, 200, 200)
        pygame.draw.rect(screen, color, rect)
        # 貓咪按鈕的文字顏色也建議用對比色，例如黑色背景的圖上用白色
        #print(f"Drawing cat button for {cat_type} at {rect.topleft}")  # Debugging line
        screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 15))
        cost = cat_costs.get(cat_type, 0)
        cost_text = font.render(f"Cost: {cost}", True, (0, 0, 0))
        screen.blit(cost_text, (rect.x + 5, rect.y + 30))

    # Reset Progress Button
    reset_rect = pygame.Rect(50, 400, 200, 50)
    pygame.draw.rect(screen, (255, 100, 100), reset_rect)
    reset_text = font.render("Reset Progress", True, (0, 0, 0))
    screen.blit(reset_text, (reset_rect.x + 40, reset_rect.y + 15))

    # Quit Button
    quit_rect = pygame.Rect(50, 470, 200, 50) # 定義離開按鈕的位置和大小
    pygame.draw.rect(screen, (200, 50, 50), quit_rect) # 紅色按鈕
    quit_text = font.render("Quit", True, (255, 255, 255)) # 白色文字
    screen.blit(quit_text, (quit_rect.x + 70, quit_rect.y + 15)) # 放置文字

    # Instructions text
    screen.blit(font.render("Click to select level, click to toggle cats, press Enter to start", True, (0, 0, 0)), (50, 540)) # 調整說明文字的Y座標，以免重疊

    return cat_rects, reset_rect, quit_rect # 返回 quit_rect

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

    # Dynamically adjust button positions with horizontal layout and row break at 5
    button_x_start = 300  # Starting x position
    button_y_start = 50  # Starting y position
    button_spacing_x = 120  # Horizontal spacing between buttons
    button_spacing_y = 70   # Vertical sliding between rows
    max_buttons_per_row = 5  # Maximum buttons per row

    # Recalculate button_rects based on selected_cats with row logic
    calculated_button_rects = {}
    for idx, cat_type in enumerate(selected_cats):
        row = idx // max_buttons_per_row
        col = idx % max_buttons_per_row
        rect_x = button_x_start + col * button_spacing_x
        rect_y = button_y_start + row * button_spacing_y
        rect = pygame.Rect(rect_x, rect_y, 100, 50)
        calculated_button_rects[cat_type] = rect

    # Draw cat buttons with cooldown progress bars, cost, and key mapping
    for idx, cat_type in enumerate(selected_cats):
        if cat_type in calculated_button_rects:
            rect = calculated_button_rects[cat_type]
            cost = cat_costs.get(cat_type, 0)
            color = (0, 255, 0) if current_budget >= cost else (200, 200, 200)
            
            # Draw cooldown progress bar logic
            cooldown = cat_cooldowns.get(cat_type, 0)
            time_since_last_spawn = current_time - last_spawn_time.get(cat_type, 0)
            if cooldown > 0 and time_since_last_spawn < cooldown:
                color = (150, 150, 150)  # Gray out button during cooldown
            
            pygame.draw.rect(screen, color, rect)
            screen.blit(font.render(cat_type, True, (0, 0, 0)), (rect.x + 5, rect.y + 2))

            # Display cost below the button name
            cost_text = font.render(f"Cost: {cost}", True, (0, 0, 0))
            screen.blit(cost_text, (rect.x + 5, rect.y + 17))

            # Find and display the corresponding key
            key = next((k for k, v in cat_key_map.items() if v == cat_type), None)
            key_text = font.render(f"Key: {pygame.key.name(key) if key else 'N/A'}", True, (0, 0, 0)) if key else font.render("Key: N/A", True, (0, 0, 0))
            screen.blit(key_text, (rect.x + 5, rect.y + 32))

            # Draw cooldown progress bar
            if cooldown > 0 and time_since_last_spawn < cooldown:
                cooldown_remaining = max(0, cooldown - time_since_last_spawn)
                cooldown_percentage = cooldown_remaining / cooldown
                bar_height = 10
                bar_width = rect.width
                bar_x = rect.x
                bar_y = rect.y + rect.height + 20  # Adjusted to avoid overlap with cost and key text
                # Draw gray background for the bar
                pygame.draw.rect(screen, (150, 150, 150), (bar_x, bar_y, bar_width, bar_height))
                # Draw red fill from left to right
                fill_width = int(bar_width * cooldown_percentage)
                pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, fill_width, bar_height))
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


# 新增一個變數來儲存背景圖片
# 建議在 ui.py 的頂部或適當位置加載一次圖片，避免每幀重複加載
_intro_background_image = None
_intro_background_image_path = "background/background_intro.jpg" # <--- 設定你的背景圖片路徑

def load_intro_background_image(screen_width, screen_height):
    """
    載入並縮放開場背景圖片。
    這個函數應該只被調用一次。
    """
    global _intro_background_image
    if _intro_background_image is None:
        try:
            # 確保圖片路徑正確，相對於遊戲運行時的根目錄
            # 假設 'background' 資料夾與 'game' 資料夾位於同一層級
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            image_path = os.path.join(base_dir, _intro_background_image_path)
            
            # --- DEBUGGING LINE ---
            print(f"Attempting to load intro image from: {image_path}") 

            image = pygame.image.load(image_path).convert_alpha() # 使用 convert_alpha 處理透明度
            _intro_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except pygame.error as e:
            print(f"Error loading intro background image: {e}")
            _intro_background_image = None # 載入失敗則設為 None
        except FileNotFoundError: # 針對檔案找不到的錯誤
            print(f"Intro background image file not found: {image_path}")
            _intro_background_image = None
    return _intro_background_image

# (你的 wrap_text 函數保持不變)
def wrap_text(text, font, max_width):
    """
    將一段文字按指定的最大寬度進行自動換行。
    ... (你的 wrap_text 函數代碼)
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
    # --- START OF MISSING BACKGROUND DRAWING LOGIC ---
    # 載入背景圖片 (如果尚未載入)
    background_image = load_intro_background_image(screen.get_width(), screen.get_height())

    # 繪製背景圖片 (如果存在)
    if background_image:
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        temp_surface.blit(background_image, (0, 0))
        temp_surface.set_alpha(fade_alpha) # 設定背景圖片的透明度
        screen.blit(temp_surface, (0, 0))
    else:
        # 如果圖片載入失敗，則保持黑色背景
        screen.fill((0, 0, 0))
        print("Warning: Intro background image not loaded or found, using black background.")
    # --- END OF MISSING BACKGROUND DRAWING LOGIC ---


    # Load story from file
    story_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "background", "backgroundStory.txt")
    story_lines = [] # 為了避免衝突，將其初始化為空列表
    raw_story_content = "" # 確保有預設值

    if os.path.exists(story_file):
        try:
            with open(story_file, "r", encoding="utf-8") as f:
                raw_story_content = f.read() # 讀取整個文件內容，而不是按行讀取
        except Exception as e:
            print(f"Error reading story file {story_file}: {e}")
            raw_story_content = "Error loading story. Default story: Cats fight invaders!"
    else:
        raw_story_content = "No story file found. Default story: Cats fight invaders!"


    # Create a surface for the story with custom font size
    line_height = 40  # Increased to 40 pixels per line for larger text
    larger_font = pygame.font.SysFont(None, 36)  # Increased font size to 36

    # --- START MODIFICATION for story text wrapping ---
    # 定義故事文字的最大顯示寬度
    # 例如，你希望它佔據螢幕的 80% 寬度並居中
    story_max_width = int(screen.get_width() * 0.8)
    
    # 處理所有故事文字的換行
    wrapped_story_lines = []
    # 如果原始文件是多段落，你可能需要按段落分割再換行
    paragraphs = raw_story_content.split('\n') # 按換行符號分割段落
    for paragraph in paragraphs:
        if paragraph.strip(): # 處理空行
            wrapped_story_lines.extend(wrap_text(paragraph.strip(), larger_font, story_max_width))
            wrapped_story_lines.append("") # 每段之間增加一個空行
    if wrapped_story_lines and wrapped_story_lines[-1] == "":
        wrapped_story_lines.pop() # 移除最後多餘的空行

    story_surface_height = len(wrapped_story_lines) * line_height + 20 # 根據換行後的行數調整高度
    story_surface = pygame.Surface((screen.get_width(), story_surface_height), pygame.SRCALPHA)
    story_surface.fill((0, 0, 0, 0))  # Transparent background

    # Render and center story lines with larger font
    for i, line in enumerate(wrapped_story_lines):
        text = larger_font.render(line, True, (255, 255, 255))
        # Center horizontally based on the story_max_width for the entire block
        text_x = (screen.get_width() - story_max_width) // 2 + (story_max_width - text.get_width()) // 2
        text_y = i * line_height  # Vertical position
        story_surface.blit(text, (text_x, text_y))
    # --- END MODIFICATION for story text wrapping ---

    # Blit the story surface with sliding effect
    screen.blit(story_surface, (0, y_offset))

    # Draw Skip button with larger font
    skip_rect = pygame.Rect(1100, 50, 100, 50)
    pygame.draw.rect(screen, (255, 100, 100), skip_rect) # Reddish button
    skip_text = larger_font.render("Skip", True, (0, 0, 0)) # Black text
    
    # Center "Skip" text on the button
    skip_text_rect = skip_text.get_rect(center=skip_rect.center)
    screen.blit(skip_text, skip_text_rect)

    return skip_rect