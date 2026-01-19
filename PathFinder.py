import math
from typing import Tuple, List
from enum import Enum

import time
import os


class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

    @property
    def opposite(self):
        opposites = {
            Direction.UP: Direction.DOWN,
            Direction.DOWN: Direction.UP,
            Direction.LEFT: Direction.RIGHT,
            Direction.RIGHT: Direction.LEFT,
        }
        return opposites[self]


class Pathfinder:
    """
    Implements ghost pathfinding logic for a Pac-Man-style maze.
    Ghosts look one step ahead and choose directions based on Euclidean distance
    to their target tile.
    """

    # Direction preference order for tie-breaking: up, left, down, right
    DIRECTION_PREFERENCE = [Direction.UP, Direction.LEFT, Direction.DOWN, Direction.RIGHT]

    def __init__(self, maze: List[List[int]]):
        """
        Initialize the pathfinder with a maze.

        Args:
            maze: 2D list where 0 = walkable tile, 1 = wall
        """
        self.maze = maze
        self.height = len(maze)
        self.width = len(maze[0]) if maze else 0

    def is_valid_tile(self, x: int, y: int) -> bool:
        """Check if a tile position is valid and walkable."""
        if x < 0 or x >= self.width or y < 0 or y >= self.height:
            return False
        return self.maze[y][x] == 0

    def get_available_exits(self, x: int, y: int, current_direction: Direction) -> List[Direction]:
        """
        Get all available exits from a tile, excluding walls and reverse direction.

        Args:
            x, y: Current tile coordinates
            current_direction: Current direction of travel

        Returns:
            List of valid directions to move
        """
        available = []

        for direction in self.DIRECTION_PREFERENCE:
            # Skip reverse direction
            if direction == current_direction.opposite:
                continue

            # Check if the exit leads to a valid tile
            dx, dy = direction.value
            next_x, next_y = x + dx, y + dy

            if self.is_valid_tile(next_x, next_y):
                available.append(direction)

        return available

    def euclidean_distance(self, x1: int, y1: int, x2: int, y2: int) -> float:
        """Calculate Euclidean distance between two points."""
        return math.dist((x1, y1), (x2, y2))

    def choose_direction(
        self, ghost_x: int, ghost_y: int, current_direction: Direction, target_x: int, target_y: int
    ) -> Direction:
        """
        Choose the next direction for the ghost based on looking ahead one tile.

        Args:
            ghost_x, ghost_y: Current ghost position
            current_direction: Ghost's current direction of travel
            target_x, target_y: Target tile coordinates

        Returns:
            The direction the ghost should take at the next intersection
        """
        # Look ahead to the next tile along current direction
        dx, dy = current_direction.value
        lookahead_x = ghost_x + dx
        lookahead_y = ghost_y + dy

        # Get available exits from the lookahead tile
        available_exits = self.get_available_exits(lookahead_x, lookahead_y, current_direction)

        # If only one exit is available, use it
        if len(available_exits) == 1:
            return available_exits[0]

        # If no exits are available (dead end), reverse direction
        if len(available_exits) == 0:
            return current_direction.opposite

        # Multiple exits available - evaluate test tiles
        best_direction = None
        best_distance = float("inf")

        for direction in available_exits:
            # Get test tile position (one tile beyond intersection in this direction)
            test_dx, test_dy = direction.value
            test_x = lookahead_x + test_dx
            test_y = lookahead_y + test_dy

            # Calculate distance from test tile to target
            distance = self.euclidean_distance(test_x, test_y, target_x, target_y)

            # Update best direction if this is better
            if distance < best_distance:
                best_distance = distance
                best_direction = direction
            elif distance == best_distance:
                # Tie-breaking: use direction preference order
                if self.DIRECTION_PREFERENCE.index(direction) < self.DIRECTION_PREFERENCE.index(
                    best_direction
                ):
                    best_direction = direction

        return best_direction

    def get_next_position(self, x: int, y: int, direction: Direction) -> Tuple[int, int]:
        """
        Get the next position given current position and direction.

        Args:
            x, y: Current position
            direction: Direction to move

        Returns:
            Tuple of (next_x, next_y)
        """
        dx, dy = direction.value
        return (x + dx, y + dy)


def draw_maze(maze, path, ghost, target):
    path_set = set(path)

    for y, row in enumerate(maze):
        line = ""
        for x, cell in enumerate(row):
            pos = (x, y)

            if pos == ghost:
                line += "👻 "
            elif pos == target:
                line += "🎯 "
            elif pos in path_set:
                line += "🟩 "
            elif cell == 1:
                line += "🟦 "
            else:
                line += "⬜ "
        print(line)


def animate_ghost(
    pathfinder: Pathfinder,
    maze,
    ghost_x: int,
    ghost_y: int,
    current_direction: Direction,
    target_x: int,
    target_y: int,
    delay: float = 0.4,
    max_steps: int = 100,
):
    x, y = ghost_x, ghost_y
    direction = current_direction
    visited = []

    for step in range(max_steps):
        visited.append((x, y))

        os.system("cls" if os.name == "nt" else "clear")
        print(f"Step {step} | Ghost: ({x}, {y}) | Moving: {direction.name}")
        draw_maze(maze, visited, (x, y), (target_x, target_y))

        if (x, y) == (target_x, target_y):
            print("\nTarget reached!")
            break

        # 1. Decide what the turn will be AFTER reaching the next tile
        next_direction = pathfinder.choose_direction(x, y, direction, target_x, target_y)

        # 2. Move to the next tile using the CURRENT direction
        x, y = pathfinder.get_next_position(x, y, direction)

        # 3. Now that we've arrived at the new tile, update the direction for the NEXT step
        direction = next_direction

        time.sleep(delay)


def simulate_ghost_path(
    pathfinder: Pathfinder,
    ghost_x: int,
    ghost_y: int,
    current_direction: Direction,
    target_x: int,
    target_y: int,
    max_steps: int = 100,
):
    path = [(ghost_x, ghost_y)]
    x, y = ghost_x, ghost_y
    direction = current_direction

    for _ in range(max_steps):
        if (x, y) == (target_x, target_y):
            break

        direction = pathfinder.choose_direction(x, y, direction, target_x, target_y)

        x, y = pathfinder.get_next_position(x, y, direction)
        path.append((x, y))

    return path


if __name__ == "__main__":
    maze = [
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        [0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0],  # Tunnel Row
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 1, 0, 1, 1, 1, 1],
        [1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 0, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 1],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 0, 1, 1],
        [1, 0, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 1, 0, 0, 0, 0, 1],
        [1, 0, 1, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 1, 1, 0, 1],
        [1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1],
        [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    ]

    pathfinder = Pathfinder(maze)

    animate_ghost(
        pathfinder,
        maze,
        ghost_x=1,  # Start top-left
        ghost_y=1,
        current_direction=Direction.RIGHT,
        target_x=17,  # Target bottom-right
        target_y=19,
        delay=0.1,  # Speed it up for the larger map
    )
