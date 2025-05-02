# Implicit, but Deterministic Generation of Graphs

  

# Introduction

  

This API allows users to generate variety of state-space graphs. The tool allows the user to use simple predefined graphs, or to fine-tune the graph by using user-defined function passing. Using Hashing and a starting seed, reproducability is ensured for each graph. This tool supports user control over branching factor, depth, values of states, heuristic values of states, cycles and transpositions among other features.

  

An accompanying research paper can be found [here](www.example.org).

  

# Getting Started

First, you install it:

....

  

# Basic Usage

Initialize a new state-space graph by using the `State` constructor.

```python

state = State()

  ```

This creates a simple graph, with default values for each parameter. This default graph is a binary tree, with no maximum depth, no state values and no transpositions or cycles.


## Parameters
- **`root_value`** (`int`, default: `1`)  
  The true value of the root node
  
- **`seed`** (`int`, default: `0`)  
  Determines the starting seed for the graph generator. Ensures reproducibility.

- **`max_depth`** (`int`, default: `2^8 - 1`)  
  Sets the maximum depth of the graph. If `None`, the graph can grow infinitely deep.

- **`distribution`** (`RandomnessDistribution`, default: `Dist.UNIFORM`)  
Determines what distribution the random number generator follows.

- **`retain_tree`** (`bool`, default: `False`)  
Stores tree in memory, used to draw tree

- **`branching_factor_base`** (`int`, default: `2`)  
  The number of child nodes each state can generate.

- **`branching_factor_variance`** (`int`, default: `0`)  
  How much the branching factor can vary.

- **`terminal_minimum_depth`** (`int`, default: `0`)  
Defines how deep a state must be before it can be considered terminal.

Need to change stuff below

- **`value_fn`** (`function`, default: `None`)  
  A custom function provided by the user to assign true values to states.

- **`heuristic_fn`** (`function`, default: `None`)  
  A custom function for estimating heuristic values of states.

- **`allow_cycles`** (`bool`, default: `False`)  
  Whether to allow cycles in the graph (i.e., paths that return to a previously visited state).

- **`allow_transpositions`** (`bool`, default: `False`)  
  Whether different action paths can lead to the same state, simulating transpositions.
  
 
  
  

# Examples

  Hello
  

# API Reference



| Method            | Description                                                                 | Arguments                                           |
|-------------------|-----------------------------------------------------------------------------|-----------------------------------------------------|
| `id()`            | Returns the ID of the current state.                                        | None                                                |
| `is_terminal()`   | Returns `True` if the current state is terminal (a leaf node), else `False`. | None                                                |
| `is_root()`       | Returns `True` if the current state is the root of the graph, else `False`. | None                                                |
| `value()`         | Returns the true (actual) value of the current state.                        | None                                                |
| `heuristic_value()` | Returns the heuristic estimate of the state's value.                      | None                                                |
| `actions()`       | Returns a list of integers representing available actions from this state.  | None                                                |
| `make(action)`    | Transitions the current state by applying the specified action.              | `action` (int): The action to apply.               |
| `make_random()`   | Randomly applies one of the available actions.                              | None                                                |
| `undo()`          | Undoes the last action taken.                                                | None                                                |
| `draw()`          | Visualizes the current state and its immediate children. |None 
  


  
  

# License

  

GPL3 ?