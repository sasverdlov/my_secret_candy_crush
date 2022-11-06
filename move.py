class Move:
    def __init__(self, father, row, col, direction, depth, grid, colormap, path, results):
        self.colormap = colormap
        self.grid = grid
        self.father = father
        self.direction = direction
        self.row = row
        self.col = col
        self.depth = depth
        self.path = path
        self.results = results
        # self.depth = self.father.depth += 1