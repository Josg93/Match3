"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class Board.
"""

from typing import List, Optional, Tuple, Any, Dict, Set

import pygame

import random

import settings
from src.Tile import Tile


class Board:
    def __init__(self, x: int, y: int) -> None:
        self.x = x
        self.y = y
        self.matches: List[List[Tile]] = []
        self.tiles: List[List[Tile]] = []
        self._initialize_tiles()
        self.powerups = []

    def render(self, surface: pygame.Surface) -> None:
        for row in self.tiles:
            for tile in row:
                tile.render(surface, self.x, self.y)

    def _is_match_generated(self, i: int, j: int, color: int) -> bool:
        if (
            i >= 2
            and self.tiles[i - 1][j].color == color
            and self.tiles[i - 2][j].color == color
        ):
            return True

        return (
            j >= 2
            and self.tiles[i][j - 1].color == color
            and self.tiles[i][j - 2].color == color
        )

    def _initialize_tiles(self) -> None:
        self.tiles = [
            [None for _ in range(settings.BOARD_WIDTH)]
            for _ in range(settings.BOARD_HEIGHT)
        ]
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                color = random.randint(14, settings.NUM_COLORS - 1)
                while self._is_match_generated(i, j, color):
                    color = random.randint(14, settings.NUM_COLORS - 1)

                self.tiles[i][j] = Tile(
                    i, j, color, random.randint(0, settings.NUM_VARIETIES - 1)
                )

    def has_possible_matches(self) -> bool:
        for i in range(settings.BOARD_HEIGHT):
            for j in range(settings.BOARD_WIDTH):
                tile1 = self.tiles[i][j]
                if tile1 is None:
                    continue
                
                # Probar intercambio con el vecino derecho (j + 1)
                if j + 1 < settings.BOARD_WIDTH:
                    tile2 = self.tiles[i][j + 1]
                    if tile2 is not None:
                        # Intercambio lógico temporal
                        self.tiles[i][j], self.tiles[i][j + 1] = tile2, tile1
                        tile1.i, tile1.j, tile2.i, tile2.j = i, j + 1, i, j
                        
                        matches = self.calculate_matches_for([tile1, tile2])
                        
                        # Revertir intercambio lógico
                        self.tiles[i][j], self.tiles[i][j + 1] = tile1, tile2
                        tile1.i, tile1.j, tile2.i, tile2.j = i, j, i, j + 1
                        
                        if matches is not None:
                            return True
                    
                # Probar intercambio con el vecino inferior (i + 1)
                if i + 1 < settings.BOARD_HEIGHT:
                    tile2 = self.tiles[i + 1][j]
                    if tile2 is not None:
                        # Intercambio lógico temporal
                        self.tiles[i][j], self.tiles[i + 1][j] = tile2, tile1
                        tile1.i, tile1.j, tile2.i, tile2.j = i + 1, j, i, j
                        
                        matches = self.calculate_matches_for([tile1, tile2])
                        
                        # Revertir intercambio lógico
                        self.tiles[i][j], self.tiles[i + 1][j] = tile1, tile2
                        tile1.i, tile1.j, tile2.i, tile2.j = i, j, i + 1, j
                        
                        if matches is not None:
                            return True
                      
        return False

    def _calculate_match_rec(self, tile: Tile) -> Set[Tile]:
        if tile in self.in_stack:
            return []

        self.in_stack.add(tile)

        color_to_match = tile.color

        ## Check horizontal match
        h_match: List[Tile] = []

        # Check left
        if tile.j > 0:
            left = max(0, tile.j - 2)
            for j in range(tile.j - 1, left - 1, -1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        # Check right
        if tile.j < settings.BOARD_WIDTH - 1:
            right = min(settings.BOARD_WIDTH - 1, tile.j + 2)
            for j in range(tile.j + 1, right + 1):
                if self.tiles[tile.i][j].color != color_to_match:
                    break
                h_match.append(self.tiles[tile.i][j])

        ## Check vertical match
        v_match: List[Tile] = []

        # Check top
        if tile.i > 0:
            top = max(0, tile.i - 2)
            for i in range(tile.i - 1, top - 1, -1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        # Check bottom
        if tile.i < settings.BOARD_HEIGHT - 1:
            bottom = min(settings.BOARD_HEIGHT - 1, tile.i + 2)
            for i in range(tile.i + 1, bottom + 1):
                if self.tiles[i][tile.j].color != color_to_match:
                    break
                v_match.append(self.tiles[i][tile.j])

        match: List[Tile] = []

        if len(h_match) >= 2:
            for t in h_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(v_match) >= 2:
            for t in v_match:
                if t not in self.in_match:
                    self.in_match.add(t)
                    match.append(t)

        if len(match) > 0:
            if tile not in self.in_match:
                self.in_match.add(tile)
                match.append(tile)

        for t in match:
            match += self._calculate_match_rec(t)

        self.in_stack.remove(tile)
        return match

    def calculate_power_ups(self, last_tile: Tile, type: str) -> None:
        valid_types = {"line_clear", "color_bomb"}
        if type not in valid_types:
            raise ValueError(f"Tipo de power-up inválido: {type}. Use {valid_types}")
        
        # Generar power-up en la posición de la última baldosa movida,
        # heredando el color de las baldosas combinadas
        i = last_tile.i
        j = last_tile.j
        powerup = Tile(i,j,last_tile.color,last_tile.variety, type)
        self.powerups.append(powerup) 

    def generate_power_ups(self):
        for powerup in self.powerups:
            self.tiles[powerup.i][powerup.j] = powerup  
   
   
    def activate_power_up(self, tile: Tile) -> List[Tile]:
        # Lista de baldosas afectadas por la activación del power-up
        matched_tiles = [tile]
        
        #Si es Limpia-Líneas (4 baldosas), destruye su fila y columna completas
        if tile.power_up == "line_clear":
            # Añadir todas las baldosas de la misma fila i
            for j_idx in range(settings.BOARD_WIDTH):
                t = self.tiles[tile.i][j_idx]
                if t and t not in matched_tiles:
                    matched_tiles.append(t)
            # Añadir todas las baldosas de la misma columna j
            for i_idx in range(settings.BOARD_HEIGHT):
                t = self.tiles[i_idx][tile.j]
                if t and t not in matched_tiles:
                    matched_tiles.append(t)
            settings.SOUNDS["line_clear"].play()        
        # Si es Bomba de Color (5+ baldosas), destruye todas las baldosas del mismo color en el tablero
        elif tile.power_up == "color_bomb":
            for row in self.tiles:
                for t in row:
                    if t and t.color == tile.color and t not in matched_tiles:
                        matched_tiles.append(t)
            settings.SOUNDS["color_bomb"].play()            
        # Marcar power-up como consumido (su efecto ya se aplicó)
        tile.power_up_consumed = True
        return matched_tiles

    def calculate_matches_for(self, new_tiles: List[Tile], last_moved: Optional[Tile] = None) -> Optional[List[List[Tile]]]:
        self.matches = []
        self.in_match: Set[Tile] = set()
        self.in_stack: Set[Tile] = set()

        for tile in new_tiles:
            if tile in self.in_match:
                continue
            match = self._calculate_match_rec(tile)
            if len(match) > 0:
                self.matches.append(match)

            if len(match) >= 4:
                power_tile = None
                if last_moved is not None and last_moved in match:
                    power_tile = last_moved
                elif len(new_tiles) > 0 and new_tiles[0] in match:
                    power_tile = new_tiles[0]
                else:
                    power_tile = match[0]

                if len(match) == 4:
                    self.calculate_power_ups(last_tile=power_tile, type="line_clear")
                elif len(match) >= 5:
                    self.calculate_power_ups(last_tile=power_tile, type="color_bomb")
                    
            #verificar que un powerup haya hecho match 
            activated_powerups: Set[Tile] = set()
            for tile in match:
                if tile.power_up is not None and tile not in activated_powerups:
                    power_up_matches = self.activate_power_up(tile)
                    activated_powerups.add(tile)
                    if len(power_up_matches) > 1:
                        self.matches.append(power_up_matches)    
                    
        delattr(self, "in_match")
        delattr(self, "in_stack")

        return self.matches if len(self.matches) > 0 else None

    def remove_matches(self) -> None:
        for match in self.matches:
            for tile in match:
                if tile.power_up is not None and not tile.power_up_consumed:
                    # Power-up activo sin consumir - no lo removemos, se queda en el tablero
                    continue
                self.tiles[tile.i][tile.j] = None   
        self.matches = []

    def get_falling_tiles(self) -> Tuple[Any, Dict[str, Any]]:
        # List of tweens to create
        tweens: Tuple[Tile, Dict[str, Any]] = []

        # for each column, go up tile by tile until we hit a space
        for j in range(settings.BOARD_WIDTH):
            space = False
            space_i = -1
            i = settings.BOARD_HEIGHT - 1

            while i >= 0:
                tile = self.tiles[i][j]

                # if our previous tile was a space
                if space:
                    # if the current tile is not a space
                    if tile is not None:
                        self.tiles[space_i][j] = tile
                        tile.i = space_i

                        # set its prior position to None
                        self.tiles[i][j] = None

                        tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))
                        space = False
                        i = space_i
                        space_i = -1
                elif tile is None:
                    space = True

                    if space_i == -1:
                        space_i = i

                i -= 1

        # create a replacement tiles at the top of the screen
        for j in range(settings.BOARD_WIDTH):
            for i in range(settings.BOARD_HEIGHT):
                tile = self.tiles[i][j]

                if tile is None:
                    tile = Tile(
                        i,
                        j,
                        random.randint(0, settings.NUM_COLORS - 1),
                        random.randint(0, settings.NUM_VARIETIES - 1),
                    )
                    tile.y -= settings.TILE_SIZE
                    self.tiles[i][j] = tile
                    tweens.append((tile, {"y": tile.i * settings.TILE_SIZE}))

        return tweens
