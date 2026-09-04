"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Tile.
"""

import pygame

from typing import Optional # Importamos Optional para tipado del power_up

import settings


class Tile:
    # Añadimos soporte para power_up (None, "line_clear", "color_bomb")
    def __init__(self, i: int, j: int, color: int, variety: int, power_up: Optional[str] = None) -> None:
   
        self.i = i
        self.j = j
        self.x = self.j * settings.TILE_SIZE
        self.y = self.i * settings.TILE_SIZE
        self.color = color
        self.variety = variety
        self.power_up = power_up  # Tipo de power-up ("line_clear", "color_bomb", o None)
        self.alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        
        
    def is_power_up(self):
        return self.power_up
    
    def render(self, surface: pygame.Surface, offset_x: int, offset_y: int) -> None:
        self.alpha_surface.blit(
            settings.TEXTURES["tiles"],
            (0, 0),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
        pygame.draw.rect(
            self.alpha_surface,
            (34, 32, 52, 200),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )
        
        
        # Si la baldosa tiene un power-up activo, dibujamos un indicador visual distintivo encima
        if self.power_up == "line_clear":
            pygame.draw.rect(
                self.alpha_surface,
                (255, 255, 255, 220),
                pygame.Rect(2, 2, settings.TILE_SIZE - 4, settings.TILE_SIZE - 4),
                width=3,
                border_radius=5,
            )
        elif self.power_up == "color_bomb":
           pygame.draw.circle(
                self.alpha_surface,
                (255, 215, 0, 240),
                (settings.TILE_SIZE // 2, settings.TILE_SIZE // 2),
                settings.TILE_SIZE // 3,
                width=4,
            )
        surface.blit(self.alpha_surface, (self.x + 2 + offset_x, self.y + 2 + offset_y))
        surface.blit(
            settings.TEXTURES["tiles"],
            (self.x + offset_x, self.y + offset_y),
            settings.FRAMES["tiles"][self.color][self.variety],
        )
