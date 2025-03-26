from enum import Enum
from copy import copy
from typing import Literal
from collections import defaultdict

class Player(Enum):
    O = 1
    X = 2

class Cell(Enum):
    E = 0
    O = Player.O.value
    X = Player.X.value


def all_same(ls: list[Cell]) -> bool:
    return all(cell == ls[0] and cell != Cell.E for cell in ls)


class Node:
    def __init__(self, player: Player, depth: int, transposition_number: int, state: list[Cell]|None=None):
        if state is None:
            self.state: list[Cell] = [Cell.E] * 9
        else:
            self.state = state
        self.player: Player = player
        self.depth = depth
        self.children: list[Node] = []
        self.transposition_number = transposition_number
    
    def draw(self):
        out: str = ""
        for i in range(3):
            out += ' '.join(cell.name for cell in self.state[i*3:i*3+3]) + '\n'
        print(out)
    
    def generate_children(self):
        for i, cell in enumerate(self.state):
            if cell == Cell.E:
                new_state = copy(self.state)
                new_state[i] = Cell(self.player.value)
                node = Node(
                    player=self._other_player(), 
                    depth=self.depth+1, 
                    transposition_number=self.transposition_number, 
                    state=new_state
                )
                self.children.append(node)
                
                
    def _other_player(self) -> Literal[Player.O] | Literal[Player.X]:
        return Player.O if self.player == Player.X else Player.X
    
    def game_over(self) -> None | Literal[True]:
        for i in range(3):
            if all_same(self.state[i*3: i*3+3]):
                return True
            if all_same([self.state[i], self.state[i+3], self.state[i+6]]):
                return True
        if all_same([self.state[0], self.state[4], self.state[8]]):
            return True
        if all_same([self.state[2], self.state[4], self.state[6]]):
            return True


def hash_node(node: Node) -> int:
    return hash(str(node.state))


nodes_memo: dict[int, Node] = dict()

def BFS(root: Node):
    bfs_queue = [root]
    while bfs_queue:
        node = bfs_queue.pop(0)
        node_hash = hash_node(node)
        node_memo = nodes_memo.get(node_hash)
        if node_memo is not None:
            node_memo.transposition_number += node.transposition_number
            pass
        else: nodes_memo[node_hash] = node
        if node.game_over():
            continue
        node.generate_children()
        bfs_queue += node.children

root = Node(player=Player.X, depth=0, transposition_number=1) 
BFS(root)


depth_sorted_nodes: list[list[Node]] = [[] for _ in range(10)]
for node in nodes_memo.values():
    depth_sorted_nodes[node.depth].append(node)

bf_by_depth_unique = [[0] * 10 for _ in range(10)]
bf_by_depth_nonunique = [[0] * 10 for _ in range(10)]
for depth, nodes  in enumerate(depth_sorted_nodes):
    for node in nodes:
        bf_by_depth_unique[depth][len(node.children)] += 1
        bf_by_depth_nonunique[depth][len(node.children)] += node.transposition_number


print("###############################################")
print("branching factor by depth")
print()
print("unique:")
for depth, cnt in enumerate(bf_by_depth_unique):
    print(depth, cnt)
print()
print("non-unique:")
for depth, cnt in enumerate(bf_by_depth_nonunique):
    print(depth, cnt)

print()
print("###############################################")
print("terminal state density by depth")
print()
print("unique:")
for depth, cnt in enumerate(bf_by_depth_unique):
    try:
        ratio = cnt[0] / sum(cnt[1:])
    except ZeroDivisionError:
        ratio = 1
    print(depth, float(ratio))
print()
print("non-unique:")
for depth, cnt in enumerate(bf_by_depth_nonunique):
    try:
        ratio = cnt[0] / sum(cnt[1:])
    except ZeroDivisionError:
        ratio = 1
    print(depth, float(ratio))


print()
print("###############################################")
print("average game length")
total = 0
terminals_cnt = 0
for nodes in depth_sorted_nodes:
    for node in nodes:
        if node.game_over():
            total += node.depth
            terminals_cnt += 1
print()
print("unique:", total / terminals_cnt)
total = 0
terminals_cnt = 0
for nodes in depth_sorted_nodes:
    for node in nodes:
        if node.game_over():
            total += node.depth * node.transposition_number
            terminals_cnt += node.transposition_number
print("non-unique:", total / terminals_cnt)


print()
print("###############################################")
print("transposition density by depth")

transposition_density_by_depth: list[defaultdict[int, int]] = [defaultdict(lambda: 0) for _ in range(10)]
for depth, nodes  in enumerate(depth_sorted_nodes):
    for node in nodes:
        transposition_density_by_depth[depth][node.transposition_number] += 1

for depth, d in enumerate(transposition_density_by_depth):
    print(depth, ', '.join(f"{d[k]:>4} states with {k:>4} transpositions" for k in d))