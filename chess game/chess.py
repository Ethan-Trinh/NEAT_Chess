import pygame

from const import *
from board import Board, Square
from dragger import Dragger
from config import Config

class Chess:

    def __init__(self):
        self.turn_player = 'white'
        self.hovered_square = None
        self.board = Board()
        self.dragger = Dragger()
        self.config = Config()

# render methods
    def show_bg(self, surface):
        theme = self.config.theme

        for row in range(ROWS):
            for col in range(COLS):

                #if (row + col) % 2 == 0:
                #    color = (234, 235, 200) # Light Green Tile
                #else:
                #    color = (119, 154, 88)  # Dark Green Tile

                color = theme.bg.light if (row + col) % 2 == 0 else theme.bg.dark
                
                rect = (col * SQSIZE, row * SQSIZE, SQSIZE, SQSIZE)

                pygame.draw.rect(surface, color, rect)

                if col == 0:
                    # color
                    color = theme.bg.dark if row % 2 == 0 else theme.bg.light
                    
                    # label
                    label = self.config.font.render(str(ROWS-row), 1, color)
                    label_pos = (5, 5 + row * SQSIZE)

                    # blit
                    surface.blit(label, label_pos)

                if row == 7:
                    # color
                    color = theme.bg.dark if (row + col) % 2 == 0 else theme.bg.light
                    
                    # label
                    label = self.config.font.render(Square.get_alphacol(col), 1, color)
                    label_pos = (col * SQSIZE + SQSIZE - 20, HEIGHT - 20)

                    # blit
                    surface.blit(label, label_pos)



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
        theme = self.config.theme

        if self.dragger.dragging:
            piece = self.dragger.piece

            # Find all valid moves
            for move in piece.moves:
                # color
                #color = '#C86464' if (move.final.row + move.final.col) % 2 == 0 else '#C84646'
                color = theme.moves.light if (move.final.row + move.final.col) % 2 == 0 else theme.moves.dark

                # rect
                rect = (move.final.col * SQSIZE, move.final.row * SQSIZE, SQSIZE, SQSIZE)

                # blit
                pygame.draw.rect(surface, color, rect)

    def show_last_move(self, surface):
        theme = self.config.theme

        if self.board.last_move:
            initial = self.board.last_move.initial
            final = self.board.last_move.final

            for pos in [initial, final]:
                # color
                #color = (244, 247, 116) if (pos.row + pos.col) % 2 == 0 else (172, 195, 51)
                color = theme.trace.light if (pos.row + pos.col) % 2 == 0 else theme.trace.dark

                # rect
                rect = (pos.col * SQSIZE, pos.row * SQSIZE, SQSIZE, SQSIZE)

                # blit
                pygame.draw.rect(surface, color, rect)

    def show_hover(self, surface):
        if self.hovered_square:
            # color
            color = (180, 180, 180)

            # rect
            rect = (self.hovered_square.col * SQSIZE, self.hovered_square.row * SQSIZE, SQSIZE, SQSIZE)

            # blit
            pygame.draw.rect(surface, color, rect, width=10)



    # other methods
    def next_turn(self):
        if self.turn_player == 'black':
            self.turn_player = 'white' 
        else:
            self.turn_player = 'black'

    def set_hover(self, row, col):
        self.hovered_square = self.board.squares[row][col]

    def play_sound(self, captured=False):
        if captured:
            self.config.capture_sound.play()
        else:
            self.config.move_sound.play()
        