from game.entities.common import Common
from game.entities.shockwaveeffect import ShockwaveEffect
from game.entities.soul import Soul
import pygame

class Enemy(Common):
    def __init__(self, x, y, hp, speed, color, attack_range=50, is_aoe=False, is_boss=False,
                 is_b=False, atk=10, kb_limit=1, width=50, height=50, idle_frames=None,
                 move_frames=None, windup_frames=None, attack_frames=None, recovery_frames=None,
                 kb_frames=None, windup_duration=200, attack_duration=100, recovery_duration=50,
                 attack_interval=1000, hp_multiplier=1.0, atk_multiplier=1.0, done_attack=False,
                 reward=5, attack_type="gun"):
        super().__init__(x, y, int(hp * hp_multiplier), atk * atk_multiplier, speed, color, attack_range,
                         is_aoe, width, height, kb_limit, idle_frames, move_frames, windup_frames,
                         attack_frames, recovery_frames, kb_frames, windup_duration, attack_duration,
                         recovery_duration, attack_interval, attack_type)
        self.is_boss = is_boss
        self.reward = reward
        self.done_attack = done_attack

    def move(self):
        if not self.is_attacking and not self.kb_animation and self.anim_state not in ["windup", "attacking", "recovery"]:
            self.x += self.speed
            self.is_attacking = False
            self.anim_state = "moving"

    def get_attack_zone(self):
        return pygame.Rect(self.x + self.width, self.y, self.attack_range, self.height)

    def draw(self, screen):
        super().draw(screen)
        if self.is_boss:
            boss_label = pygame.font.SysFont(None, 20).render("Boss", True, (255, 0, 0))
            screen.blit(boss_label, (self.x, self.y - 20))