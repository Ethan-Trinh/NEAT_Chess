from const import*
from piece import *
from move import Move
from sound import Sound
import copy
import os

class Square:

    ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}

    def __init__(self, row, col, piece=None):
        self.row = row
        self.col = col
        self.piece = piece
        self.alphacols = self.ALPHACOLS[col]

    def __eq__(self, other):
        return self.row == other.row and self.col == other.col

    def has_piece(self):
        return self.piece != None
    
    def is_empty(self):
        return not self.has_piece()
    
    def has_ally_piece(self, color):
        return self.has_piece() and self.piece.color == color
    
    def has_enemy_piece(self, color):
        return self.has_piece() and self.piece.color != color
    
    def is_empty_or_enemy(self, color):
        return self.is_empty() or self.has_enemy_piece(color)
    
    @staticmethod
    def in_range(*args):
        for arg in args:
            if arg < 0 or arg > 7:
                return False
        
        return True
    
    @staticmethod
    def get_alphacol(col):
        ALPHACOLS = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h'}
        return ALPHACOLS[col]

class Board:

    def __init__(self):
        self.squares = [[0, 0, 0, 0, 0, 0, 0, 0] for col in range(COLS)]
        self.last_move = None

        self._create()
        self._add_pieces('white')
        self._add_pieces('black')

    def move(self, piece, move, testing=False):
        initial = move.initial
        final = move.final 

        en_passant_empty = self.squares[final.row][final.col].is_empty()

        # Console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # Pawn Special Actions
        if isinstance(piece, Pawn):
            diff = final.col - initial.col         
            if diff != 0 and en_passant_empty:
                diff = final.col - initial.col         
                self.squares[initial.row][initial.col + diff].piece = None
                self.squares[final.row][final.col].piece = piece
                if not testing:
                    sound = Sound(
                        os.path.join('assets/sounds/capture.wav')
                    )
                    sound.play()

            else:
                self.check_promotion(piece, final)

        # If King Castles
        if isinstance(piece, King):
            if self.castling(initial, final) and not testing:
                diff = final.col - initial.col
                rook = piece.a_rook if (diff < 0) else piece.h_rook
                self.move(rook, rook.moves[-1])

        # Move
        piece.moved = True

        # Clear valid moves
        piece.clear_moves()

        # Set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves
    
    def check_promotion(self, piece, final):
        if final.row == 0 or final.row == 7:        # If a pawn reaches the back ranks
            self.squares[final.row][final.col].piece = Queen(piece.color)   # Programmed for pawn to become a queen

    def castling(self, initial, final):
        return abs(initial.col - final.col) == 2
    
    def set_en_passant_true(self,piece):
        if not isinstance(piece, Pawn):
            return
        
        for row in range(ROWS):
            for col in range(COLS):
                if isinstance(self.squares[row][col].piece, Pawn):
                    self.squares[row][col].piece.en_passant = False

        piece.en_passant = True
    
    def in_check(self, piece, move):
        temp_piece = copy.deepcopy(piece)
        temp_board = copy.deepcopy(self)
        temp_board.move(temp_piece, move, testing=True)

        for row in range(ROWS):
            for col in range(COLS):
                if temp_board.squares[row][col].has_enemy_piece(piece.color):
                    p = temp_board.squares[row][col].piece
                    temp_board.calc_moves(p, row, col, bool=False)

                    for m in p.moves:
                        if isinstance(m.final.piece, King):
                            return True
        
        return False

    def calc_moves(self, piece, row, col, bool=True):
        
        def pawn_moves():
            # Pawns can advance 2 spaces forward if on the their respective home row
            steps = 1 if piece.moved else 2

            # Vertical move
            start = row + piece.dir
            end = row + (piece.dir * (1 + steps))

            for possible_move_row in range(start, end, piece.dir):
                if Square.in_range(possible_move_row):
                    if self.squares[possible_move_row][col].is_empty():
                        # create initial and final position
                        initial = Square(row, col)
                        final = Square(possible_move_row, col)

                        # create move
                        move = Move(initial, final)

                        if bool:
                            # look for checks
                            if not self.in_check(piece, move):
                                # append move
                                piece.add_move(move)
                        else:
                            piece.add_move(move)
                    # Blocked
                    else:
                        break
                else:
                    break

            # Diagonal move
            possible_move_row = row + piece.dir
            possible_move_cols = [col-1, col+1]

            for possible_move_col in possible_move_cols:
                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                        # create initial and final position
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create move and append
                        move = Move(initial, final)
                        
                        if bool:
                            # look for checks
                            if not self.in_check(piece, move):
                                # append move
                                piece.add_move(move)
                        else:
                            piece.add_move(move)

            # En Passant
            r = 3 if piece.color == 'white' else 4
            fr = 2 if piece.color == 'white' else 5

            #En Passant left
            if Square.in_range(col - 1) and row == r:
                if self.squares[row][col-1].has_enemy_piece(piece.color):
                    p = self.squares[row][col-1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col-1, p)

                            # create move and append
                            move = Move(initial, final)
                            
                            if bool:
                            # look for checks
                                if not self.in_check(piece, move):
                                    # append move
                                    piece.add_move(move)
                                else:
                                    piece.add_move(move)

            #En Passant right
            if Square.in_range(col + 1) and row == r:
                if self.squares[row][col + 1].has_enemy_piece(piece.color):
                    p = self.squares[row][col + 1].piece
                    if isinstance(p, Pawn):
                        if p.en_passant:
                            initial = Square(row, col)
                            final = Square(fr, col + 1, p)

                            # create move and append
                            move = Move(initial, final)
                            
                            if bool:
                            # look for checks
                                if not self.in_check(piece, move):
                                    # append move
                                    piece.add_move(move)
                                else:
                                    piece.add_move(move)

        def knight_moves():
            # Knights have 8 possible moves
            # for example, a knight on D4 can move to
            possible_moves = [
                (row-2, col-1),     #C6
                (row-2, col+1),     #E6
                (row-1, col-2),     #B5
                (row-1, col+2),     #F5
                (row+1, col-2),     #B3
                (row+1, col+2),     #F3
                (row+2, col-1),     #C2
                (row+2, col+1),     #E2
            ]

            # Check if possible move is within the board
            for possible_move in possible_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        # create squares
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)    #piece=pieces

                        # create move and append
                        move = Move(initial, final)
                        
                        if bool:
                            # look for checks
                            if not self.in_check(piece, move):
                                # append move
                                piece.add_move(move)
                            else: break
                        else:
                            piece.add_move(move)

        def line_move(incraments):
            for incr in incraments:
                row_incr, col_incr = incr
                possible_move_row = row + row_incr
                possible_move_col = col + col_incr

                while True:
                    if Square.in_range(possible_move_row, possible_move_col):

                        # create initial and final position
                        initial = Square(row, col)
                        final_piece = self.squares[possible_move_row][possible_move_col].piece
                        final = Square(possible_move_row, possible_move_col, final_piece)

                        # create move
                        move = Move(initial, final)

                        # If square is empty, continue loop
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            if bool:
                                # look for checks
                                if not self.in_check(piece, move):
                                    # append move
                                    piece.add_move(move)
                                
                            else:
                                piece.add_move(move)

                        # If has an enemy piece, add move then break
                        elif self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            if bool:
                                # look for checks
                                if not self.in_check(piece, move):
                                    # append move
                                    piece.add_move(move)
                                
                            else:
                                piece.add_move(move)
                            break

                        # Has ally piece, break
                        elif self.squares[possible_move_row][possible_move_col].has_ally_piece(piece.color):
                            break

                    else: break

                    # Increment incrs
                    possible_move_row = possible_move_row + row_incr
                    possible_move_col = possible_move_col + col_incr

        def king_moves():
            adj_moves = [
                (row-1, col+0),      # up
                (row-1, col+1),      # up-right
                (row-1, col-1),      # up-left
                (row+0, col+1),      # right
                (row+0, col-1),      # left
                (row+1, col+0),      # down
                (row+1, col+1),      # down-right
                (row+1, col-1),      # down-left
            ]

            for possible_move in adj_moves:
                possible_move_row, possible_move_col = possible_move

                if Square.in_range(possible_move_row, possible_move_col):
                    if self.squares[possible_move_row][possible_move_col].is_empty_or_enemy(piece.color):
                        # create squares
                        initial = Square(row, col)
                        final = Square(possible_move_row, possible_move_col)

                        # create move and append
                        move = Move(initial, final)
                        if bool:
                                # look for checks
                                if not self.in_check(piece, move):
                                    # append move
                                    piece.add_move(move)
                                else: break                
                        else:
                            piece.add_move(move)

                # Castling Method
                if not piece.moved:
                    # Queen side castle
                    a_rook = self.squares[row][0].piece
                    if isinstance(a_rook, Rook):
                        if not a_rook.moved:
                            # If there is a piece on the the B, C and D file, break loop
                            for i in range(1, 4):
                                if self.squares[row][i].has_piece():
                                    break

                                if i == 3:
                                    # adds A rook to king
                                    piece.a_rook = a_rook

                                    # rook move
                                    initial = Square(row, 0)
                                    final = Square(row, 3)
                                    move_R = Move(initial, final)

                                    # king move
                                    initial = Square(row, col)
                                    final = Square(row, 2)
                                    move_K = Move(initial, final)

                                    if bool:
                                            # look for checks
                                        if not self.in_check(piece, move_K) and not self.in_check(a_rook, move_R):
                                            # append moves
                                            a_rook.add_move(move_R)
                                            piece.add_move(move_K)
                                        
                                    else:
                                        # append new move to rook
                                        a_rook.add_move(move_R)
                                        piece.add_move(move_K)
                            
                    # King side castle
                    h_rook = self.squares[row][7].piece
                    if isinstance(h_rook, Rook):
                        if not h_rook.moved:
                            # If there is a piece on the the F and G file, break loop
                            for i in range(5, 7):
                                if self.squares[row][i].has_piece():
                                    break

                                if i == 6:
                                    # adds H rook to king
                                    piece.h_rook = h_rook

                                    # rook move
                                    initial = Square(row, 7)
                                    final = Square(row, 5)
                                    move_R = Move(initial, final)

                                    # king move
                                    initial = Square(row, col)
                                    final = Square(row, 6)
                                    move_K = Move(initial, final)

                                    if bool:
                                            # look for checks
                                        if not self.in_check(piece, move_K) and not self.in_check(h_rook, move_R):
                                            # append moves
                                            h_rook.add_move(move_R)
                                            piece.add_move(move_K)
                                        
                                    else:
                                        # append new move to rook
                                        h_rook.add_move(move_R)
                                        piece.add_move(move_K)


        if isinstance(piece, Pawn): 
            pawn_moves()

        elif isinstance(piece, Knight): 
            knight_moves()

        elif isinstance(piece, Bishop): 
            line_move([
                (-1, 1),     # up-right
                (-1, -1),    # up-left
                (1, 1),      # down-right
                (1, -1),     # down-left
            ])

        elif isinstance(piece, Rook): 
            line_move([
                (-1, 0),     # up
                (1, 0),      # down
                (0, 1),      # left
                (0, -1),     # right
            ])

        elif isinstance(piece, Queen): 
            line_move([
                (-1, 0),     # up
                (1, 0),      # down
                (0, 1),      # left
                (0, -1),     # right
                (-1, 1),     # up-right
                (-1, -1),    # up-left
                (1, 1),      # down-right
                (1, -1),     # down-left
            ])

        elif isinstance(piece, King):
            king_moves()

    def _create(self):
        for row in range(ROWS):
            for col in range(COLS):
                self.squares[row][col] = Square(row, col)

    def _add_pieces(self, color):
        row_pawn, row_other = (6, 7) if color == 'white' else (1, 0)

        # Create Pawns
        for col in range(COLS):
            self.squares[row_pawn][col] = Square(row_pawn, col, Pawn(color))

        # Knights
        self.squares[row_other][1] = Square(row_other, 1, Knight(color))
        self.squares[row_other][6] = Square(row_other, 6, Knight(color))

        # Bishops
        self.squares[row_other][2] = Square(row_other, 2, Bishop(color))
        self.squares[row_other][5] = Square(row_other, 5, Bishop(color))

        # Rooks
        self.squares[row_other][0] = Square(row_other, 0, Rook(color))
        self.squares[row_other][7] = Square(row_other, 7, Rook(color))

        # Queen
        self.squares[row_other][3] = Square(row_other, 3, Queen(color))

        # King
        self.squares[row_other][4] = Square(row_other, 4, King(color))