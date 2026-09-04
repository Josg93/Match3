"""
ISPPV1 2023
Study Case: Match-3

Author: Alejandro Mujica
alejandro.j.mujic4@gmail.com

This file contains the class PlayState.
"""

from typing import Dict, Any, List, Optional
from src.Tile import Tile

import pygame

from gale.input_handler import InputData
from gale.state import BaseState
from gale.text import render_text
from gale.timer import Timer

import settings


class PlayState(BaseState):
    def enter(self, **enter_params: Dict[str, Any]) -> None:
        self.level = enter_params["level"]
        self.board = enter_params["board"]
        self.score = enter_params["score"]

        self.active = True
        self.is_dragging = False          
        self.selected_tile = None        
        
        self.timer = settings.LEVEL_TIME

        self.goal_score = self.level * 1.25 * 3000

        # A surface that supports alpha to highlight a selected tile
        self.tile_alpha_surface = pygame.Surface(
            (settings.TILE_SIZE, settings.TILE_SIZE), pygame.SRCALPHA
        )
        pygame.draw.rect(
            self.tile_alpha_surface,
            (255, 255, 255, 96),
            pygame.Rect(0, 0, settings.TILE_SIZE, settings.TILE_SIZE),
            border_radius=7,
        )

        # A surface that supports alpha to draw behind the text.
        self.text_alpha_surface = pygame.Surface((212, 136), pygame.SRCALPHA)
        pygame.draw.rect(
            self.text_alpha_surface, (56, 56, 56, 234), pygame.Rect(0, 0, 212, 136)
        )

        def decrement_timer():
            self.timer -= 1

            # Play warning sound on timer if we get low
            if self.timer <= 5:
                settings.SOUNDS["clock"].play()

        Timer.every(1, decrement_timer)
        
        while not self.board.has_possible_matches():
            self.board._initialize_tiles()

    def update(self, _: float) -> None:
        if self.timer <= 0:
            Timer.clear()
            settings.SOUNDS["game-over"].play()
            self.state_machine.change("game-over", score=self.score)

        if self.score >= self.goal_score:
            Timer.clear()
            settings.SOUNDS["next-level"].play()
            self.state_machine.change("begin", level=self.level + 1, score=self.score)

    def _activate_power_up_directly(self, tile: Tile) -> None:
        # Activar el power-up inmediatamente cuando se hace clic sobre él
        power_up_matches = self.board.activate_power_up(tile)
        if power_up_matches is not None:
            self.board.matches.append(power_up_matches)
            self.board.remove_matches(True)
            
        # Continuar con la lógica de caída de fichas
        # (remove_matches se llamará naturalmente en el siguiente _calculate_matches)
        
        falling_tiles = self.board.get_falling_tiles()
        Timer.tween(
            0.70,
            falling_tiles,
            on_finish=lambda: self._calculate_matches(
                [item[0] for item in falling_tiles], last_moved=None
            ),
        )

    def render(self, surface: pygame.Surface) -> None:
        self.board.render(surface)
        if self.is_dragging and self.selected_tile is not None:
            # Resaltar casilla origen (donde estaba la ficha seleccionada en grid)
            x = self.selected_grid_j * settings.TILE_SIZE + self.board.x
            y = self.selected_grid_i * settings.TILE_SIZE + self.board.y
            surface.blit(self.tile_alpha_surface, (x, y))
            
            # Copia visual siguiendo el cursor
            if self.is_dragging == True and self.selected_tile is not None:
                drag_copy_x = (self.mouse_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH) - self.selected_tile.x
                drag_copy_y = (self.mouse_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT) - self.selected_tile.y
                # Dibujar la ficha en posición cursor usando su textura
                # pero sin alterar selected_tile.x/y
                self.selected_tile.render(surface, drag_copy_x, drag_copy_y )

        surface.blit(self.text_alpha_surface, (16, 16))
        render_text(
            surface,
            f"Level: {self.level}",
            settings.FONTS["medium"],
            30,
            24,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Score: {self.score}",
            settings.FONTS["medium"],
            30,
            52,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Goal: {self.goal_score}",
            settings.FONTS["medium"],
            30,
            80,
            (99, 155, 255),
            shadowed=True,
        )
        render_text(
            surface,
            f"Timer: {self.timer}",
            settings.FONTS["medium"],
            30,
            108,
            (99, 155, 255),
            shadowed=True,
        )

    def on_input(self, input_id: str, input_data: InputData) -> None:
        if not self.active:
            return
        
        # al presionar clic
        if input_id == "click" and input_data.pressed:
            self.mouse_x, self.mouse_y  = input_data.position
            pos_x = self.mouse_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = self.mouse_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE
        
            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                clicked_tile = self.board.tiles[i][j]
                
                # Si se hizo clic en un power-up, activarlo directamente
                if clicked_tile and clicked_tile.is_power_up():
                    self._activate_power_up_directly(clicked_tile)
                    self.active = True
                    return
                
                self.is_dragging = True
                self.selected_tile = clicked_tile
                self.selected_grid_i, self.selected_grid_j = i, j
                
        #al mover mouse y click presionado
        elif input_id == "mouse_motion":
            self.mouse_x, self.mouse_y = input_data.position
            pos_x = self.mouse_x * settings.VIRTUAL_WIDTH // settings.WINDOW_WIDTH
            pos_y = self.mouse_y * settings.VIRTUAL_HEIGHT // settings.WINDOW_HEIGHT
            i = (pos_y - self.board.y) // settings.TILE_SIZE
            j = (pos_x - self.board.x) // settings.TILE_SIZE

            if 0 <= i < settings.BOARD_HEIGHT and 0 <= j < settings.BOARD_WIDTH:
                self.target = self.board.tiles[i][j]
            else:
                self.target = None

        #al soltar click
        elif input_id == "click" and input_data.released:
            self.is_dragging = False
            #hacer swap:
            tile1 = self.selected_tile
            tile2 = self.target 
            if tile2 is None or tile1 is None:
                self.selected_tile = None
                self.target = None
                self.active = True
                return

            di = abs(tile1.i - tile2.i)
            dj = abs(tile1.j - tile2.j)
            if not ((di == 1 and dj == 0) or (di == 0 and dj == 1)):
                # Reproducir sonido de error y cancelar el movimiento si no son adyacentes
                settings.SOUNDS["error"].play()
                self.selected_tile = None
                self.target = None
                self.active = True
                return

            self.active = False           
            #arrive realiza el cambio lógico  
            def arrive():
                tile1 = self.selected_tile
                tile2 = self.target
                
                (self.board.tiles[tile1.i][tile1.j], self.board.tiles[tile2.i][tile2.j],
                ) = (self.board.tiles[tile2.i][tile2.j], self.board.tiles[tile1.i][tile1.j],)
                tile1.i, tile1.j, tile2.i, tile2.j = (
                    tile2.i,
                    tile2.j,
                    tile1.i,
                    tile1.j,
                )
                
                self.selected_tile, self.target = None, None
                self._calculate_matches([tile1, tile2], user_swap=True, last_moved=tile2)

            if tile2 is not None:        
                Timer.tween(
                    0.25,
                    [
                        (tile1, {"x": tile2.x, "y": tile2.y}),
                        (tile2, {"x": tile1.x, "y": tile1.y}),
                    ],
                    on_finish=arrive,
                )

    def _calculate_matches(self, tiles: List, user_swap=False, last_moved: Optional[Tile] = None) -> None:
        matches = self.board.calculate_matches_for(tiles, last_moved)
        if matches is None: 
            #si no hay matches y fue jugada del ususario
            if user_swap == True:    
                tile1 = tiles[0]
                tile2 = tiles[1]

                def arrive():
                    tile1 = tiles[0]
                    tile2 = tiles[1]

                    (self.board.tiles[tile1.i][tile1.j], self.board.tiles[tile2.i][tile2.j],
                    ) = (self.board.tiles[tile2.i][tile2.j], self.board.tiles[tile1.i][tile1.j],)
                    tile1.i, tile1.j, tile2.i, tile2.j = (
                        tile2.i,
                        tile2.j,
                        tile1.i,
                        tile1.j,
                    )

                    self.selected_tile, self.target = None, None
                Timer.tween(
                        0.25,
                        [
                            (tile1, {"x": tile2.x, "y": tile2.y}),
                            (tile2, {"x": tile1.x, "y": tile1.y}),
                        ],
                        on_finish=arrive,
                    )
                self.active = True
                return
            #si no hay matches y fue falling tiles
            else:
                while not self.board.has_possible_matches():
                    self.board._initialize_tiles()
                self.active = True
                return
            
        settings.SOUNDS["match"].stop()
        settings.SOUNDS["match"].play()
        for match in matches:
            self.score += len(match) * 50
          
        self.board.remove_matches()
        self.board.generate_power_ups()
        falling_tiles = self.board.get_falling_tiles()
        Timer.tween(
         0.70,
         falling_tiles,
         on_finish=lambda: self._calculate_matches(
             [item[0] for item in falling_tiles], last_moved=None
         ),
        )
