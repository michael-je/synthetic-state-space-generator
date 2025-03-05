# https://ludii.games/details.php?keyword=All%20Queens%20Chess

from enum import Enum
from typing import Union
import random

class IllegalMove(Exception):
    pass

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
starting_board = [
    [CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ],
    [CellType.Empty] * 5,
    [CellType.WhiteQ] + [CellType.Empty] * 3 + [CellType.BlackQ],
    [CellType.Empty] * 5,
    [CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ, CellType.BlackQ, CellType.WhiteQ],
]
states_memo: dict[str, "AllQueensStateNode"] = dict()


class AllQueensStateNode:
    def __init__(self, parent: "AllQueensStateNode"=None, player: Player=Player.White, 
                 transition_move: tuple[tuple[int, int], tuple[int, int]]=None):
        self.cur_walk_parent = parent
        self.player = player
        self.transition_move = transition_move


class AllQueensChess:
    def __init__(self):
        self.root = AllQueensStateNode()
        self.cur = self.root
        self.board = starting_board
    
    def _get_cell_type(self, cell: tuple[int, int]) -> CellType:
        i, j = cell
        return self.board[i][j]
    
    def _apply_dir(self, cell: tuple[int, int], dir: tuple[int, int]) -> tuple[int, int]:
        i, j = cell
        di, dj = dir
        return (i+di, j+dj)
    
    def _cell_in_boundary(self, cell: tuple[int, int]) -> bool:
        i, j = cell
        return 0 <= i < DIM and 0 <= j < DIM
    
    def _get_piece_moves(self, cell: tuple[int, int]) -> list[tuple[int, int]]:
        moves: list[tuple[int, int]] = []
        for dir in DIRS:
            check_cell = self._apply_dir(cell, dir)
            while self._cell_in_boundary(check_cell) and self._get_cell_type(check_cell) == CellType.Empty:
                moves.append(check_cell)
                check_cell = self._apply_dir(check_cell, dir)
        return moves
    
    def print(self):
        print()
        rep = {CellType.Empty: '.', CellType.WhiteQ: 'W', CellType.BlackQ: 'B'}
        for row in self.board:
            print(' '.join(rep[cell_t] for cell_t in row))
    
    def _cell_type_of_player(self, player: Player):
        return CellType.WhiteQ if player == Player.White else CellType.BlackQ
    
    def _get_player_pieces(self, player: Player) -> list[tuple[int, int]]:
        piece_t = self._cell_type_of_player(player)
        pieces = []
        for i in range(DIM):
            for j in range(DIM):
                if self.board[i][j] == piece_t:
                    pieces.append((i, j))
        return pieces
    
    def _get_available_moves(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        moves: list[tuple[tuple[int, int], tuple[int, int]]] = []
        for piece in self._get_player_pieces(self.cur.player):
            for move in self._get_piece_moves(piece):
                moves.append((piece, move))
        return moves
    
    def _make_move(self, move: tuple[tuple[int, int], tuple[int, int]]) -> bool:
        if move not in self._get_available_moves():
            return False
        piece, new_cell = move
        pi, pj = piece
        self.board[pi][pj] = CellType.Empty
        dj, dj = new_cell
        self.board[dj][dj] = self._cell_type_of_player(self.cur.player)

        # fetch existing state and update walk parent if exists, otherwise 
        # create new state.
        cur_walk_parent = self.cur.cur_walk_parent
        next_player = Player(-self.cur.player.value)
        self.cur = states_memo.get(self.id())
        if self.cur is None:
            self.cur = AllQueensStateNode(player=next_player, transition_move=move, parent=cur_walk_parent)
            states_memo[self.id()] = self.cur
        else:
            self.cur.cur_walk_parent = cur_walk_parent
        return True
    
    def _undo_move(self) -> bool:
        if self.cur is self.root:
            return False
        self.cur = self.cur.cur_walk_parent
        # TODO: have to reverse move, but cannot use _make_move() in its current state (side effects)
        return True
    
    def _game_over(self) -> Union[Player, None]:
        for player in Player:
            piece_t = self._cell_type_of_player(player)
            for piece in self._get_player_pieces(player):
                for dir in DIRS:
                    cnt = 1
                    check_cell = self._apply_dir(piece, dir)
                    i, j = check_cell
                    while self._cell_in_boundary(check_cell) and self.board[i][j] == piece_t:
                        cnt += 1
                        check_cell = self._apply_dir(check_cell, dir)
                        i, j = check_cell
                    if cnt >= 4:
                        return player
        return None

    # standardized api
    def actions(self) -> list[tuple[tuple[int, int], tuple[int, int]]]:
        return self._get_available_moves()

    def make(self, move: tuple[tuple[int, int], tuple[int, int]]) -> "AllQueensChess":
        if not self._make_move(move):
            raise IllegalMove
        return self

    def undo(self) -> "AllQueensChess":
        if not self._undo_move():
            raise IllegalMove
        return self

    def terminal(self) -> bool:
        return self._game_over() is not None

    def id(self):
        return self.cur.player.name + '_' + '.'.join('.'.join(col.name for col in row) for row in self.board)


def main():
    state = AllQueensChess()
    state.print()
    while not state.terminal():
        state.make(random.choice(state.actions()))
        state.print()
    print(f"{state._game_over().name} wins.")


main()
