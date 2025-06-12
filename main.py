# main.py
import asyncio
import pygame
from game.game_loop import main_game_loop

async def main():
    pygame.init()
    screen = pygame.display.set_mode((1280, 600))
    clock = pygame.time.Clock()
    await main_game_loop(screen, clock)
    pygame.quit()

if __name__ == "__main__":
    asyncio.run(main())