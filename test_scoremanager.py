import pytest

from ScoreManager import ScoreManager


# -------------------------
# Fixtures
# -------------------------


@pytest.fixture
def score_manager():
    return ScoreManager()


# -------------------------
# Initialization & reset
# -------------------------


def test_initial_state(score_manager):
    assert score_manager.score == 0
    assert score_manager.ghost_eaten_combo == 1


def test_reset_restores_initial_state(score_manager):
    score_manager.score = 1234
    score_manager.ghost_eaten_combo = 4

    score_manager.reset()

    assert score_manager.score == 0
    assert score_manager.ghost_eaten_combo == 1


# -------------------------
# Pellet scoring
# -------------------------


def test_add_pellet_score(score_manager):
    score_manager.add_pellet_score()
    assert score_manager.score == 10
    assert score_manager.ghost_eaten_combo == 1


def test_multiple_pellets_accumulate(score_manager):
    for _ in range(5):
        score_manager.add_pellet_score()

    assert score_manager.score == 50
    assert score_manager.ghost_eaten_combo == 1


# -------------------------
# Power pellet scoring
# -------------------------


def test_add_power_pellet_score(score_manager):
    score_manager.add_power_pellet_score()

    assert score_manager.score == 50
    assert score_manager.ghost_eaten_combo == 1


def test_power_pellet_resets_ghost_combo(score_manager):
    score_manager.add_ghost_score()  # combo -> 2
    score_manager.add_ghost_score()  # combo -> 3

    score_manager.add_power_pellet_score()

    assert score_manager.ghost_eaten_combo == 1


# -------------------------
# Ghost scoring & combos
# -------------------------


def test_first_ghost_score(score_manager):
    score_manager.add_ghost_score()

    assert score_manager.score == 200
    assert score_manager.ghost_eaten_combo == 2


def test_second_ghost_score(score_manager):
    score_manager.add_ghost_score()
    score_manager.add_ghost_score()

    # 200 + 400
    assert score_manager.score == 600
    assert score_manager.ghost_eaten_combo == 3


def test_full_ghost_combo_sequence(score_manager):
    scores = []

    for _ in range(4):
        score_manager.add_ghost_score()
        scores.append(score_manager.score)

    assert scores == [200, 600, 1400, 3000]
    assert score_manager.ghost_eaten_combo == 5


def test_ghost_score_formula(score_manager):
    # Explicitly validate the formula: (2 ** combo) * 100
    expected_scores = [200, 400, 800, 1600]

    for expected in expected_scores:
        previous_score = score_manager.score
        score_manager.add_ghost_score()

        assert score_manager.score - previous_score == expected


# -------------------------
# Sequencing & integration behavior
# -------------------------


def test_pellets_do_not_affect_ghost_combo(score_manager):
    score_manager.add_ghost_score()  # combo -> 2
    score_manager.add_pellet_score()

    assert score_manager.ghost_eaten_combo == 2


def test_power_pellet_then_ghost(score_manager):
    score_manager.add_ghost_score()  # 200
    score_manager.add_power_pellet_score()
    score_manager.add_ghost_score()  # should restart at 200

    assert score_manager.score == 200 + 50 + 200
    assert score_manager.ghost_eaten_combo == 2


def test_mixed_gameplay_sequence(score_manager):
    score_manager.add_pellet_score()  # 10
    score_manager.add_pellet_score()  # 20
    score_manager.add_power_pellet_score()  # 70
    score_manager.add_ghost_score()  # 270
    score_manager.add_ghost_score()  # 670
    score_manager.add_pellet_score()  # 680

    assert score_manager.score == 680
    assert score_manager.ghost_eaten_combo == 3


# -------------------------
# Safety & regression tests
# -------------------------


def test_score_never_decreases(score_manager):
    score_manager.add_pellet_score()
    score_manager.add_power_pellet_score()
    score_manager.add_ghost_score()

    assert score_manager.score > 0


def test_combo_never_below_one(score_manager):
    score_manager.add_power_pellet_score()
    score_manager.reset()

    assert score_manager.ghost_eaten_combo >= 1
