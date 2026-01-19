class ScoreManager:
    def __init__(self):
        self.score = 0
        self.ghost_eaten_combo = 1

    def reset(self):
        self.score = 0
        self.ghost_eaten_combo = 1

    def add_pellet_score(self):
        self.score += 10

    def add_power_pellet_score(self):
        self.score += 50
        self.ghost_eaten_combo = 1  # The combo should reset when a power pellet is eaten

    def add_ghost_score(self):
        self.score += (2**self.ghost_eaten_combo) * 100  # 200 -> 400 -> 800 -> 1600
        self.ghost_eaten_combo += 1


if __name__ == "__main__":
    score_manager = ScoreManager()
    score_manager.add_pellet_score()  # 10
    score_manager.add_pellet_score()  # 20
    score_manager.add_power_pellet_score()  # 70
    score_manager.add_ghost_score()  # 270
    score_manager.add_ghost_score()  # 670
    score_manager.add_pellet_score()  # 680

    print(score_manager.score)
    print(score_manager.ghost_eaten_combo)
