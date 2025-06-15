import pygame
import math
import sys, os
import random

class ShockwaveEffect:
    def __init__(self, x, y, max_radius=200, duration=1000, thickness=5):
        self.x = x
        self.y = y
        self.start_time = pygame.time.get_ticks()
        self.duration = duration
        self.alpha = 1.0
        self.max_radius = max_radius
        self.thickness = thickness

    def update(self, now):
        current_time = now
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        # Print at the very start of draw to confirm it's being called
        # print(f"DEBUG: Shockwave.draw called for obj at ({self.x},{self.y}) with alpha={self.alpha:.2f}")

        if self.alpha > 0:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.start_time
            progress = elapsed / self.duration
            radius = int(self.max_radius * progress)

            # --- Critical Check 1: Radius and Surface Size ---
            if radius <= 0:
                # print("DEBUG: Radius is 0 or less, skipping draw.")
                return

            surface_width = self.max_radius * 2
            surface_height = self.max_radius * 2
            # print(f"DEBUG: Creating temp_surface of size ({surface_width}, {surface_height})")

            # Try a different surface flag if SRCALPHA is problematic, though it shouldn't be
            # You can try pygame.HWACCEL for hardware acceleration if available,
            # but SRCALPHA is usually what you want for transparency.
            try:
                temp_surface = pygame.Surface((surface_width, surface_height), pygame.SRCALPHA)
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to create temp_surface: {e}")
                raise # Re-raise to see full traceback if this is the issue

            temp_surface.fill((0, 0, 0, 0)) # Fill with fully transparent

            shockwave_color = (100, 100, 255) # RGB only
            # print(f"DEBUG: Drawing outer circle: color={shockwave_color}, center=({self.max_radius}, {self.max_radius}), radius={radius}")

            # --- Critical Check 2: Outer Circle Draw ---
            try:
                pygame.draw.circle(temp_surface, shockwave_color, (self.max_radius, self.max_radius), radius)
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to draw outer circle: {e}")
                raise

            inner_radius = max(0, radius - self.thickness)
            if inner_radius > 0:
                # print(f"DEBUG: Drawing inner circle: color=(0,0,0,0), center=({self.max_radius}, {self.max_radius}), radius={inner_radius}")
                # --- Critical Check 3: Inner Circle Draw ---
                try:
                    pygame.draw.circle(temp_surface, (0, 0, 0, 0), (self.max_radius, self.max_radius), inner_radius)
                except Exception as e:
                    print(f"CRITICAL ERROR: Failed to draw inner circle: {e}")
                    raise

            alpha_for_blit = int(self.alpha * 255)
            # print(f"DEBUG: Setting temp_surface alpha to {alpha_for_blit}")
            # --- Critical Check 4: Set Alpha ---
            try:
                temp_surface.set_alpha(alpha_for_blit)
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to set surface alpha: {e}")
                raise

            blit_x = self.x - self.max_radius
            blit_y = self.y - self.max_radius
            # print(f"DEBUG: Blitting temp_surface to screen at ({blit_x}, {blit_y})")
            # --- Critical Check 5: Blit Operation ---
            try:
                screen.blit(temp_surface, (blit_x, blit_y))
            except Exception as e:
                print(f"CRITICAL ERROR: Failed to blit surface: {e}")
                raise