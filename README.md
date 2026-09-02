*This project has been created as part of the 42 curriculum by <wezhou>, <mmoriya>.*

# A-Maze-ing

## Description

A-Maze-ing is a maze generation project written in Python.

The program reads maze parameters from a configuration file, generates a valid maze, writes the maze data to an output file using hexadecimal wall encoding, and displays the maze graphically using MiniLibX.

The project supports both perfect and non-perfect mazes. It also provides shortest-path calculation, reproducible maze generation using a seed, and an interactive graphical interface.

The maze generation logic is implemented as a reusable Python package named `mazegen`, independently from the graphical renderer and the main program.

## Features

- Random maze generation
- Reproducible generation using a seed
- Perfect and non-perfect mazes
- Multiple maze generation algorithms
- Shortest-path calculation
- Hexadecimal maze output
- Visible `42` pattern using closed cells
- Graphical visualization using MiniLibX
- Interactive maze regeneration
- Show/hide shortest solution path
- Change wall colours
- Reusable `mazegen` Python package

## Instructions

### Requirements

- Python 3.10 or later
- MiniLibX
- pip

Install the required dependencies with:

    make install

### Running the Program

Run the project with:

    python3 a_maze_ing.py config.txt

or:

    make run

The program takes exactly one configuration file as its argument.

### Debugging

Run the program using Python's debugger with:

    make debug

### Linting

Run the required style and type checks with:

    make lint

### Cleaning

Remove temporary Python files and caches with:

    make clean

## Configuration File

The configuration file uses the following format:

    KEY=VALUE

One configuration option is written per line. Lines beginning with `#` are treated as comments and ignored.

Example:

    WIDTH=20
    HEIGHT=20
    ENTRY=2,3
    EXIT=19,13
    OUTPUT_FILE=output_file.txt
    PERFECT=False
    SEED=42
    ALGORITHM=kruskal

### Mandatory Options

WIDTH
    Width of the maze in cells.

HEIGHT
    Height of the maze in cells.

ENTRY
    Entry coordinates in `x,y` format.

EXIT
    Exit coordinates in `x,y` format.

OUTPUT_FILE
    File where the generated maze is written.

PERFECT
    `True` to generate a perfect maze, otherwise `False`.

### Additional Options

SEED
    Seed used for reproducible random generation.

ALGORITHM
    Maze generation algorithm.

Supported algorithms:

    dfs
    prim
    kruskal

## Maze Representation

Each maze cell contains four possible walls.

The hexadecimal wall representation uses the following bits:

    Bit 0: North = 1
    Bit 1: East  = 2
    Bit 2: South = 4
    Bit 3: West  = 8

A closed wall is represented by 1 and an open wall by 0.

For example:

    F (1111) = all four walls are closed
    3 (0011) = North and East walls are closed
    A (1010) = East and West walls are closed

Each cell is written as one hexadecimal digit in the output file.

After the maze representation, an empty line is written, followed by:

    1. Entry coordinates
    2. Exit coordinates
    3. Shortest path from entry to exit

The shortest path is represented using the letters:

    N = North
    E = East
    S = South
    W = West

## Maze Generation

The project supports three maze generation algorithms:

    - Depth-First Search
    - Randomized Prim's Algorithm
    - Randomized Kruskal's Algorithm

### Depth-First Search

The DFS implementation uses a randomized recursive-backtracker approach.

Starting from a cell, the algorithm randomly selects an unvisited neighbouring cell, removes the wall between them, and continues exploring. When no unvisited neighbour is available, it backtracks until another possible path is found.

DFS was chosen as the initial algorithm because it provides a simple and efficient way to generate a connected perfect maze.

### Randomized Prim's Algorithm

Prim's algorithm maintains a frontier between visited and unvisited cells.

A random frontier connection is repeatedly selected, connecting a new cell to the generated maze until all available cells have been included.

### Randomized Kruskal's Algorithm

Kruskal's algorithm initially treats each available cell as an independent set.

Possible connections between neighbouring cells are shuffled. A wall is removed only when the two cells belong to different sets. The sets are then merged using a Union-Find data structure.

This prevents cycles during perfect-maze generation while eventually connecting the available maze cells.

### Perfect and Non-Perfect Mazes

When:

    PERFECT=True

the generated maze contains exactly one valid path between the entry and exit.

When:

    PERFECT=False

additional walls may be removed to introduce cycles and alternative paths while preserving the validity of the maze.

## The 42 Pattern

The visual maze contains a `42` pattern made from fully closed cells.

These cells are excluded from the normal traversable maze structure.

If the configured maze is too small to contain the pattern, the program reports the problem to the user and generates the maze without the pattern.

## Pathfinding

The shortest path between the entry and exit is calculated using Breadth-First Search (BFS).

BFS explores the maze level by level, which guarantees a shortest path in an unweighted maze.

The resulting coordinate path is converted into a sequence of:

    N
    E
    S
    W

directions before being written to the output file.

## Graphical Display

The graphical interface is implemented using MiniLibX.

The renderer displays:

    - Maze walls
    - Entry
    - Exit
    - The `42` pattern
    - Shortest solution path

The following keyboard controls are available:

    1           Generate a new maze
    2           Show or hide the shortest path
    3           Change wall colour
    4 / Q / ESC Exit the program

When a new maze is generated, the graphical representation, shortest path, and output file are updated.

## Reusable Module

Maze generation is separated from the user interface and provided through the `mazegen` package.

