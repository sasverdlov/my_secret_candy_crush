from collections import deque, defaultdict, Counter
from typing import List

from cell import Cell


class MatchFinder:
    def __init__(self, grid: List[List[Cell]]):
        self.grid = grid
        self.rows = len(grid)
        self.columns = len(grid[0])
        self.visited = [[-1 for _ in range(self.columns)] for _ in range(self.rows)]
        self.incidents = {}

    def is_possible_point(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.columns

    def get_neighbors(self, row, col):
        if (row, col) in self.incidents:
            return self.incidents[(row, col)]
        all_points = [(row, col + 1), (row - 1, col), (row, col - 1), (row + 1, col)]
        incs = [t for t in all_points if self.is_possible_point(t[0], t[1])]
        self.incidents[(row, col)] = incs
        return incs

    def _is_3_in_line_match(self, match):
        if len(match) < 3:
            return False
        rows = Counter([x for x, y in match])
        columns = Counter([y for x, y in match])
        for i, v in rows.items():
            if v >= 3:
                return True
        for i, v in columns.items():
            if v >= 3:
                return True
        return False

    def find_matches(self):
        index = 0
        index_map = defaultdict(list)
        for row in range(self.rows):
            for col in range(self.columns):
                if self.visited[row][col] < 0:
                    self._find_matches(row, col, index, index_map)
                    index = index + 1
        matches = [val for val in index_map.values() if self._is_3_in_line_match(val)]
        return matches

    def _find_matches(self, row, col, index, index_map):
        deq = deque()
        deq.append(((row, col), index))
        while len(deq) > 0:
            v, i = deq.pop()
            row, col = v
            v_cell = self.grid[row][col]
            self.visited[row][col] = i
            index_map[i].append(v)
            for w in self.get_neighbors(row, col):
                w_row, w_col = w
                w_cell = self.grid[w_row][w_col]
                if self.visited[w_row][w_col] < 0:
                    if v_cell.color == w_cell.color:
                        self.visited[w_row][w_col] = i
                        deq.append((w, i))
