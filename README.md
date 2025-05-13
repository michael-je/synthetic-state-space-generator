
# Synthetic State Space Generator

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
// TODO: michael when api is ready

# Basic Usage
Initialize a new state-space graph by using the `State` constructor.
```python
state = State()
```
This creates a simple graph, with default values for each parameter. This default graph is a binary tree, with no maximum depth, no state values and no transpositions or cycles.

// TODO: add a few (1-3) short examples (max 10 lines each)
  
// TODO: move this code to new chapter "code examples"
<a name="minimax-search"></a>
Example of a minimax search in the graph:
```python
from State import State
from custom_types import Player

INF = 1000
visited: dict[int, int] = {}
def minimax(state: State, depth: int) -> int:
	if state.id() in visited.keys():
		return state.true_value()
	if state.is_terminal():
		return state.true_value()
	if depth == 0:
		return state.heuristic_value()
	
	if state.player() == Player.MAX:
		max_eval = -INF
		for action in state.actions():
			state.make(action)
			s_eval = minimax(state, depth-1)
			state.undo()
			max_eval = max(max_eval, s_eval)
		visited[state.id()] = max_eval
		return max_eval
	else:
		min_eval = INF
		for action in state.actions():
			state.make(action)
			s_eval = minimax(state, depth-1)
			state.undo()
			min_eval = min(min_eval, s_eval)			
		visited[state.id()] = min_eval
		return min_eval

def main():
	state = State(max_depth=9)
	val = minimax(state, 9)
	print(f"Minimax Value: {val}")
	print(f"True value: {state.true_value()}")

main()
```

<a name="parameters"></a>
# Parameters

-  **`seed`** (`int`, default: `0`, range: `Positive Integer`)
Determines the starting seed for the graph generator. Ensures reproducibility.

-  **`max_depth`** (`int`, default: `2^8 - 1`)
Sets the maximum depth of the graph.

