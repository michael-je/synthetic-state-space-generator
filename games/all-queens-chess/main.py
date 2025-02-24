from enum import Enum
from typing import Union
import random
from time import sleep

class CellType(Enum):
    Empty = 0
    WhiteQ = 1
    BlackQ = 2

class Player(Enum):
    White = 1
    Black = -1

DIM = 5
DIRS = [
    (-1, -1), (-1,  0), (-1,  1),
    ( 0, -1),           ( 0,  1),
    ( 1, -1), ( 1,  0), ( 1,  1),
]

class AllQueensChess:
    def __init__(self):
        self.cells = [
            [CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ],
            [CellType.Empty] * 5,
            [CellType.WhiteQ] + [CellType.Empty] * 3 + [CellType.BlackQ],
            [CellType.Empty] * 5,
            [CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ],
        ]
        self.cur_player = Player.White
    
    def get_cell_type(self, cell: tuple[int, int]) -> CellType:
        i, j = cell
        return self.cells[i][j]
    
    def apply_dir(self, cell: tuple[int, int], dir: tuple[int, int]) -> tuple[int, int]:
        i, j = cell
        di, dj = dir
        return (i+di, j+dj)
    
    def cell_in_boundary(self, cell: tuple[int, int]) -> bool:
        i, j = cell
        return 0 <= i < DIM and 0 <= j < DIM
    
    def get_piece_moves(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for dir in DIRS:
            check_cell = self.apply_dir(cell, dir)
            while self.cell_in_boundary(check_cell) and self.get_cell_type(check_cell) == CellType.Empty:
                moves.append(check_cell)
                check_cell = self.apply_dir(check_cell, dir)
        return moves
    
    def print(self):
        print()
        rep = {CellType.Empty: '.', CellType.WhiteQ: 'W', CellType.BlackQ: 'B'}
        for row in self.cells:
            print(' '.join(rep[cell_t] for cell_t in row))
    
    def cell_type_of_player(self, player: Player):
        return CellType.WhiteQ if player == Player.White else CellType.BlackQ
    
    def get_player_pieces(self, player: Player) -> list[tuple[int, int]]:
        piece_t = self.cell_type_of_player(player)
        pieces = []
        for i in range(DIM):
            for j in range(DIM):
                if self.cells[i][j] == piece_t:
                    pieces.append((i, j))
        return pieces
    
    def get_available_moves(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        moves: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for piece in self.get_player_pieces(self.cur_player):
            for move in self.get_piece_moves(piece):
                moves.append((piece, move))
        return moves
    
    def make_move(self, piece: tuple[int, int], cell: tuple[int, int]) -> bool:
        if (piece, cell) not in self.get_available_moves():
            return False
        pi, pj = piece
        self.cells[pi][pj] = CellType.Empty
        ci, cj = cell
        self.cells[ci][cj] = self.cell_type_of_player(self.cur_player)
        self.cur_player = Player(-self.cur_player.value)
        return True
    
    def game_over(self) -> Union[Player, None]:
        for player in Player:
            piece_t = self.cell_type_of_player(player)
            for piece in self.get_player_pieces(player):
                for dir in DIRS:
                    cnt = 1
                    check_cell = self.apply_dir(piece, dir)
                    i, j = check_cell
                    while self.cell_in_boundary(check_cell) and self.cells[i][j] == piece_t:
                        cnt += 1
                        check_cell = self.apply_dir(check_cell, dir)
                        i, j = check_cell
                    if cnt >= 4:
                        return player
        return None


def main():
    board = AllQueensChess()
    board.print()
    while board.game_over() is None:
        board.make_move(*random.choice(board.get_available_moves()))
        board.print()
    print(f"{board.game_over().name} wins.")


main()