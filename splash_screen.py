import pygame, sys

from constants import W, H


# ── Splash screen ──────────────────────────────────────────────────────────────
class SplashScreen:
    def __init__(self, screen, font, font_big):
        self.screen = screen
        self.font = font
        self.font_big = font_big

    def show(self, lines):
        self.screen.fill((10,10,20))
        y = H//2 - len(lines)*30
        for i, (txt, color) in enumerate(lines):
            s = (self.font_big if i == 0 else self.font).render(txt, True, color)
            self.screen.blit(s, (W//2 - s.get_width()//2, y + i*40))
        pygame.display.flip()

        waiting = True
        while waiting:
            for e in pygame.event.get():
                if e.type == pygame.QUIT: pygame.quit(); sys.exit()
                if e.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN):
                    waiting = False
