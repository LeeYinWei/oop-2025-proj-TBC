import pygame
import os

_ending_background_image = None
_ending_background_image_path = "images/background/1a901572-aa72-4382-b64f-b0d60c1b9cc3.jpg"

def load_ending_background_image(screen_width, screen_height):
    """
    載入並縮放結尾背景圖片。
    這個函數應該只被調用一次。
    """
    global _ending_background_image
    if _ending_background_image is None:
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            image_path = os.path.join(base_dir, _ending_background_image_path)
            image = pygame.image.load(image_path).convert_alpha()
            _ending_background_image = pygame.transform.scale(image, (screen_width, screen_height))
        except (pygame.error, FileNotFoundError) as e:
            print(f"Error loading ending background image: {e}")
            _ending_background_image = None
    return _ending_background_image

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
    story_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "images/background", "mission_complete_story.txt")
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