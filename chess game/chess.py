import pygame

from const import *
from board import Board
from dragger import Dragger

class Chess:

    def __init__(self):
        self.board = Board()
        self.dragger = Dragger()

# Show background tiles
    def show_bg(self, surface):

        for row in range(ROWS):
            for col in range(COLS):
                if (row + col) % 2 == 0:
                    color = (234, 235, 200) # Light Green Tile
                else:
                    color = (119, 154, 88)  # Dark Green Tile
                
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)

                pygame.draw.rect(surface, color, rect)

    def show_pieces(self, surface):
        for row in range(ROWS):
            for col in range(COLS):

                if self.board.squares[row][col].has_piece():
                    piece = self.board.squares[row][col].piece

                    # All pieces except dragging piece
                    if piece is not self.dragger.piece:
                        piece.set_texture(size=80)
                        img = pygame.image.load(piece.texture)
                        img_center = col * SQSIZE + SQSIZE // 2, row * SQSIZE + SQSIZE // 2
                        piece.texture_rect = img.get_rect(center = img_center)
                        surface.blit(img, piece.texture_rect)

    def show_moves(self, surface):
        if self.dragger.dragging:
            piece = self.dragger.piece

            # Find all valid moves
            for move in piece.moves:
                # color
                color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'

                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)

                # blit
                pygame.draw.rect(surface, color, rect)