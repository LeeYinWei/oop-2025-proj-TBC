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
        self.alpha = .4 # This will still control the fade, but applied differently
        self.max_radius = max_radius
        self.thickness = thickness

        self.temp_surface = None # Initialize to None

        surface_dim = self.max_radius * 2
        if surface_dim <= 0:
            print(f"WARNING: Invalid surface dimension ({surface_dim}) for ShockwaveEffect at init. Not creating surface.")
            return

        try:
            # We keep SRCALPHA because we draw a transparent "hole" with (0,0,0,0)
            self.temp_surface = pygame.Surface((surface_dim, surface_dim), pygame.SRCALPHA)
            print(f"DEBUG: Initialized ShockwaveEffect at ({self.x},{self.y}). temp_surface created.")
        except pygame.error as e:
            print(f"CRITICAL ERROR: Failed to create temp_surface for ShockwaveEffect at ({self.x}, {self.y}): {e}")
        except Exception as e:
            print(f"UNEXPECTED ERROR: Failed to create temp_surface for ShockwaveEffect at ({self.x}, {self.y}): {e}")

    def update(self, now):
        current_time = now
        elapsed = current_time - self.start_time
        if elapsed >= self.duration:
            # print(f"DEBUG: Shockwave at ({self.x},{self.y}) finished.")
            return False
        self.alpha = max(0, 1.0 - (elapsed / self.duration))
        return True

    def draw(self, screen):
        # Always check if temp_surface was successfully created
        if self.temp_surface is None or self.alpha <= 0:
            return

        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.start_time
        progress = elapsed / self.duration
        radius = int(self.max_radius * progress)

        if radius <= 0:
            return

        # Clear the temporary surface for the current frame's drawing
        self.temp_surface.fill((0, 0, 0, 0)) # Fill with fully transparent

        # Calculate the actual alpha for drawing the shockwave color based on self.alpha
        
        shockwave_rgba = (100, 100, 255, self.alpha) # RGBA color

        # Draw the outer filled circle with transparency
        pygame.draw.circle(self.temp_surface, shockwave_rgba, (self.max_radius, self.max_radius), radius)

        # Draw the inner filled circle to create the "thickness" effect (this still uses full transparency)
        inner_radius = max(0, radius - self.thickness)
        if inner_radius > 0:
            hole_color = (0, 0, 0, 0) # Fully transparent black for cutting out the hole
            pygame.draw.circle(self.temp_surface, hole_color, (self.max_radius, self.max_radius), inner_radius)

        # --- CRITICAL CHANGE: Remove self.temp_surface.set_alpha() ---
        # Instead, we will rely on the alpha of the colors drawn onto temp_surface,
        # and the BLEND_RGBA_MULT blit flag.
        # self.temp_surface.set_alpha(current_alpha_int) # REMOVE THIS LINE

        # Blit the temporary surface onto the main screen using BLEND_RGBA_MULT
        # This blend mode multiplies the source's alpha with destination.
        # So, if shockwave_rgba has alpha=255, it's fully opaque. If alpha=0, it's fully transparent.
        screen.blit(self.temp_surface, (self.x - self.max_radius, self.y - self.max_radius), special_flags=pygame.BLEND_RGBA_MULT)