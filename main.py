import asyncio
import pygame, sys
from game.game_loop import main_game_loop

async def main():
    pygame.init()
    pygame.display.set_caption("The snail adventure")
    screen = pygame.display.set_mode((1280, 600))
    clock = pygame.time.Clock()
    await main_game_loop(screen, clock)
    # 避免直接退出，瀏覽器環境由 pygbag 管理
    # pygame.quit() 在這裡可以註解掉

if __name__ == "__main__":
    if sys.platform == "emscripten":  # 檢測是否在瀏覽器環境
        asyncio.ensure_future(main())
    else:
        asyncio.run(main())