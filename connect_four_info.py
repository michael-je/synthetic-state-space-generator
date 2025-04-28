import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from collections import deque
from collections import defaultdict
from typing import List, DefaultDict
from graphviz import Digraph

def simulate():
    def simulate_column_fill(num_columns=7, column_height=6, num_simulations=30000):
        fill_times = np.zeros((num_simulations, num_columns), dtype=int)

        for sim in range(num_simulations):
            heights = np.zeros(num_columns, dtype=int)
            full_at = np.zeros(num_columns, dtype=int)
            toss = 0
            filled = set()

            while len(filled) < num_columns:
                toss += 1
                non_full = np.where(heights < column_height)[0]
                choice = np.random.choice(non_full)
                heights[choice] += 1
                if heights[choice] == column_height:
                    filled.add(choice)
                    full_at[len(filled) - 1] = toss

            fill_times[sim] = full_at

        expected_fill_tosses = fill_times.mean(axis=0)
        
        # Convert to DataFrame
        results_df = pd.DataFrame({
            "Columns Filled": np.arange(1, num_columns + 1),
            "Expected Toss Number": expected_fill_tosses
        })

        return results_df

    # Run the simulation
    df = simulate_column_fill()

    # Display result
    print(df)

    # Optional: plot the results
    plt.figure(figsize=(8, 5))
    plt.plot(df["Columns Filled"], df["Expected Toss Number"], marker='o')
    plt.title("Expected Toss Number to Fill k Columns")
    plt.xlabel("Number of Columns Filled")
    plt.ylabel("Expected Toss Number")
    plt.grid(True)
    plt.tight_layout()
    plt.show()



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
            self.state: list[Cell] = [Cell.E] * 42        
        else:
            self.state = state
        self.player: Player = player
        self.depth = depth
        self.children: list[Node] = []
        self.transposition_number = transposition_number
        self.winner: Player | None = None
    
    def draw(self):
        out: str = ""
        for i in range(6):
            out += ' '.join(cell.name for cell in self.state[i*7:i*7+7]) + '\n'
        print(out)
    
    def generate_children(self):
        for col in range(7):
            for row in reversed(range(6)):
                idx = row * 7 + col
                if self.state[idx] == Cell.E:
                    new_state = copy(self.state)
                    new_state[idx] = Cell(self.player.value)
                    node = Node(
                        player=self._other_player(), 
                        depth=self.depth + 1, 
                        transposition_number=self.transposition_number, 
                        state=new_state
                    )
                    self.children.append(node)
                    break  # Only one move per column

    
    def _same_cells(self, ls: list[Cell]) -> Cell | None:
        if all(cell == ls[0] for cell in ls) and ls[0] != Cell.E:
            return ls[0]
        else:
            return None
    
    def check_set_winner(self) -> Player | None:
        def get_cell(row: int, col: int) -> Cell | None:
            if 0 <= row < 6 and 0 <= col < 7:
                return self.state[row * 7 + col]
            return None

        directions = [
            (0, 1),   # horizontal →
            (1, 0),   # vertical ↓
            (1, 1),   # diagonal ↘
            (1, -1),  # diagonal ↙
        ]

        for row in range(6):
            for col in range(7):
                base_cell = get_cell(row, col)
                if base_cell == Cell.E:
                    continue

                for dr, dc in directions:
                    sequence = [
                        get_cell(row + i * dr, col + i * dc)
                        for i in range(4)
                    ]
                    if sequence.count(base_cell) == 4:
                        self.winner = Player(base_cell.value)
                        return self.winner

        self.winner = None
        return None


    def _other_player(self) -> Literal[Player.O] | Literal[Player.X]:
        return Player.O if self.player == Player.X else Player.X
    
    def game_over(self) -> bool:
        if self.winner is not None:
            return True
        return self.check_set_winner() is not None

    def __hash__(self) -> int:
        return hash(tuple(self.state))
    
    def __eq__(self, other):
        return isinstance(other, Node) and self.state == other.state


nodes_memo: dict[int, Node] = dict()


def BFS(root: Node):
    bfs_queue = deque([root])
    while bfs_queue:
        node = bfs_queue.popleft()
        node_hash = hash(node)
        node_memo = nodes_memo.get(node_hash)
        if node_memo is not None:
            node_memo.transposition_number += node.transposition_number
            pass
        else: nodes_memo[node_hash] = node
        if node.game_over():
            continue
        node.generate_children()
        bfs_queue.extend(node.children)


def create_node_from_board(board_2d: list[list[str]]) -> Node:
    symbol_to_cell = {'.': Cell.E, 'X': Cell.X, 'O': Cell.O}
    flat_board = [symbol_to_cell[ch] for row in board_2d for ch in row]
    x_count = flat_board.count(Cell.X)
    o_count = flat_board.count(Cell.O)
    next_player = Player.X if x_count == o_count else Player.O
    return Node(player=next_player, depth=x_count + o_count, transposition_number=1, state=flat_board)

