import pygame, sys

from constants import W, H


# ── Comparison screen ──────────────────────────────────────────────────────────
class ComparisonScreen:
    def __init__(self, screen, font, font_big):
        self.screen = screen
        self.font = font
        self.font_big = font_big

    def show_comparison(self, results):
        self.screen.fill((10,10,20))
        title = self.font_big.render("Algorithm Comparison", True, (0,255,255))
        self.screen.blit(title, (W//2-title.get_width()//2, 40))

        headers = ["Level", "Algo", "Path Len", "Nodes", "Total Time", "Result"]
        col_x   = [20, 100, 200, 320, 440, 560]
        y = 120
        # header row
        for i, h in enumerate(headers):
            s = self.font.render(h, True, (180,180,255))
            self.screen.blit(s, (col_x[i], y))
        pygame.draw.line(self.screen, (80,80,120), (20, y+28), (W-20, y+28), 1)
        y += 40

        for r in results:
            if r.get('death') and not r['success']:
                status_text = "✗ Died out"
                color = (255,100,100)
            else:
                status_text = "✓ Success" if r['success'] else "✗ Failed"
                color = (100,255,100) if r['success'] else (255,100,100)

            vals = [
                str(r['level']),
                r['algo'],
                str(r['path_len']),
                str(r['nodes']),
                f"{r['time']:.2f} s",
                status_text
            ]

            for i, v in enumerate(vals):
                s = self.font.render(v, True, color)
                self.screen.blit(s, (col_x[i], y))
            y += 36

        # Insight
        if len(results) == 3 and all(r['success'] for r in results):
            bfs_r = next(r for r in results if r['algo']=='BFS')
            dfs_r = next(r for r in results if r['algo']=='DFS')
            astar_r = next(r for r in results if r['algo']=='A*')
            note1 = f"BFS: {bfs_r['path_len']} cells | DFS: {dfs_r['path_len']} cells | A*: {astar_r['path_len']} cells"
            note2 = f"BFS nodes: {bfs_r['nodes']} | DFS nodes: {dfs_r['nodes']} | A* nodes: {astar_r['nodes']}"
            note3 = "A* usually explores fewer nodes than BFS for the shortest path."
            for i, line in enumerate([note1, note2, note3]):
                s = self.font.render(line, True, (200,200,100))
                self.screen.blit(s, (W//2-s.get_width()//2, y+20+i*32))

        quit_msg = self.font.render("Press any key to quit.", True, (150,150,150))
        self.screen.blit(quit_msg, (W//2-quit_msg.get_width()//2, H-50))
        pygame.display.flip()

        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
