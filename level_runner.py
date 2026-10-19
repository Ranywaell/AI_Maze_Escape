import pygame, sys, math, time

from constants import W, H, TILE, COLORS, LEVELS


# ── Main Game Loop Runner ──────────────────────────────────────────────────────
class LevelRunner:
    def __init__(self, screen, clock, font, font_big, risk_predictor):
        self.screen = screen
        self.clock = clock
        self.font = font
        self.font_big = font_big
        self.risk_predictor = risk_predictor

    def run_level(self, level_idx, algo_name, search_fn):
        maze = LEVELS[level_idx]
        rows, cols = len(maze), len(maze[0])

        walls = set()
        start_pos = (0,0)
        exit_pos = (0,0)
        enemies_init = []

        for y, row in enumerate(maze):
            for x, char in enumerate(row):
                if char == '#': walls.add((x,y))
                elif char == 'P': start_pos = (x,y)
                elif char == 'E': exit_pos = (x,y)
                elif char == 'e':
                    enemies_init.append({'pos': [x*TILE, y*TILE], 'dir': 1, 'axis': 'x' if len(enemies_init)%2==0 else 'y'})

        path = []
        death_tiles = set()
        deaths = 0
        max_deaths = 5
        total_nodes = 0

        while deaths < max_deaths:
            # ── Map Stopwatch (Resets on each restart!) ──
            map_start_time = time.perf_counter()
            current_map_time = 0.0

            enemies = []
            for e in enemies_init:
                enemies.append({'pos': list(e['pos']), 'dir': e['dir'], 'axis': e['axis']})

            agent_pos = list(start_pos)

            # Consider walls AND tiles where the agent died as obstacles
            virtual_walls = walls.union(death_tiles)

            # Calculates path ONLY ONCE at the start of the life!
            path, nodes = search_fn(virtual_walls, cols, rows, tuple(agent_pos), exit_pos)
            total_nodes += nodes

            path_idx = 0
            alive = True
            reached_exit = False
            max_risk = 0.0
            status = "Safe"
            agent_move_counter = 0
            agent_move_delay = 8  # HIGHER NUMBER = SLOWER AGENT

            while alive and not reached_exit:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()

                # Calculate elapsed time continuously for this specific attempt
                current_map_time = time.perf_counter() - map_start_time

                # Move Agent along path (Now Slower!)
                agent_move_counter += 1
                if agent_move_counter >= agent_move_delay:
                    if path_idx < len(path):
                        next_cell = path[path_idx]

                        lookahead = path[path_idx : path_idx+3]
                        max_risk = 0.0
                        status = "Safe"

                        # ── 2-Block Proximity Check (For UI Only) ──
                        min_dist = float('inf')
                        for en in enemies:
                            ex, ey = int(en['pos'][0]//TILE), int(en['pos'][1]//TILE)
                            # Calculate Manhattan distance from the agent's current position
                            dist = abs(agent_pos[0] - ex) + abs(agent_pos[1] - ey)
                            if dist < min_dist:
                                min_dist = dist

                        if min_dist <= 2:
                            # UI update, but agent will ignore it and keep walking!
                            status = "Danger Ahead! (Ignoring)"
                        else:
                            # Calculate Neural Network Risk for UI
                            for c in lookahead:
                                risk_pct = self.risk_predictor.get_risk_percentage(c, enemies)
                                if risk_pct > max_risk:
                                    max_risk = risk_pct

                                if risk_pct >= 10.0:
                                    status = "Risky Path! (Ignoring)"

                        # NO RE-EVALUATION: The agent unconditionally moves to the next cell on its original path
                        agent_pos = list(next_cell)
                        path_idx += 1

                        if tuple(agent_pos) == exit_pos:
                            reached_exit = True

                    agent_move_counter = 0

                # Move Enemies (Slow speed)
                for en in enemies:
                    px, py = en['pos']
                    axis = en['axis']
                    d = en['dir']
                    speed = 1

                    if axis == 'x':
                        nx = px + d * speed
                        tx1, tx2 = int(nx//TILE), int((nx+TILE-1)//TILE)
                        ty1, ty2 = int(py//TILE), int((py+TILE-1)//TILE)
                        if any((cx, cy) in walls for cx in range(tx1, tx2+1) for cy in range(ty1, ty2+1)):
                            en['dir'] *= -1
                        else:
                            en['pos'][0] = nx
                    else:
                        ny = py + d * speed
                        tx1, tx2 = int(px//TILE), int((px+TILE-1)//TILE)
                        ty1, ty2 = int(ny//TILE), int((ny+TILE-1)//TILE)
                        if any((cx, cy) in walls for cx in range(tx1, tx2+1) for cy in range(ty1, ty2+1)):
                            en['dir'] *= -1
                        else:
                            en['pos'][1] = ny

                # Collision Check
                if alive:
                    ax, ay = agent_pos[0]*TILE + TILE/2, agent_pos[1]*TILE + TILE/2
                    for en in enemies:
                        ex, ey = en['pos'][0] + TILE/2, en['pos'][1] + TILE/2
                        if math.hypot(ax-ex, ay-ey) < TILE*0.8:
                            alive = False
                            death_tiles.add(tuple(agent_pos))
                            deaths += 1

                            # Visual Restart Feedback
                            pygame.draw.rect(self.screen, COLORS['ui_bg'], (0, 0, W, 40))
                            ui_text = self.font.render(f"Algo: {algo_name} | DIED! RESTARTING...", True, (255, 80, 80))
                            self.screen.blit(ui_text, (10, 10))
                            pygame.display.flip()
                            pygame.time.delay(1000)  # Pause for 1 second to show restart
                            break

                # Rendering
                if alive:
                    self.screen.fill(COLORS['bg'])
                    for y in range(rows):
                        for x in range(cols):
                            rect = (x*TILE, y*TILE, TILE, TILE)
                            if (x,y) in walls:
                                pygame.draw.rect(self.screen, COLORS['wall'], rect)
                            elif (x,y) in death_tiles:
                                pygame.draw.rect(self.screen, COLORS['danger'], rect)
                            elif (x,y) == exit_pos:
                                pygame.draw.rect(self.screen, COLORS['exit'], rect)

                    # Draw Path
                    for i, p in enumerate(path):
                        if i >= path_idx:
                            pygame.draw.circle(self.screen, COLORS['path'], (p[0]*TILE + TILE//2, p[1]*TILE + TILE//2), 4)

                    # Draw Agent
                    pygame.draw.rect(self.screen, COLORS['agent'], (agent_pos[0]*TILE + 4, agent_pos[1]*TILE + 4, TILE-8, TILE-8), border_radius=4)

                    # Draw Enemies
                    for en in enemies:
                        pygame.draw.rect(self.screen, COLORS['enemy'], (en['pos'][0]+4, en['pos'][1]+4, TILE-8, TILE-8), border_radius=8)

                    # UI
                    pygame.draw.rect(self.screen, COLORS['ui_bg'], (0, 0, W, 40))
                    ui_text = self.font.render(f"Algo: {algo_name} | Deaths: {deaths}/{max_deaths} | Nodes: {total_nodes} | Time: {current_map_time:.1f}s | Risk: {max_risk:.0f}% {status}", True, COLORS['text'])
                    self.screen.blit(ui_text, (10, 10))

                    pygame.display.flip()
                    self.clock.tick(60)

            if reached_exit:
                path_len = len(path)
                return {"algo": algo_name, "path_len": path_len, "nodes": total_nodes, "time": current_map_time, "success": True, "deaths": deaths}

        # If it looped out because deaths >= max_deaths
        return {"algo": algo_name, "path_len": len(path), "nodes": total_nodes, "time": current_map_time, "success": False, "death": True, "deaths": deaths}
