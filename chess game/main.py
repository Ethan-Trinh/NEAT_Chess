import pygame
import sys

from const import *
from chess import Chess
from board import Square
from move import Move

class Main:

    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('Chess')
        self.game = Chess()

    def mainloop(self):

        game = self.game
        screen = self.screen
        board = self.game.board
        dragger = self.game.dragger

        while True:
            # show methods
            game.show_bg(screen)
            game.show_last_move(screen)
            game.show_moves(screen)
            game.show_pieces(screen)
            game.show_hover(screen)

            if dragger.dragging:
                dragger.update_blit(screen)

            for event in pygame.event.get():

                # Click
                if event.type == pygame.MOUSEBUTTONDOWN:
                    dragger.update_mouse(event.pos)
                    print(event.pos)

                    clicked_row = dragger.mouseY // SQSIZE
                    clicked_col = dragger.mouseX // SQSIZE

                    #print(dragger.mouseY, clicked_row)
                    #print(dragger.mouseX, clicked_col)

                    if board.squares[clicked_row][clicked_col].has_piece():
                        piece = board.squares[clicked_row][clicked_col].piece

                        # Check if Valid Piece (turn player color)
                        if piece.color == game.turn_player:
                            board.calc_moves(piece, clicked_row, clicked_col)
                            dragger.save_initial(event.pos)
                            dragger.drag_piece(piece)

                            # show methods
                            game.show_bg(screen)
                            #game.show_last_move(screen)
                            game.show_moves(screen)
                            game.show_pieces(screen)
                            dragger.update_blit(screen)


                elif event.type == pygame.MOUSEMOTION:
                    motion_row = event.pos[1] // SQSIZE
                    motion_col = event.pos[0] // SQSIZE

                    game.set_hover(motion_row, motion_col)

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)
                        game.show_bg(screen)
                        game.show_last_move(screen)
                        game.show_moves(screen)
                        game.show_pieces(screen)
                        game.show_hover(screen)
                        dragger.update_blit(screen)

                elif event.type == pygame.MOUSEBUTTONUP:

                    if dragger.dragging:
                        dragger.update_mouse(event.pos)

                        relesed_row = dragger.mouseY // SQSIZE
                        relesed_col = dragger.mouseX // SQSIZE

                        # create possible moves
                        initial = Square(dragger.initial_row, dragger.initial_col)
                        final = Square(relesed_row, relesed_col)
                        move = Move(initial, final)

                        # Validates if move is valid, then moves piece
                        if board.valid_move(dragger.piece, move):
                            captured = board.squares[relesed_row][relesed_col].has_piece()
                            board.move(dragger.piece, move)

                            # sound method
                            game.play_sound(captured)

                            # show methods
                            game.show_bg(screen)
                            game.show_last_move(screen)
                            game.show_pieces(screen)

                            # change turn player
                            game.next_turn()

                    dragger.undrag_piece()

                # Close application
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            
            pygame.display.update()

main = Main()
main.mainloop()