The package contains the generation logic, maze representation, generation algorithms, and pathfinding functionality. It does not depend on the MiniLibX renderer.

This allows the generator to be reused in another Python project without using the A-Maze-ing graphical interface.

### Basic Usage

Example:

    from mazegen import MazeGenerator

    generator = MazeGenerator(config)

    generator.generate()

    maze = generator.grid

The generator accepts configuration parameters such as maze dimensions, entry and exit coordinates, random seed, perfect/non-perfect mode, and generation algorithm.

The generated maze structure can be accessed directly from the generator. A solution can be obtained using the pathfinding functionality provided by the package.

### Building the Package

Build the reusable package with:

    python3 -m build

or, if the Makefile provides the build rule:

    make build

The resulting package can be distributed as a `.whl` or `.tar.gz` file and installed using pip.

## Project Structure

    .
    ├── amazing/
    │   ├── __init__.py
    │   ├── config.py
    │   ├── exceptions.py
    │   └── renderer.py
    │
    ├── mazegen/
    │   ├── algorithms/
    │   │   ├── dfs.py
    │   │   ├── kruskal.py
    │   │   ├── prim.py
    │   │   └── utils.py
    │   ├── __init__.py
    │   ├── cell.py
    │   ├── constants.py
    │   ├── generator.py
    │   └── pathfinding.py
    │
    ├── a_maze_ing.py
    ├── config.txt
    ├── Makefile
    ├── pyproject.toml
    └── README.md

## Team and Project Management

### Team Members

<wezhou>

    Maze generation and core logic

<mmoriya>

    Graphical visualization and renderer

### Task Distribution

<wezhou>

    - Configuration file parsing and validation
    - Implementation of maze generation algorithms, including DFS, Prim's algorithm, and Kruskal's algorithm
    - Maze structure, pathfinding, output generation, and validation of maze requirements

<mmoriya>

    - Implementation of the graphical renderer using MiniLibX
    - Visualization of maze walls, entry, exit, the 42 pattern, and the solution path
    - Implementation of graphical interactions such as maze regeneration, path display, and wall colour changes

### Planning

At the beginning of the project, we divided the work according to the two major parts of the program. One member focused on the maze generation logic and configuration system, while the other focused on graphical visualization using MiniLibX.

The generation part was developed first so that the maze structure could be tested independently from the graphical interface. After the basic maze generation and output were working, the renderer was connected to the generator.

During development, the project was extended to support multiple generation algorithms. DFS was implemented first as the basic generation algorithm, followed by Prim's and Kruskal's algorithms. Pathfinding and output generation were also separated from the renderer so that they could be reused by both the output system and the graphical interface.

In the final stage, we focused on integration and testing. This included connecting maze regeneration to the renderer, updating the shortest path after regeneration, checking different configurations and maze sizes, and making sure that the generated maze remained valid for all supported algorithms.

### What Worked Well

Dividing the project into generation logic and graphical rendering allowed both parts to be developed relatively independently.

The separation between the reusable `mazegen` package and the graphical application also made the project easier to test and maintain. The maze generation algorithms could be tested without starting MiniLibX, while the renderer only needed to work with the generated maze structure.

Using a common maze representation for DFS, Prim's, and Kruskal's algorithms also made it easier to add new algorithms without changing the renderer or output format.

Finally, integrating the components through a clear interface between the generator and renderer reduced dependencies between the two parts of the project.

### What Could Be Improved

The integration between the maze generator and the graphical renderer could have been started earlier. Since the two parts were initially developed mostly independently, some issues only became visible when they were connected, such as keeping the displayed shortest path and output file synchronized after maze regeneration.

More integration tests during the earlier stages of development would have helped identify these problems sooner.

The project could also benefit from more automated tests covering different maze sizes, seeds, algorithms, and invalid configuration files. Although individual components were tested during development, a more systematic test suite would make it easier to verify that changes to one component do not affect other parts of the program.

For future group projects, we would therefore integrate major components earlier and establish shared integration tests before the final stage of development.

### Why We Chose These Algorithms
DFS was chosen as the initial generation algorithm because it is simple to implement, easy to understand, and naturally produces a connected perfect maze using a recursive-backtracking approach.

Prim's algorithm was added to provide a different generation strategy based on gradually expanding a frontier from the already generated region.

Kruskal's algorithm was added because it provides another graph-based approach using disjoint sets and Union-Find. It also demonstrates clearly how cycles can be prevented while connecting all available cells.

Supporting multiple algorithms also made the reusable generator more flexible and allowed us to compare different maze generation strategies while keeping the same maze representation, renderer, and output format.

### Tools

The project was developed using:

    - Git and GitHub for version control and collaboration
    - Python virtual environments for dependency isolation
    - flake8 for style checking
    - mypy for static type checking
    - MiniLibX for graphical rendering

## Resources

### References

The following resources were used during development:

    - Python documentation
    - MiniLibX documentation
    - Documentation and references for Depth-First Search
    - Documentation and references for Prim's algorithm
    - Documentation and references for Kruskal's algorithm
    - Documentation and references for Breadth-First Search
    - Python packaging documentation

### Use of AI

AI tools were used during the development of this project as a learning and development aid.

They were used for tasks such as:

    - Explaining maze generation and pathfinding algorithms
    - Discussing project architecture and module separation
    - Debugging and reviewing Python code
    - Understanding Python packaging and virtual environments
    - Reviewing configuration validation and edge cases
    - Assisting with MiniLibX integration and debugging
    - Reviewing documentation and project requirements
