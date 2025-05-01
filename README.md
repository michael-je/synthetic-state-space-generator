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

This creates a simple graph, with default values for each parameter. This default graph is a binary tree, with no maximum depth, no state values and no transpositions or cycles.



## Examples

# API Reference

Method | Description | Arguments
| :--- | :--- | :---|
| `id()` | Used to return the ID of the current state.| |
| `is_terminal()` | Used to return True if current state is terminal (is leaf), and false otherwise.| |
| `is_root()` | Used to return True if current state is the root of the graph, and false otherwise.| |
| `value()` | Used to return the true value of the current state.| |
| `heuristic_value()` | Used to return the heuristic value of the current state.| |
| `actions()` | Used to return the possible actions that can be taken from current state. Returns a list of integers representing unique action to transition to new state.| |
| `make()` |  | `action`: An integer representing which  |
| `make_random()` | | |
| `undo()` | Used to undo the last action taken in| |
| `draw()` | Used | |


# License

GPL3 ?