# === Define a custom 22-move board ===
board_1 = [
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', 'X', 'O', 'X', '.', '.'],
    ['.', 'O', 'X', 'O', 'O', '.', '.'],
    ['X', 'X', 'O', 'X', 'X', 'O', '.'],
    ['O', 'O', 'X', 'X', 'O', 'X', '.'],
]

board_2 = [
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
]

board_3 = [
    ['.', '.', '.', '.', '.', '.', '.'],
    ['.', '.', '.', '.', '.', '.', '.'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
    ['X', 'O', 'X', 'O', 'X', 'O', 'X'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
]

board_4 = [
    ['.', '.', '.', '.', '.', '.', '.'],
    ['O', 'X', 'O', '.', '.', 'X', '.'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
    ['X', 'O', 'X', 'O', 'X', 'O', 'X'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
    ['O', 'X', 'O', 'X', 'O', 'X', 'O'],
]



root = create_node_from_board(board_4)


print("Starting board (22 turns in):")
root.draw()
print(f"Next player to move: {root.player.name}")
print(f"Is game over? {root.game_over()}")
################ Calculations #####################


BFS(root)



max_depth = max(node.depth for node in nodes_memo.values())
start_depth = root.depth
depth_sorted_nodes: list[list[Node]] = [[] for _ in range(max_depth + 1)]

for node in nodes_memo.values():
    depth_sorted_nodes[node.depth].append(node)



print("###############################################")
print("branching factor by depth")
max_children = max(len(node.children) for node in nodes_memo.values())

bf_by_depth_unique = [[0] * (max_children + 1) for _ in range(max_depth + 1)]
bf_by_depth_nonunique = [[0] * (max_children + 1) for _ in range(max_depth + 1)]

for depth in range(start_depth, max_depth + 1):
    for node in depth_sorted_nodes[depth]:
        bf_by_depth_unique[depth][len(node.children)] += 1
        bf_by_depth_nonunique[depth][len(node.children)] += node.transposition_number

print("\nunique:")
for depth in range(start_depth, max_depth + 1):
    print(depth, bf_by_depth_unique[depth])

print("\nnon-unique:")
for depth in range(start_depth, max_depth + 1):
    print(depth, bf_by_depth_nonunique[depth])


print()
print("\n###############################################")
print("terminal state density by depth")

print("\nunique:")
for depth in range(start_depth, max_depth + 1):
    stats = bf_by_depth_unique[depth]
    try:
        ratio = stats[0] / sum(stats[1:])
    except ZeroDivisionError:
        ratio = 1
    print(depth, float(ratio))

print("\nnon-unique:")
for depth in range(start_depth, max_depth + 1):
    stats = bf_by_depth_nonunique[depth]
    try:
        ratio = stats[0] / sum(stats[1:])
    except ZeroDivisionError:
        ratio = 1
    print(depth, float(ratio))

print("\n###############################################")
print("average game length")

# Unique
total = 0
terminals_cnt = 0
for depth in range(start_depth, max_depth + 1):
    for node in depth_sorted_nodes[depth]:
        if node.game_over():
            total += node.depth
            terminals_cnt += 1
print("\nunique:", total / terminals_cnt)

# Non-unique
total = 0
terminals_cnt = 0
for depth in range(start_depth, max_depth + 1):
    for node in depth_sorted_nodes[depth]:
        if node.game_over():
            total += node.depth * node.transposition_number
            terminals_cnt += node.transposition_number
print("non-unique:", total / terminals_cnt)

print("\n###############################################")
print("transposition density by depth")
transposition_density_by_depth: List[DefaultDict[int, int]] = [defaultdict(int) for _ in range(max_depth + 1)]

for depth in range(start_depth, max_depth + 1):
    for node in depth_sorted_nodes[depth]:
        transposition_density_by_depth[depth][node.transposition_number] += 1

for depth in range(start_depth, max_depth + 1):
    d = transposition_density_by_depth[depth]
    print(depth, ', '.join(f"{d[k]:>4} states with {k:>4} transpositions" for k in sorted(d)))

print("\n###############################################")
print("outcome distribution by depth")

outcomes_by_depth_unique: list[tuple[int, int, int]] = []
outcomes_by_depth_nonunique: list[tuple[int, int, int]] = []

for depth in range(start_depth, max_depth + 1):
    nodes = depth_sorted_nodes[depth]
    outcomes_by_depth_unique.append((
        sum(1 for node in nodes if node.winner == Player.X),
        sum(1 for node in nodes if node.winner == Player.O),
        sum(1 for node in nodes if node.winner is None),
    ))
    outcomes_by_depth_nonunique.append((
        sum(node.transposition_number for node in nodes if node.winner == Player.X),
        sum(node.transposition_number for node in nodes if node.winner == Player.O),
        sum(node.transposition_number for node in nodes if node.winner is None),
    ))

print("\nunique:")
for i, stats in enumerate(outcomes_by_depth_unique):
    depth = start_depth + i
    total = sum(stats)
    if total == 0:
        print(depth, "No terminal states")
    else:
        print(depth, f"X: {stats[0]:<6} ({100*stats[0]/total:6.2f}%), "
                     f"O: {stats[1]:<6} ({100*stats[1]/total:6.2f}%), "
                     f"Tie: {stats[2]:<6} ({100*stats[2]/total:6.2f}%)")

print("\nnon-unique:")
for i, stats in enumerate(outcomes_by_depth_nonunique):
    depth = start_depth + i
    total = sum(stats)
    if total == 0:
        print(depth, "No terminal states")
    else:
        print(depth, f"X: {stats[0]:<6} ({100*stats[0]/total:6.2f}%), "
                     f"O: {stats[1]:<6} ({100*stats[1]/total:6.2f}%), "
                     f"Tie: {stats[2]:<6} ({100*stats[2]/total:6.2f}%)")





def generate_dot_graph(root: Node, max_nodes=1000):
    dot = Digraph()
    queue = deque([(root, None)])
    count = 0

    while queue and count < max_nodes:
        node, parent_id = queue.popleft()
        node_id = str(id(node))
        label = f"D{node.depth}\n{'X' if node.player == Player.X else 'O'}"
        dot.node(node_id, label)
        if parent_id:
            dot.edge(parent_id, node_id)

        for child in node.children:
            queue.append((child, node_id))

        count += 1

    return dot

# Usage:
dot = generate_dot_graph(root, max_nodes=3000)
dot.render("gametree", format="png", cleanup=True)








# Create filtered DataFrame starting at start_depth
depths = list(range(start_depth, len(bf_by_depth_unique)))
bf_df = pd.DataFrame(bf_by_depth_unique[start_depth:], columns=[f'{i} children' for i in range(len(bf_by_depth_unique[0]))])
bf_df['Depth'] = depths
bf_df = bf_df.set_index('Depth')

################################################3
# Plot branching factor
bf_df.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title("Branching Factor by Depth (Unique States)")
plt.xlabel("Depth")
plt.ylabel("Number of States")
plt.legend(title="Children")
plt.grid(True)
plt.tight_layout()
plt.show()


bf_df_nonunique = pd.DataFrame(
    bf_by_depth_nonunique[start_depth:],
    columns=[f'{i} children' for i in range(len(bf_by_depth_nonunique[0]))]
)
bf_df_nonunique['Depth'] = depths
bf_df_nonunique.set_index('Depth').plot(
    kind='bar', stacked=True, figsize=(10, 6), title="Branching Factor by Depth (Non-Unique States)"
)
plt.xlabel("Depth")
plt.ylabel("Number of States (Weighted by Transpositions)")
plt.grid(True)
plt.tight_layout()
plt.show()


# === 2. Terminal State Density ===
# === Compute terminal state densities from branching factors ===
terminal_state_density_unique = []
terminal_state_density_nonunique = []

for depth in range(start_depth, max_depth + 1):
    unique_stats = bf_by_depth_unique[depth]
    nonunique_stats = bf_by_depth_nonunique[depth]

    try:
        unique_ratio = unique_stats[0] / sum(unique_stats[1:])
    except ZeroDivisionError:
        unique_ratio = 1.0
    terminal_state_density_unique.append(unique_ratio)

    try:
        nonunique_ratio = nonunique_stats[0] / sum(nonunique_stats[1:])
    except ZeroDivisionError:
        nonunique_ratio = 1.0
    terminal_state_density_nonunique.append(nonunique_ratio)

# Prepare depth list
depths = list(range(start_depth, max_depth + 1))

# === Plot Terminal State Density ===
plt.figure(figsize=(8, 5))
plt.plot(depths, terminal_state_density_unique, marker='o', label="Unique")
plt.plot(depths, terminal_state_density_nonunique, marker='x', label="Non-Unique")
plt.title("Terminal State Density by Depth")
plt.xlabel("Depth")
plt.ylabel("Terminal / Non-Terminal Ratio")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === 4. Transposition Density by Depth ===
plt.figure(figsize=(10, 6))
for k in sorted({k for d in transposition_density_by_depth[start_depth:] for k in d}):
    values = [d.get(k, 0) for d in transposition_density_by_depth[start_depth:]]
    plt.plot(depths, values, marker='o', label=f'{k} transpositions')
plt.title("Transposition Density by Depth")
plt.xlabel("Depth")
plt.ylabel("Number of States")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# === 5. Outcome Distribution ===
# Unique
outcomes_df_unique = pd.DataFrame(outcomes_by_depth_unique[start_depth:], columns=["X Wins", "O Wins", "Ties"], index=depths)
outcomes_df_unique.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title("Outcome Distribution by Depth (Unique States)")
plt.xlabel("Depth")
plt.ylabel("Number of Outcomes")
plt.grid(True)
plt.tight_layout()
plt.show()

# Non-unique
outcomes_df_nonunique = pd.DataFrame(outcomes_by_depth_nonunique[start_depth:], columns=["X Wins", "O Wins", "Ties"], index=depths)
outcomes_df_nonunique.plot(kind='bar', stacked=True, figsize=(10, 6))
plt.title("Outcome Distribution by Depth (Non-Unique States)")
plt.xlabel("Depth")
plt.ylabel("Number of Outcomes (Weighted by Transpositions)")
plt.grid(True)
plt.tight_layout()
plt.show()
