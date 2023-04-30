from const import*
from piece import *
from move import Move

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

    def move(self, piece, move):
        initial = move.initial
        final = move.final 

        # console board move update
        self.squares[initial.row][initial.col].piece = None
        self.squares[final.row][final.col].piece = piece

        # move
        piece.moved = True

        # clear valid moves
        piece.clear_moves()

        # set last move
        self.last_move = move

    def valid_move(self, piece, move):
        return move in piece.moves

    def calc_moves(self, piece, row, col):
        
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
                        piece.add_move(move)
                        
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
                        final = Square(possible_move_row, possible_move_col)

                        # create move and append
                        move = Move(initial, final)
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
                        final = Square(possible_move_row, possible_move_col)    #piece=pieces

                        # create move and append
                        move = Move(initial, final)
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
                        final = Square(possible_move_row, possible_move_col)

                        # create move
                        move = Move(initial, final)

                        # If square is empty, continue loop
                        if self.squares[possible_move_row][possible_move_col].is_empty():
                            # append move
                            piece.add_move(move)

                        # If has an enemy piece, add move then break
                        if self.squares[possible_move_row][possible_move_col].has_enemy_piece(piece.color):
                            piece.add_move(move)
                            break

                        # Has ally piece, break
                        if self.squares[possible_move_row][possible_move_col].has_ally_piece(piece.color):
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
                        piece.add_move(move)

                # Castling Methods

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