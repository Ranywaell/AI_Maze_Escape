import heapq
from collections import deque


# ── Search algorithms ──────────────────────────────────────────────────────────
class SearchAlgorithms:
    @staticmethod
    def bfs(walls_set, cols, rows, start, end):
        """Breadth-First Search — guarantees shortest path."""
        q = deque([(start, [start])])
        seen = {start}
        nodes = 0
        while q:
            (cx, cy), path = q.popleft()
            nodes += 1
            if (cx, cy) == end:
                return path, nodes
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0<=nx<cols and 0<=ny<rows and (nx,ny) not in seen and (nx,ny) not in walls_set:
                    seen.add((nx,ny))
                    q.append(((nx,ny), path+[(nx,ny)]))
        return [], nodes

    @staticmethod
    def astar(walls_set, cols, rows, start, end):
        """A* Search — uses heuristic to guide the search."""
        def h(pos):
            return abs(pos[0]-end[0]) + abs(pos[1]-end[1])
            
        pq = []
        heapq.heappush(pq, (h(start), 0, start, [start]))
        seen = {start: 0}
        nodes = 0
        while pq:
            f, g, (cx, cy), path = heapq.heappop(pq)
            nodes += 1
            if (cx, cy) == end:
                return path, nodes
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0<=nx<cols and 0<=ny<rows and (nx,ny) not in walls_set:
                    new_g = g + 1
                    if (nx,ny) not in seen or new_g < seen[(nx,ny)]:
                        seen[(nx,ny)] = new_g
                        heapq.heappush(pq, (new_g + h((nx,ny)), new_g, (nx,ny), path+[(nx,ny)]))
        return [], nodes

    @staticmethod
    def dfs(walls_set, cols, rows, start, end):
        """Depth-First Search — not guaranteed shortest, but explores differently."""
        stack = [(start, [start])]
        seen = {start}
        nodes = 0
        while stack:
            (cx, cy), path = stack.pop()
            nodes += 1
            if (cx, cy) == end:
                return path, nodes
            for dx, dy in [(-1,0),(1,0),(0,-1),(0,1)]:
                nx, ny = cx+dx, cy+dy
                if 0<=nx<cols and 0<=ny<rows and (nx,ny) not in seen and (nx,ny) not in walls_set:
                    seen.add((nx,ny))
                    stack.append(((nx,ny), path+[(nx,ny)]))
        return [], nodes
