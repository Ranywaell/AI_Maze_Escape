import pygame, sys

from constants import W, H
from search_algorithms import SearchAlgorithms
from risk_predictor import RiskPredictor
from splash_screen import SplashScreen
from level_runner import LevelRunner
from comparison_screen import ComparisonScreen

pygame.init()
screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Maze Escape – AI Agent")
clock = pygame.time.Clock()
font     = pygame.font.SysFont(None, 28)
font_big = pygame.font.SysFont(None, 48)


# ── Main Game Controller ───────────────────────────────────────────────────────
class MazeEscapeGame:
    def __init__(self):
        self.risk_predictor = RiskPredictor()
        self.splash_screen = SplashScreen(screen, font, font_big)
        self.level_runner = LevelRunner(screen, clock, font, font_big, self.risk_predictor)
        self.comparison_screen = ComparisonScreen(screen, font, font_big)

    def run(self):
        self.splash_screen.show([
            ("Maze Escape – AI Agent", (0,255,255)),
            ("Level 1: BFS  |  Level 2: DFS  |  Level 3: A*", (200,200,200)),
            ("Watch the agent navigate and compare algorithms.", (160,160,160)),
            ("Press any key to start.", (120,120,120)),
        ])

        configs = [("BFS", SearchAlgorithms.bfs), ("DFS", SearchAlgorithms.dfs), ("A*", SearchAlgorithms.astar)]
        results = []

        for idx, (name, fn) in enumerate(configs):
            self.splash_screen.show([
                (f"Level {idx+1}: {name}", (0,255,200)),
                (f"Algorithm: {'Breadth-First Search' if name=='BFS' else ('Depth-First Search' if name=='DFS' else 'A* Search')}", (200,200,200)),
                ("Press any key to watch the agent.", (150,150,150)),
            ])
            res = self.level_runner.run_level(idx, name, fn)
            res['level'] = idx+1
            results.append(res)

            if res.get('death') and not res['success']:
                msg = "You Ran Out Of Lives!"
                color = (255, 80, 80)
            else:
                msg = "Level Complete!" if res['success'] else "Level Failed"
                color = (100, 255, 100) if res['success'] else (255, 80, 80)

            self.splash_screen.show([
                (msg, color),
                (f"Path: {res['path_len']} | Nodes: {res['nodes']} | Deaths: {res['deaths']}", (200,200,200)),
                ("Press any key to continue.", (150,150,150)),
            ])

        self.comparison_screen.show_comparison(results)
        pygame.quit()


# ── Entry point ────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    game = MazeEscapeGame()
    game.run()
