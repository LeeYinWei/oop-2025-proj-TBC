import asyncio
import platform
import pygame
from game.game_loop import main_game_loop

# 初始化 pygame
pygame.init()
screen = pygame.display.set_mode((1280, 600))  # 更新寬度為 1280
pygame.display.set_caption("Battle Cats: Attack Range")
clock = pygame.time.Clock()

async def main():
    await main_game_loop(screen, clock)

if __name__ == "__main__":
    if platform.system() == "Emscripten":
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())