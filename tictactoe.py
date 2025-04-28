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
        self.winner: Player | None = None
    
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
    
    def _same_cells(self, ls: list[Cell]) -> Cell | None:
        if all(cell == ls[0] for cell in ls) and ls[0] != Cell.E:
            return ls[0]
        else:
            return None
    
    def check_set_winner(self) -> Player | None:
        for i in range(3):
            if cells := self._same_cells(self.state[i*3: i*3+3]):
                self.winner = Player(cells.value)
                return self.winner
            if cells := self._same_cells([self.state[i], self.state[i+3], self.state[i+6]]):
                self.winner = Player(cells.value)
                return self.winner
        if cells := self._same_cells([self.state[0], self.state[4], self.state[8]]):
            self.winner = Player(cells.value)
            return self.winner
        if cells := self._same_cells([self.state[2], self.state[4], self.state[6]]):
            self.winner = Player(cells.value)
            return self.winner
        return self.winner

    def _other_player(self) -> Literal[Player.O] | Literal[Player.X]:
        return Player.O if self.player == Player.X else Player.X
    
    def game_over(self) -> bool:
        return self.check_set_winner() is not None

    def __hash__(self) -> int:
        return hash(str(self.state))


nodes_memo: dict[int, Node] = dict()

def BFS(root: Node):
    bfs_queue = [root]
    while bfs_queue:
        node = bfs_queue.pop(0)
        node_hash = hash(node)
        node_memo = nodes_memo.get(node_hash)
        if node_memo is not None:
            node_memo.transposition_number += node.transposition_number
            pass
        else: nodes_memo[node_hash] = node
        if node.game_over():
            continue
        node.generate_children()
        bfs_queue += node.children


################ Calculations #####################

root = Node(player=Player.X, depth=0, transposition_number=1) 
BFS(root)

depth_sorted_nodes: list[list[Node]] = [[] for _ in range(10)]
for node in nodes_memo.values():
    depth_sorted_nodes[node.depth].append(node)


print("###############################################")
print("branching factor by depth")
bf_by_depth_unique = [[0] * 10 for _ in range(10)]
bf_by_depth_nonunique = [[0] * 10 for _ in range(10)]
for depth, nodes  in enumerate(depth_sorted_nodes):
    for node in nodes:
        bf_by_depth_unique[depth][len(node.children)] += 1
        bf_by_depth_nonunique[depth][len(node.children)] += node.transposition_number
print()
print("unique:")
for depth, stats in enumerate(bf_by_depth_unique):
    print(depth, stats)
print()
print("non-unique:")
for depth, stats in enumerate(bf_by_depth_nonunique):
    print(depth, stats)


import matplotlib.pyplot as plt
import numpy as np
def plot_bf_by_depth(data, title, ylabel):
    data_np = np.array(data)
    depths = np.arange(data_np.shape[0])

    fig, ax = plt.subplots(figsize=(14, 8))

    bottom = np.zeros_like(depths)
    colors = plt.cm.tab10(np.linspace(0, 1, data_np.shape[1]))  # Professional colors (10 distinct ones)

    for bf in range(data_np.shape[1]):
        bars = ax.bar(depths, data_np[:, bf], bottom=bottom, color=colors[bf], label=f'BF {bf}')
        # Add labels inside bars
        for bar, value in zip(bars, data_np[:, bf]):
            if value > 0:
                ax.text(
                    bar.get_x() + bar.get_width() / 2,  # center of bar
                    bar.get_y() + bar.get_height() / 2,  # center vertically
                    f'{bf}',
                    ha='center', va='center',
                    fontsize=8,
                    color='white' if value > 10 else 'black'  # make sure text is visible
                )
        bottom += data_np[:, bf]

    ax.set_xlabel('Depth')
    ax.set_ylabel(ylabel)
    ax.set_yscale('log')  # <-- Logarithmic y-axis
    ax.set_title(title)
    ax.legend(title='Branching Factor', bbox_to_anchor=(1.05, 1), loc='upper left')
    ax.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.show()

# Plot unique
plot_bf_by_depth(
    bf_by_depth_unique,
    title='Branching Factor Distribution by Depth in Tic-Tac-Toe',
    ylabel='Number of States (log scale)'
)

plot_bf_by_depth(
    bf_by_depth_nonunique,
    title='Branching Factor Distribution by Depth (Non-Unique)',
    ylabel='Number of States Weighted by Transpositions (log scale)'
)

print()
print("###############################################")
print("terminal state density by depth")
print()
print("unique:")
for depth, stats in enumerate(bf_by_depth_unique):
    try:
        ratio = stats[0] / sum(stats[1:])
    except ZeroDivisionError:
        ratio = 1
    print(depth, float(ratio))
print()
print("non-unique:")
for depth, stats in enumerate(bf_by_depth_nonunique):
    try:
        ratio = stats[0] / sum(stats[1:])
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


print()
print("###############################################")
print("outcome distribution by depth")

outcomes_by_depth_unique: list[tuple[int, int, int]] = []
outcomes_by_depth_nonunique: list[tuple[int, int, int]] = []
for nodes  in depth_sorted_nodes:
    outcomes_by_depth_unique.append((
        sum(1 for node in nodes if node.winner == Player.X),
        sum(1 for node in nodes if node.winner == Player.O),
        sum(1 for node in nodes if node.winner == None)
    ))
    outcomes_by_depth_nonunique.append((
        sum(node.transposition_number for node in nodes if node.winner == Player.X),
        sum(node.transposition_number for node in nodes if node.winner == Player.O),
        sum(node.transposition_number for node in nodes if node.winner == None)
    ))
print()
print("unique:")
for depth, stats in enumerate(outcomes_by_depth_unique):
    total = sum(stats)
    print(depth, f"X: {stats[0]:<6} ({100*stats[0]/total:6.2f}%), O: {stats[1]:<6} ({100*stats[1]/total:6.2f}%), Tie: {stats[2]:<6} ({100*stats[2]/total:6.2f}%)")
print()
print("non-unique:")
for depth, stats in enumerate(outcomes_by_depth_nonunique):
    total = sum(stats)
    print(depth, f"X: {stats[0]:<6} ({100*stats[0]/total:6.2f}%), O: {stats[1]:<6} ({100*stats[1]/total:6.2f}%), Tie: {stats[2]:<6} ({100*stats[2]/total:6.2f}%)")
