
# Synthetic State Space Generator

## Table of Contents

- [Introduction](#introduction)

- [Getting Started](#getting-started)

- [Basic Usage](#basic-usage)

- [Parameters](#parameters)

- [Default Behavioural Functions](#default-behavioural-functions)


- [Use of Deterministic Randomness in Behavioral Functions](#use-of-deterministic-randomness-in-behavioral-functions)

- [Custom Types and Containers](#custom-types-and-containers)

- [API Reference](#api-reference)

- [License](#license)

# Introduction
This API allows users to generate a variety of synthetic state-space graphs which simulate real games, and to interact with them in ways that game solvers typically would. 

The tool is aimed at researchers in the field of AI and games (specifically *two-player, deterministic, perfect-information, zero-sum games*). The hope is that it will assist in quick and intuitive prototyping of synthetic game-spaces, in order to test the comparative effectiveness of different algorithms to games with varying properties.

The main principles of the tool are:
- 1. **Memory efficiency**: Graphs are generated implicitly. This means that once initialized with initial parameters and seed, the graph is generated on the fly as it is being traversed.
- 2. **Reproducability**: Being able to replicate results is very important. Since graphs are not stored in memory, the approach is to ensure that they behave completely deterministically no matter how they are traversed. 
- 3. **Easy to use, but powerful**: Ideally, a wide variety of games can be imitated somewhat intuitievly by the default behavior and parameters we have provided. However, the scope of different games and their rules is too large to be able to cover every case. Therefore, in order to strike a balance between complexity and ease of use, the tool has a modular design to allow users to pass custom functions that control certain aspects of its behavior.

This document serves mainly as a guide on the use of software itself. For a deeper conceptional understanding on its design, an accompanying research paper will be linked here once available.

# Getting Started
To install the API, simply,
1. Clone the repository:
```
git clone git@github.com:michael-je/synthetic-state-space-generator.git
```
2. Move into the repository directory:
```
cd synthetic-state-space-generator
```
3. Optionally create a new virtual environment (might be necessary on some systems):
```
python3 -m venv venv
```
4. Install the package locally via pip:
```
pip3 install .
```

# Basic Usage
## Methods
To initialize a new state-space graph, use the `SyntheticGraph` constructor. The default graph is a simple binary tree:
```python
state = SyntheticGraph()   # initialize a new graph
```

After creating a graph, we can query the current state for available actions using `.actions()`, and transition to child states using the `.make()` method:
```python
actions = state.actions()  # get a list of available transitions
state.make(actions[0])     # transition to the first child state
```

We can interact with the graph programatically:
```python
while not state.is_terminal():	# take random actions until we reach a terminal state
	state.make_random()
state.true_value()		# then query for the state's true value
```

We can undo actions as often as we like to traverse back up the graph:
```python
while not state.is_root():	# undo the actions until we return to the root state
	state.undo()
```

More detailed examples can be found in [example_usage.py](examples/example_usage.py).

## Parametrization

To quickly create graphs with different properties, we can initialize `SyntheticGraph` with keyword arguments.
```python
# create a graph with a high branching factor
state = SyntheticGraph(
	branching_factor_base = 40,
	branching_factor_variance = 10
)
```
```python
# create a graph with a very good heuristic evaluation function
state = SyntheticGraph(
	heuristic_accuracy_base = 0.9,
	heuristic_depth_scaling = 0.8
)
```
```python
# create a graph with a custom child depth function that randomly creates cycles 10% of the time.
def custom_child_depth_function(randint, randf, params):
	if randf() < 0.1:
		return randint(-6, -2)
	return 1

state = SyntheticGraph(
	child_depth_function = custom_child_depth_function
)
```
These parameters can of course be combined in interesting ways to construct all sorts of different game-state graphs.  For examples of creating more complex graphs, see [example_graphs.py](examples/example_graphs.py).

<a name="parameters"></a>
# Parameters

-  **`seed`** (`int`, default: `0`, range: `[0, 0xFFFFFFFF]`)
Determines the starting seed for the graph generator. Ensures reproducibility.

-  **`max_depth`** (`int`, default: `2^8 - 1`)
Sets the maximum depth of the graph.

-  **`distribution`** ([`RandomnessDistribution`](#RandomnessDistribution), default: `UNIFORM`, option: `UNIFORM` or `GAUSSIAN`)Determines what distribution the random number generator follows.

-  **`root_true_value`** (`int`, default: `0`, Allowed Values: `[-1, 0, 1]`)
The true value of the root node

<a name="branching-factor-parameters"></a>

-  **`branching_factor_base`** (`int`, default: `2`, range: `Positive Integers`)
  Sets the base branching factor, it represents the typical number of children each state will generate in the graph. This parameter goes in hand with the `branching_factor_variance` to determine the actual number of children generated.

-  **`branching_factor_variance`** (`int`, default: `0`, range: `Positive Integer`)
Specifies how much the branching factor can vary around the base value. A value of `0` means all states have exactly `branching_factor_base` children. Higher values introduce randomness into the number of children each state generates.


-  **`terminal_minimum_depth`** (`int`, default: `0`, range: `Positive Integer`)
  Specifies the minimum depth a state must be before it can be become a terminal node. This ensures that early states in the graph cannot terminate prematurely.

<a name="child-depth-parameters"></a>

-  **`child_depth_minimum`** (`int`, default: `1`)
Defines the minimum depth of a child relative to its parent.
  
-  **`child_depth_maximum`** (`int`, default: `1`)
Defines the maximum depth of a child relative to its parent
	> **NOTE**: `child_depth_minimum` and `child_depth_maximum` can take negative values. In this case, children may be generated "above" their parent, creating cycles in the graph.

-  **`locality_grouping `** (`float`, default: `0`, range: `[0, 1]`)
Controls how much of the available state space can be used when generating children. A value of `0` allows use of the full space at each depth; higher values restrict generation to a smaller portion centered around the parent node.

<a name="true-value-parameters"></a>

-  **`true_value_forced_ratio`** (`float`, default: `0.1`, range: `[0, 1]`)
Controls the ratio of children that are `forced` to share the same true value as their parent state. (NOTE: this is a strict lower bound and setting this to zero breaks the integrity of true value propagation.)

-  **`true_value_similarity_chance`** (`float`, default: `0.5`, range: `[0, 1]`)
After meeting the minimum forced match requirement, this sets the chance that a remaining child will also take on the parent’s true value (A value of `0` means only forced nodes inherit the parent’s value; `1` means all children do).

-  **`true_value_tie_chance `** (`float`, default: `0.2`, range: `[0, 1]`)
For children not covered by `forced value` or `similarity chance`, this sets the probability of the child being assigned a draw. (**NOTE**: the actual expected number of draws is dependent on `true_value_forced_ratio` and `true_value_similarity_chance`)

- **`symmetry_factor`** (`float`, default: `1.0`, range: `[0, 1]`)  
Controls how much the branching factor is reduced for symmetric states. A value of `1.0` means no reduction, while lower values simulate symmetry by proportionally reducing the number of generated states. For example, a symmetry factor of `0.5` will halve the branching factor when symmetry applies.

- **`symmetry_frequency`** (`float`, default: `0.0`, range: `[0, 1]`)  
  Specifies the likelihood that a given state is considered symmetric. If a state is determined to be symmetric (based on this probability), the branching factor is reduced according to the `symmetry_factor`.

<a name="heuristic-value-parameters"></a>

-  **`heuristic_accuracy_base`** (`float`, default: `0.7`, range: `[0, 1]`)
  Controls the baseline accuracy of the `heuristic_value` relative to the `true_value`. A value of `1.0` means the heuristic always matches the true value. A value of `0.0` means the heuristic is completely random

-  **`heuristic_depth_scaling`** (`float`, default: `0.5`, range: `[0, 1]`)
Determines how depth affects the accuracy of the `hueristic value`. A value of `0.0` means depth has no effect, while higher values cause heuristic accuracy to improve as depth increases.

-  **`heuristic_locality_scaling`** (`float`, default: `0.5`, range: `[0, 1]`)
Determines how locality affects the accuracy of the `hueristic value`. This aims to simulate how some parts of the graph have a worse hueristic than others.

<a name="branching-function"></a>
-  **`branching_function`** (`function`, default: [`default_branching_function`](#default_branching_function))
A custom function able to be overriden by the user to determine the branching factor of states.

-  **`child_value_function`** (`function`, default: [`default_value_function`](#default_value_function))
A custom function able to be overriden by the user to determine the true values of a state's child.

-  **`child_depth_function`** (`function`, default: [`default_child_depth_function`](#default_child_depth_function))
A custom function able to be overriden by the user to determine the depth of a child relative to its parent.

-  **`transposition_space_function`** (`function`, default: [`default_transposition_space_function`](#default_transposition_space_function))
A custom function able to be overriden by the user to define the upper bound of unique states at each depth.

-  **`heuristic_value_function`** (`function`, default: [`default_heuristic_value_function`](#default_heuristic_value_function))
A custom function able to be overriden by the user to determine the heuristic values of states.

	> **NOTE**: Most of these parameters are only used by the behavioral functions (discussed in the next section) rather than interacting strongly with the software's internal logic. This means that the user is free to change how they affect the graph.


# Default Behavioural Functions

Certain functionality is controlled by what we call "behavioral functions". These functions are used to generate certain values based on other currently observed values in the graph. For example, deciding on the branching factor of a state given its depth. We provide sane defaults which can be found in [default_functions.py](default_functions.py).

However, since these rules can vary so wildly between different kinds of graphs, we allow user-defined functions to be passed to the API during initialization. We recommend having a look at the default functions, as well as the [example functions](examples/example_behavior_functions.py), to get a better idea of how to construct your own. 

Following is a list of the available functions. They must all accept the arguments listed directly below, unless explicitely stated otherwise: 
-  **Parameters:**
	-  `randint` ([`RandomIntFunction`](#use-of-deterministic-randomness-in-custom-functionality)): See [`RandomIntFunction`](#use-of-deterministic-randomness-in-custom-functionality) for a description.
	-  `randf` ([`RandomFloatFunction`](#use-of-deterministic-randomness-in-custom-functionality)): See [`RandomFloatFunction`](#use-of-deterministic-randomness-in-custom-functionality) for a description. 
	-  `params` (`StateParams`): A container holding global and local state information.
  

### `default_branching_function()`
-  **Return Type : `int`**
-  **Description:** Uses the `randf` function to add random variance (bounded by `branching_factor_variance`) to the `base_branching_factor` and returns this value. The branching factor is calculated using the [branching_factor_base](#branching-factor-parameters), [branching_factor_variance](#branching-factor-parameters) and [terminal_minimum_depth](#branching-factor-parameters) parameters.


### `default_value_function()`
-  **Parameters:**
	-  `self_branching_factor` (`int`): *An additional parameter.* The number of children associated with the current state.
	-  `child_true_value_information` (`ChildTrueValueInformation`): *An additional parameter.* Stores data on the true values of all children generated so far.
-  **Return Type : `int`**
-  **Description:** Generates a true value for a child state. Ensures that the values behave in a sensible and consistent manner, following the true value parameters [true_value_forced_ratio](#true-value-parameters), [true_value_similarity_chance](#true-value-parameters) and [true_value_tie_chance](#true-value-parameters). Below is a more detailed visualization of how these parameters work together to generate child values.

	<a name="True-Value-Graph"></a>
	![True Value Graph](./documentation_images/value_propagation.gif)


### `default_child_depth_function()`
-  **Return Type : `int`**
-  **Description:** Uses the `randint` to randomly generate a depth between minimum and maximum child depth and returns that value. The depth is calculated using the [child_minimum_depth](#child-depth-parameters) and [child_maximum_depth](#child-depth-parameters) parameters.


### `default_transposition_space_function()`

-  **Parameters:**
	-  `globals` (`GlobalVariables`): *Replaces the `params` parameter.* A container holding global state information.
	-  `depth` (`int`): *An additional parameter.* An integer specifying the depth of the current state.
-  **Return Type : `int`**
-  **Description:** Uses `globals` to return the maximum number of different states per depth, ensuring minimal transpositions.


### `default_heuristic_value_function()`

-  **Return Type : `int`**
-  **Description:** Simluates a heuristic evaluation function by calculating an "estimated value" based on the state's true value. The heuristic is generated using the [heuristic_accuracy_base](#heuristic-value-parameters), [heuristic_depth_scaling](#heuristic-value-parameters) and [heuristic_locality_scaling](#heuristic-value-parameters) parameters.

  

# Use of Deterministic Randomness in Behavioral Functions

  

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

> **NOTE:** This separation exists because not all custom functions require access to both global and local data. Separating them helps ensure that functions only receive the data they actually need.



### **`GlobalVariables`**

`GlobalVariables` is a dataclass that stores information shared across the entire graph. It mirrors the configuration options passed in during initialization — essentially a copy of the [`SyntheticGraph` class' parameters](#parameters).



### **`StateParamsSelf`**

`StateParamsSelf` is a dataclass containing local information about the current `StateNode`, such as its depth, parent relationship, or node-specific values.


<a name="RandomnessDistribution"></a>
### `RandomnessDistribution`

`RandomnessDistribution` is an enum with two options: UNIFORM and GAUSSIAN. It specifies the distribution type used by the random number generator.
```python
from custom_types import RandomnessDistribution

state = State(distribution=RandomnessDistribution.GAUSSIAN)
```
In this case, all random number generation will default to a Gaussian distribution unless overridden.

If the distribution must be overriden for specific behavioral function, it can be done like so:

```python
def uniform3_branching_function(randint:RandomIntFunction, randf: RandomFloatFunction, params: StateParams) -> int:
	return randint(low=0, high=3, distribution=RandomnessDistribution.UNIFORM)

state = State(
	distribution=RandomnessDistribution.GAUSSIAN,
	branching_function=uniform3_branching_function,
)
```
Here, the state's default is Gaussian, but `randint` in `uniform3_branching_function` explicitly uses a uniform distribution.

### `Player`

`Player` is an enum with two values: `MIN` and `MAX`. It is used by the API to identify the current player and can also be utilized by users in search algorithms.

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