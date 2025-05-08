
# Implicit, but Deterministic Generation of Graphs

  

## Table of Contents

- [Introduction](#introduction)

- [Getting Started](#getting-started)

- [Basic Usage](#basic-usage)

- [Parameters](#parameters)

- [Default Behavioural Functions](#default-behavioural-functions)

- [Use of Deterministic Randomness in Custom Functionality](#use-of-deterministic-randomness-in-custom-functionality)

- [API Reference](#api-reference)

- [License](#license)

  

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

  

Example of a minimax search in the graph:

  

```python

from State import State

  

INF = 1000

def  minimax(state: State, depth: int, isMaximizingPlayer: bool):

if state.is_terminal():

return state.value()

if depth == 0:

print(state.value())

return state.value()

return state.heuristic_value()

  

if isMaximizingPlayer:

maxEval = -INF

  

for action in state.actions():

state.make(action)

sEval = minimax(state, depth-1, not isMaximizingPlayer)

state.undo()

maxEval = max(maxEval, sEval)

return maxEval

else:

minEval = INF

for action in state.actions():

state.make(action)

sEval = minimax(state, depth-1, not isMaximizingPlayer)

state.undo()

minEval = min(minEval, sEval)

return minEval

  
  

  

def  main():

state = State(max_depth=10)

val = minimax(state, 5, isMaximizingPlayer=True)

print(val1)

  

```

  

# Parameters
-  **`root_value`** (`int`, default: `1`)
The true value of the root node

-  **`seed`** (`int`, default: `0`)
Determines the starting seed for the graph generator. Ensures reproducibility.

-  **`max_depth`** (`int`, default: `2^8 - 1`)
Sets the maximum depth of the graph. If `None`, the graph can grow infinitely deep.

-  **`distribution`** (`RandomnessDistribution`, default: `Dist.UNIFORM`)
Determines what distribution the random number generator follows.

-  **`retain_tree`** (`bool`, default: `False`)
Stores tree in memory, used to draw tree

-  **`branching_factor_base`** (`int`, default: `2`)
The number of child nodes each state can generate.


-  **`branching_factor_variance`** (`int`, default: `0`)
How much the branching factor can vary.
  
-  **`terminal_minimum_depth`** (`int`, default: `0`)
Defines how deep a state must be before it can be considered terminal.

-  **`child_depth_minimum`** (`int`, default: `1`)
Defines the minimum depth of a child.

  
-  **`child_depth_maximum`** (`int`, default: `1`)
Defines the maximum depth of a child.

-  **`locality `** (`float`, default: `0`)
Controls how much of the available state space can be used when generating children. A value of `0` allows use of the full space at each depth; higher values restrict generation to a smaller portion of it.

-  **`true_value_forced_ratio`** (`float`, default: `0.1`)
Controls the ratio of children that are `forced` to share the same true value as their parent state. (NOTE: this is a strict lower bound and setting this to zero breaks the integrity of true value propagation.)

-  **`true_value_similarity_chance`** (`float`, default: `0.5`)
After meeting the minimum forced match requirement, this sets the chance that a remaining child will also take on the parent’s true value (A value of `0` means only forced nodes inherit the parent’s value; `1` means all children do).

-  **`true_value_tie_chance `** (`float`, default: `0.2`)
For children not covered by `forced value` or `similarity chance`, this sets the probability of the child being assigned a draw. (NOTE: the actual expected number og draws is dependent on `true_value_forced_ratio` and `true_value_similarity_chance`)


    ![True Value Graph](./documentation_images/value_propagation.gif)


-  **`branching_function`** (`function`, default: [`default_branching_function`](#default_branching_function))
A custom function provided by the user to determine the branching factor of states.

-  **`value_function`** (`function`, default: [`default_value_function`](#default_value_function))
A custom function provided by the user to determine the true values of states.

  

-  **`child_depth_function`** (`function`, default: [`default_child_depth_function`](#default_child_depth_function))
A custom function provided by the user to determine the depth of each child.

  

-  **`transposition_space_function`** (`function`, default: [`default_transposition_space_function`](#default_transposition_space_function))
A custom function provided by the user to define the upper bound of unique states at each depth (returns a dictionary).

-  **`heuristic_value_function`** (`function`, default: [`default_heuristic_value_function`](#default_heuristic_value_function))
A custom function provided by the user to determine the heuristic values of states.

  
  

# Default Behavioural Functions

Passing in functions as parameters allows the user to gain fine-grained control over the structure of the generated graph. Most of the behavioural functions passed in, must have the following parameters (unless parameters are explicitly stated):

-  **Parameters:**
	-  `randint` ([`RandomIntFunction`](#use-of-deterministic-randomness-in-custom-functionality)): A callable that returns random integers given a range and distribution.

	-  `randf` ([`RandomFloatFunction`](#use-of-deterministic-randomness-in-custom-functionality)): A callable that returns random floats given a range and distribution.

	-  `params` (`StateParams`): A container holding global and local state information, including depth and branching settings.

  
  
  
  

### `default_branching_function()`
-  **Return Type : `int`**

-  **Description:** Uses the `randf` function to add random variance (bounded by `branching_factor_variance`) to the `base_branching_factor` and returns this value.

  

---

  
  

### `default_value_function()`

-  **Return Type : `int`**

-  **Description:** Uses the `randint` function to uniformly sample an integer between -1 and 1 and returns that value.

---

### `default_child_depth_function()`

-  **Return Type : `int`**

-  **Description:** Uses the `randint` to randomly generate a depth between minimum and maximum depth and returns that value.

---

### `default_transposition_space_function()`

-  **Parameters:**

	-  `randint` (`RandomIntFunction`): A callable that returns random integers given a range and distribution.

	-  `randf` (`RandomFloatFunction`): A callable that returns random floats, used to introduce branching variance.

	-  `globals` (`GlobalVariables`): A container holding global state information

	-  `depth` (`int`): A container holding global state information

-  **Return Type : `int`**

-  **Description:** Uses `globals` to return the maximum number of different states per depth, ensuring minimal transpositions.
---

### `default_heuristic_value_function()`

-  **Parameters:**

	-  `randint` (`RandomIntFunction`): A callable that returns random integers given a range and distribution.

	-  `randf` (`RandomFloatFunction`): A callable that returns random floats, used to introduce branching variance.

	-  `params` (`StateParams`): A container holding global and local state information, including depth and branching settings.

	-  `value` (`int`): The true value of the current state

-  **Return Type : `int`**

-  **Description:** Simulates a heuristic function with 70%-85% accuracy depending on depth.

  

# Use of Deterministic Randomness in Custom Functionality

  

Each state in the graph has access to a deterministic random number generator. This allows user-defined functions to behave consistently across runs. The random generators are exposed through two helper functions:


### `RandomIntFunction` and `RandomFloatFunction`


**Return Values:**
-  `RandomIntFunction`: `int`
-  `RandomFloatFunction`: `float`

Both functions sample a number between `low` and `high`, following the specified `distribution`.

If no distribution is provided, the default distribution set during initialization is used (typically uniform).

  

-  **Parameters:**

	-  `low`: The minimum value to sample from (`int` for `RandomIntFunction`, `float` for `RandomFloatFunction`).

	-  `high`: The maximum value to sample from (`int` for `RandomIntFunction`, `float` for `RandomFloatFunction`).

	-  `distribution` (`RandomnessDistribution`): Optional. Specifies the distribution to use when sampling.

  

**Example Usage:**

Graph where each state has a uniform branching factor between 0 and 3

```python

  

def  uniform3_branching_function(randint: RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:

return randint(low=0, high=3, distribution=RandomnessDistribution.UNIFORM)

  

state = State(branching_function=uniform3_branching_function)

  

```


# API Reference

| Method              | Description                                                                 | Arguments                                   |
|---------------------|-----------------------------------------------------------------------------|---------------------------------------------|
| `id()`              | Returns the ID of the current state.                                        | None                                        |
| `is_terminal()`     | Returns `True` if the current state is terminal (a leaf node), else `False`. | None                                        |
| `is_root()`         | Returns `True` if the current state is the root of the graph, else `False`. | None                                        |
| `value()`           | Returns the true (actual) value of the current state.                       | None                                        |
| `heuristic_value()` | Returns the heuristic estimate of the state's value.                        | None                                        |
| `actions()`         | Returns a list of integers representing available actions from this state.  | None                                        |
| `make(action)`      | Transitions the current state by applying the specified action.             | `action` (int): The action to apply.       |
| `make_random()`     | Randomly applies one of the available actions.                              | None                                        |
| `undo()`            | Undoes the last action taken.                                               | None                                        |
| `draw()`            | Visualizes the current state and its immediate children.                    | None                                        |

  

# License

  

  

GPL3 ?