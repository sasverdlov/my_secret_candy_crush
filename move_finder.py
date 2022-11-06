from typing import List

from cell import Cell


class MoveFinder:
    def __init__(self, grid: List[List[Cell]]):
        self.grid = grid
        self.rows = len(grid)
        self.columns = len(grid[0])

    def can_swap(self, row, col, direction):
        if direction == 'H':
            new_col, new_row = col + 1, row
        elif direction == 'V':
            new_col, new_row = col, row + 1
        else:
            raise KeyError('Invalid direction: ' + direction)
        if new_col >= self.columns or new_row >= self.rows:
            return False
        # Можем свопать только разные цвета
        return self.grid[row][col].color != self.grid[new_row][new_col].color

    def is_possible_point(self, row, col):
        return 0 <= row < self.rows and 0 <= col < self.columns

    def iter_possible_moves(self):
        for col in range(self.columns):
            for row in range(self.rows):
                for direction in ('H', 'V'):
                    if self.can_swap(row, col, direction):
                        yield row, col, direction

