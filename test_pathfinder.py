import math
import pytest

from PathFinder import Pathfinder, Direction


# -------------------------
# Fixtures
# -------------------------


@pytest.fixture
def simple_maze():
    # 0 = walkable, 1 = wall
    return [
        [1, 1, 1, 1, 1],
        [1, 0, 0, 0, 1],
        [1, 0, 1, 0, 1],
        [1, 0, 0, 0, 1],
        [1, 1, 1, 1, 1],
    ]


@pytest.fixture
def pathfinder(simple_maze):
    return Pathfinder(simple_maze)


# -------------------------
# Direction enum tests
# -------------------------


def test_direction_opposites():
    assert Direction.UP.opposite == Direction.DOWN
    assert Direction.DOWN.opposite == Direction.UP
    assert Direction.LEFT.opposite == Direction.RIGHT
    assert Direction.RIGHT.opposite == Direction.LEFT


def test_direction_vectors():
    assert Direction.UP.value == (0, -1)
    assert Direction.DOWN.value == (0, 1)
    assert Direction.LEFT.value == (-1, 0)
    assert Direction.RIGHT.value == (1, 0)


# -------------------------
# Maze validation tests
# -------------------------


@pytest.mark.parametrize(
    "x,y,expected",
    [
        (1, 1, True),  # open tile
        (0, 0, False),  # wall
        (-1, 1, False),  # out of bounds
        (1, -1, False),
        (10, 10, False),
    ],
)
def test_is_valid_tile(pathfinder, x, y, expected):
    assert pathfinder.is_valid_tile(x, y) is expected


# -------------------------
# Exit detection tests
# -------------------------


def test_available_exits_excludes_reverse(pathfinder):
    exits = pathfinder.get_available_exits(x=2, y=1, current_direction=Direction.RIGHT)

    assert exits == [Direction.RIGHT]


def test_available_exits_excludes_walls_and_reverse(pathfinder):
    exits = pathfinder.get_available_exits(x=1, y=2, current_direction=Direction.UP)

    assert exits == [Direction.UP]


def test_available_exits_order_respects_preference(pathfinder):
    exits = pathfinder.get_available_exits(x=1, y=3, current_direction=Direction.UP)

    # Preference order: UP, LEFT, DOWN, RIGHT
    assert exits == sorted(exits, key=lambda d: Pathfinder.DIRECTION_PREFERENCE.index(d))


# -------------------------
# Distance calculation tests
# -------------------------


def test_euclidean_distance_zero(pathfinder):
    assert pathfinder.euclidean_distance(2, 3, 2, 3) == 0.0


def test_euclidean_distance_known_value(pathfinder):
    dist = pathfinder.euclidean_distance(0, 0, 3, 4)
    assert math.isclose(dist, 5.0)


# -------------------------
# Direction choice logic
# -------------------------


def test_choose_direction_single_exit(pathfinder):
    direction = pathfinder.choose_direction(
        ghost_x=2, ghost_y=2, current_direction=Direction.UP, target_x=1, target_y=1
    )

    assert direction == Direction.LEFT


def test_choose_direction_dead_end_reverses(pathfinder):
    # Ghost hits dead end at (1,1) going UP
    direction = pathfinder.choose_direction(
        ghost_x=1, ghost_y=1, current_direction=Direction.UP, target_x=3, target_y=3
    )

    assert direction == Direction.DOWN


def test_choose_direction_minimizes_distance(pathfinder):
    # Intersection where DOWN is closer to target than RIGHT
    direction = pathfinder.choose_direction(
        ghost_x=2, ghost_y=1, current_direction=Direction.RIGHT, target_x=2, target_y=3
    )

    assert direction == Direction.DOWN


def test_choose_direction_tie_breaker_uses_preference(pathfinder):
    direction = pathfinder.choose_direction(
        ghost_x=2, ghost_y=3, current_direction=Direction.UP, target_x=2, target_y=2
    )

    # UP and LEFT are equidistant → UP wins by preference
    assert direction == Direction.UP


# -------------------------
# Movement tests
# -------------------------


@pytest.mark.parametrize(
    "x,y,direction,expected",
    [
        (2, 2, Direction.UP, (2, 1)),
        (2, 2, Direction.DOWN, (2, 3)),
        (2, 2, Direction.LEFT, (1, 2)),
        (2, 2, Direction.RIGHT, (3, 2)),
    ],
)
def test_get_next_position(pathfinder, x, y, direction, expected):
    assert pathfinder.get_next_position(x, y, direction) == expected


# -------------------------
# Integration-style test
# -------------------------


def test_full_decision_sequence(pathfinder):
    ghost_x, ghost_y = 1, 1
    direction = Direction.RIGHT
    target_x, target_y = 3, 3

    for _ in range(4):
        next_direction = pathfinder.choose_direction(ghost_x, ghost_y, direction, target_x, target_y)

        # Lookahead tile
        dx, dy = direction.value
        lookahead_x = ghost_x + dx
        lookahead_y = ghost_y + dy

        available = pathfinder.get_available_exits(lookahead_x, lookahead_y, direction)

        assert next_direction in available or next_direction == direction.opposite

        # Apply movement
        ghost_x, ghost_y = pathfinder.get_next_position(ghost_x, ghost_y, next_direction)
        direction = next_direction