-  **`distribution`** ([`RandomnessDistribution`](#RandomnessDistribution), default: `Dist.UNIFORM`, option: `Uniform` or `Gaussian`)Determines what distribution the random number generator follows.

-  **`root_value`** (`int`, default: `0`, Allowed Values: `-1`, `0`, `1`)
The true value of the root node

-  **`retain_tree`** (`bool`, default: `False`)
Stores tree in memory, used to draw tree

-  **`branching_factor_base`** (`int`, default: `2`, range: `Positive Integers`)
The number of child nodes each state can generate. // TODO: improve

-  **`branching_factor_variance`** (`int`, default: `0`, range: `Positive Integer`)
How much the branching factor can vary. // TODO: improve
  
-  **`terminal_minimum_depth`** (`int`, default: `0`, range: `Positive Integer`)
Defines how deep a state must be before it can be considered terminal. // TODO: improve

-  **`child_depth_minimum`** (`int`, default: `1`)
Defines the minimum depth of a child relative to its parent.
  
-  **`child_depth_maximum`** (`int`, default: `1`)
Defines the maximum depth of a child relative to its parent.

-  **`locality `** (`float`, default: `0`, range: `[0, 1]`)
Controls how much of the available state space can be used when generating children. A value of `0` allows use of the full space at each depth; higher values restrict generation to a smaller portion centered around the parent node.

<a name="true-value-parameters"></a>

-  **`true_value_forced_ratio`** (`float`, default: `0.1`, range: `[0, 1]`)
Controls the ratio of children that are `forced` to share the same true value as their parent state. (NOTE: this is a strict lower bound and setting this to zero breaks the integrity of true value propagation.)

-  **`true_value_similarity_chance`** (`float`, default: `0.5`, range: `[0, 1]`)
After meeting the minimum forced match requirement, this sets the chance that a remaining child will also take on the parent’s true value (A value of `0` means only forced nodes inherit the parent’s value; `1` means all children do).

-  **`true_value_tie_chance `** (`float`, default: `0.2`, range: `[0, 1]`)
For children not covered by `forced value` or `similarity chance`, this sets the probability of the child being assigned a draw. (NOTE: the actual expected number og draws is dependent on `true_value_forced_ratio` and `true_value_similarity_chance`)

    ![True Value Graph](./documentation_images/value_propagation.gif)
	// TODO: fix "_ratio" -> "_chance"
	// TODO: put somewhere else and link to it, shouldn't be in the middle of this list

-  **`symmetry_factor`** (`float`, default: `1.0`, range: `[0, 1]`)
// TODO: description

-  **`symmetry_frequency`** (`float`, default: `0.0`, range: `[0, 1]`)
// TODO: description

-  **`heuristic_accuracy_base`** (`float`, default: `0.7`, range: `[0, 1]`)
// TODO: description

-  **`heuristic_depth_scaling`** (`float`, default: `0.5`, range: `[0, 1]`)
// TODO: description

-  **`heuristic_locality_scaling`** (`float`, default: `0.5`, range: `[0, 1]`)
// TODO: description


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

Certain functionality is controlled by what we call "behavioral functions". These functions are used to generate certain values based on other currently observed values in the graph. For example, deciding on the branching factor of a state given its depth. We provide sane defaults which can be found in [default_functions.py](default_functions.py).

However, since these rules can vary so wildly between different kinds of graphs, we allow user-defined functions to be passed to the API during initialization. We recommend having a look at the default functions, as well as the [example functions](example_functions.py), to get a better idea of how to construct your own. 

Following is a list of the available functions. They all accept the arguments listed directly below, unless explicitely stated otherwise: 
-  **Parameters:**
	-  `randint` ([`RandomIntFunction`](#use-of-deterministic-randomness-in-custom-functionality)): A callable that returns random integers within an inclusive range between `low` and `high`. Optionally, a [`RandomnessDistribution`](#RandomnessDistribution) enum can be passed using the `distribution` keyword argument. This will override the state's default distribution.
	-  `randf` ([`RandomFloatFunction`](#use-of-deterministic-randomness-in-custom-functionality)): A callable that accepts the same arguments as above.
	-  `params` (`StateParams`): A container holding global and local state information.
  

### `default_branching_function()`
-  **Return Type : `int`**
-  **Description:** Uses the `randf` function to add random variance (bounded by `branching_factor_variance`) to the `base_branching_factor` and returns this value.


### `default_value_function()`
-  **Parameters:**
	-  `self_branching_factor` (`int`): *An additional parameter.* The number of children associated with the current state.
	-  `child_true_value_information` (`ChildTrueValueInformation`): *An additional parameter.* Stores data on the true values of all children generated so far.
-  **Return Type : `int`**
-  **Description:** Generates a true value for a child state. Ensures that the values behave in a sensible manner by adhering to the rules and the [true value parameters](#true-value-parameters).


### `default_child_depth_function()`
-  **Return Type : `int`**
-  **Description:** Uses the `randint` to randomly generate a depth between minimum and maximum child depth and returns that value.


### `default_transposition_space_function()`

-  **Parameters:**
	-  `globals` (`GlobalVariables`): *Replaces the `params` parameter.* A container holding global state information.
	-  `depth` (`int`): *An additional parameter.* An integer specifying the depth of the current state.
-  **Return Type : `int`**
-  **Description:** Uses `globals` to return the maximum number of different states per depth, ensuring minimal transpositions.


### `default_heuristic_value_function()`

-  **Return Type : `int`**
-  **Description:** Simulates a heuristic function with 70%-85% accuracy depending on depth. // TODO: change

  

# Use of Deterministic Randomness in Custom Functionality

  

Each state in the graph has access to a deterministic random number generator. This allows user-defined functions to behave consistently across runs. The random generators are exposed through two helper functions:


### `RandomIntFunction` and `RandomFloatFunction`


**Return Values:**
-  `RandomIntFunction`: `int`
-  `RandomFloatFunction`: `float`

Both functions sample a number between `low` (inclusive) and `high` (inclusive), following the specified `distribution`.

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

# Custom Types and Containers

### **`StateParams`**

`StateParams` is a dataclass that stores all relevant information about a state. The API passes an instance of this object to user-defined functions, enabling access to state-related parameters from outside the class.

`StateParams` is composed of two subcomponents:
- [`GlobalVariables`](#globalvariables): global parameters shared across the entire graph.
- [`StateParamsSelf`](#stateparamsself): local information specific to the current state node.

> **Note:** This separation exists because not all custom functions require access to both global and local data. Separating them helps ensure that functions only receive the data they actually need.



### **`GlobalVariables`**

`GlobalVariables` is a dataclass that stores information shared across the entire graph. It mirrors the configuration options passed in during initialization — essentially a copy of the [`State` class' parameters](#parameters).



### **`StateParamsSelf`**

`StateParamsSelf` is a dataclass containing local information about the current `StateNode`, such as its depth, parent relationship, or node-specific values.

___

<a name="RandomnessDistribution"></a>
## `RandomnessDistribution`

`RandomnessDistribution` is an enum with two options: UNIFORM and GAUSSIAN. It specifies the distribution type used by the random number generator.
```python
from custom_types import RandomnessDistribution

state = State(distribution=RandomnessDistribution.GAUSSIAN)
```
In this case, all random number generation will default to a Gaussian distribution unless overridden.

You can override the distribution in specific functions:

```python
from custom_types import RandomnessDistribution

def uniform3_branching_function(randint:RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
	return randint(low=0, high=3, distribution=RandomnessDistribution.UNIFORM)

state = State(distribution=RandomnessDistribution.GAUSSIAN)
```
Here, the state's default is Gaussian, but `randint` in `uniform3_branching_function` explicitly uses a uniform distribution.

## `Player`

`Player` is an enum with two values: MIN and MAX. It is used by the API to identify the current player and can also be utilized by users in search algorithms.
For a more detailed usage, see the [minimax example](#minimax-search).

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

This project is licensed under the [GNU General Public License v3.0](LICENSE).