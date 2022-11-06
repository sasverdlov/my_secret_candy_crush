import random
from collections import deque, Counter
from copy import deepcopy

from cell import Cell
from graph import Graph
from match_finder import MatchFinder
from move import Move
from move_finder import MoveFinder

MAX_MOVES = 10
COLORMAP_CAPACITY = 100


class Grid:
    def __init__(self, target, size=8, shape_draft=None, randomize=True, colorlist=None, color_weights=None):
        self.trouble = 0
        self.walked = []
        self.i = 0
        self.rows = 0
        self.columns = 0
        self.colorlist = colorlist
        self.color_weights = color_weights
        self.randomize = randomize
        self.draft_repr = self.generate_from_draft(shape_draft)
        self.colormap = self.gen_random_color_draft()
        self.orig_colormap = deepcopy(self.colormap)
        self.grid = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        # self.path_graph = Graph()
        # print(self.colormap)
        # print(self.visualize_draft())
        # if shape_draft:
        #     self.grid = self.generate_from_draft(shape_draft)
        # else:
        #     self.grid = self.generate_from_size(size)
        self.fill_grid()
        # print(len(self.grid))
        self.results = {k: 0 for k in colorlist}

        self.winning_paths = 0
        self.all_paths = 0
        self.all_paths_list = []
        self.current_path = []
        self.target = target
        self.last_move = None

    def __getitem__(self, position):
        assert type(position) == tuple
        assert len(position) == 2
        x, y = position
        return self.grid[y][x]

    def __setitem__(self, position, value):
        assert type(position) == tuple
        assert len(position) == 2
        assert type(value) == Cell
        x, y = position
        self.grid[y][x] = value

    def reset(self):
        self.results = {k: 0 for k in self.colorlist}
        self.colormap = deepcopy(self.orig_colormap)
        self.grid = [[None for _ in range(self.columns)] for _ in range(self.rows)]
        self.fill_grid()

    def swap(self, row, col, direction):
        # TODO убрать дублирование (как в move_finder)
        if direction == 'V':
            new_row, new_col = row + 1, col
        elif direction == 'H':
            new_row, new_col = row, col + 1
        else:
            raise KeyError('Invalid direction: ' + direction)
        self.grid[row][col], self.grid[new_row][new_col] = self.grid[new_row][new_col], self.grid[row][col]

    def unswap(self, x, y, direction):
        if direction == 'V':
            x2, y2 = x - 1, y
        elif direction == 'H':
            x2, y2 = x, y - 1
        else:
            raise KeyError('Invalid direction: ' + direction)
        self.grid[y][x], self.grid[y2][x2] = self.grid[y2][x2], self.grid[y][x]

    def cells_around(self, cell):
        x, y = cell.row, cell.col
        # print(cell.coords, cell.row, cell.col, cell.color)
        variants = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
        possible_variants = []
        for v in variants:
            xv, yv = v
            if 0 <= xv < self.rows and 0 <= yv < self.columns:
                possible_variants.append(self.grid[yv][xv])
        return possible_variants

    def find_3matches(self):
        matches = MatchFinder(self.grid).find_matches()
        return [[self.grid[row][col] for row, col in match] for match in matches]

    def mark_all_same_color_around(self, cell, orig=None):
        x, y = cell.coords
        # self.grid[y][x].mark()
        # self.unmark_stale(self.grid[y][x])
        if not orig:
            orig = self.grid[y][x].color
        around_same_colors = [c for c in self.cells_around(self.grid[y][x]) if c.color == orig and not c.marked]
        self.walked += around_same_colors
        for cell in around_same_colors:
            # cell.mark()
            # print(self.visualize_grid_marked())
            if not cell in self.walked:
                self.mark_all_same_color_around(cell, orig)

    # def find_same_colors_around(self, x, y):
    #     orig_color = self.grid[y][x].color
    #     matches = self.mark_3matches()
    #     for match in matches:
    #         for item in match:
    #             item.mark()
    #             around = [self.grid[y][x] for x, y in self.cells_around(x, y)]
    #             around_same_colors = [x for x in around if x.color == orig_color]
    #             # for cell in around_same_colors:
    #             #     self.mark_all_same_color_around(*cell.coords)
    #     # if len(around_same_colors) >= 2:
    #     #     self.grid[y][x].mark()
    #
    #         return True
    #     return False

    def update_columns(self):
        for col in range(self.columns):
            clean = deque([self.grid[row][col].color for row in range(self.rows) if not self.grid[row][col]._mark])
            for row in range(self.rows):
                self.grid[row][col].color = self.colormap[col].popleft() if row < self.rows-len(clean) else clean.popleft()
        self.demark()

    def unmark_stale(self, cell):
        around = self.cells_around(cell)
        if not any([x.mark for x in around]):
            cell.unmark()
            return False
        return True

    def collect_merged(self):
        for col in range(self.columns):
            for row in range(self.rows):
                if self.grid[row][col].marked:
                    self.results[self.grid[row][col].color] += 1
                    # self.grid[row][col].color = '*'

    def check_matches(self):
        # unmark everyting
        self.demark()
        assert not [item for sublist in self.grid for item in sublist if item._mark]
        self.walked = []
        # found_matches = False
        matches = self.find_3matches()
        if matches:
            # found_matches = True
            for match in matches:
                for item in match:
                    item._mark = True
            self.collect_merged()

    def find_possible_moves(self):
        # possible_moves = [[False for _ in range(self.columns)] for _ in range(self.rows)]
        return MoveFinder(self.grid).iter_possible_moves()

    def find_legal_moves(self):
        # current_grid = deepcopy(self.grid)
        # print(self.visualize_grid())
        legal_moves = []
        # print(self.visualize_grid(current_grid))
        for move in self.find_possible_moves():
            self.swap(*move)
            if self.find_3matches():
                legal_moves.append(move)
            self.swap(*move)
            # self.grid = current_grid
            # print(self.visualize_grid())
        return legal_moves

    def fill_grid(self, ):
        def add_value(c):
            return self.colormap[c].popleft()

        # for col in range(self.rows):
        #   for row in range(self.columns):
        for row in range(self.rows-1, -1, -1):
            for col in range(self.columns):
                dot = Cell(col=row, row=col,
                           color=add_value(col) if self.draft_repr[row][col] == '□' else self.draft_repr[row][col])
                # {'col': col, 'row': row, 'value': add_value() if draft_repr[col][row] == '□' else draft_repr[col][row]}
                # self[col, row] = dot
                self.grid[row][col] = dot

    def generate_from_size(self, size):
        # res = []
        # for x in range(self.rows):
        #   for y in range(self.columns):
        pass

    def generate_from_draft(self, draft):
        def generate_from_line(x):
            return x.strip().split()

        draft_repr = [generate_from_line(x) for x in draft.splitlines() if len(x.strip()) > 0]
        # print(draft_repr)
        self.rows = len(draft_repr)
        self.columns = max([Counter(x)['□'] for x in draft_repr])
        return draft_repr

    def gen_random_color_draft(self):
        return [deque(random.choices(self.colorlist, weights=self.color_weights,
                               k=COLORMAP_CAPACITY)) for _ in range(self.columns)]

    def visualize_colormap(self, cm=None):
        if cm is None:
            cm = self.colormap
        # cm = deepcopy(self.colormap) if not cm else deepcopy(cm)
        res = ""
        for row in range(COLORMAP_CAPACITY):
            for col in range(self.columns):
                res += '0' if COLORMAP_CAPACITY-row > len(cm[col]) else cm[col][COLORMAP_CAPACITY-row-1]
            res += '\n'
        return res

    def visualize_grid(self, gr=None):
        res = ""
        # print(len(self.grid))
        for row in range(self.rows):
            for col in range(self.columns):
                res += self.grid[row][col].color if not gr else gr[row][col].color
            res += '\n'
        return res

    def visualize_grid_marked(self):
        res = ""
        # print(len(self.grid))
        for row in range(self.rows):
            for col in range(self.columns):
                res += '*' if self.grid[row][col]._mark else '-'
            res += '\n'
        return res

    def check_target(self, res=None):
        r = []
        actual = self.results if not res else res
        for k, v in self.target.items():
            r.append(actual[k] >= v)
        return all(r)

    def demark(self):
        for col in range(self.columns):
            for row in range(self.rows):
                if self.grid[row][col]._mark:
                    self.grid[row][col].unmark()

    def generate_next_step(self):
        prev_colormap = deepcopy(self.colormap)
        prev_grid = deepcopy(self.grid)
        prev_results = deepcopy(self.results)

    def code_path(self, path):
        return "".join([str(i) for sl in path for i in sl])

    def get_paths_graph(self):
        self.prepare_field()
        self.path_graph = Graph(start_grid=deepcopy(self.grid),
                                start_colormap=deepcopy(self.colormap))
        self.find_legal_moves()

    def bla(self):
        # moves = self.find_legal_moves()
        i = 0
        # for move in self.find_legal_moves():
        moves = self.find_legal_moves()
        while moves:
            # add_move
            move = moves.pop(0)
            self.swap(*move)
            self.check_matches()
            self.update_columns()
            self.fill_gaps()

    def routine(self):
        self.check_matches()
        # print(self.visualize_grid_marked())
        self.update_columns()
        # print(self.visualize_grid())
        self.fill_gaps()
        # print(self.visualize_colormap())

    def iteration(self, move):
        # self.demark()
        tuple_move = move.row, move.col, move.direction
        depth, basic_grid, basic_colormap, path, results = move.depth, move.grid, move.colormap, move.path, move.results
        self.grid = basic_grid
        self.colormap = basic_colormap
        self.results = results
        # print(self.visualize_grid())
        # print(tuple_move)
        self.swap(*tuple_move)
        # print(self.visualize_grid())
        while self.find_3matches():
            self.routine()
        # print(self.visualize_grid())
        grid = deepcopy(self.grid)
        colormap = deepcopy(self.colormap)
        moves = self.find_legal_moves()
        path = path + "".join([str(x) for x in tuple_move])
        results = deepcopy(self.results)
        return moves, grid, colormap, tuple_move, depth + 1, path, results

    def iterative_approach(self):
        self.q = deque()
        # print(self.visualize_grid())
        moves = self.find_legal_moves()
        # print(self.visualize_grid())
        for i, move in enumerate(moves):
            row, col, direction = move
            new_move = Move(father=None, row=row, col=col, direction=direction, depth=0, grid=deepcopy(self.grid),
                            colormap=deepcopy(self.colormap), path="", results=deepcopy(self.results))
            self.q.append(new_move)
        while self.q:
            # try:
            current_move = self.q.pop()
            moves, grid, colormap, father, depth, path, results = self.iteration(current_move)
            print(len(self.q))
            # except IndexError:
            #     self.path_with_no_
            #     continue
            # print(depth)
            # print(len(self.q))
            print(path)
            # print(self.results)
            print(results)
            if self.check_target(results):
                self.all_paths += 1
                self.winning_paths += 1
                print("YEEEEEEEY!")
            else:
                if depth <= MAX_MOVES:
                    for move in moves:
                        row, col, direction = move
                        self.q.append(Move(father=father, row=row, col=col, direction=direction, depth=depth, grid=grid,
                                           colormap=colormap, path=path, results=results))
                else:
                    self.all_paths += 1

    def prepare_field(self):
        self.prev_colormap = deepcopy(self.colormap)
        self.prev_grid = deepcopy(self.grid)
        self.prev_results = deepcopy(self.results)
        while self.find_3matches():
            # print(self.visualize_grid())
            self.check_matches()
            # print(self.results)
            # print(self.visualize_grid())
            # print(self.visualize_grid_marked())
            self.update_columns()
            # print('Update columns..')
            # print(self.visualize_grid())
            self.fill_gaps()
        if self._start_condition:
            self.start_colormap = deepcopy(self.colormap)
            self.start_grid = deepcopy(self.grid)
            # print(self.visualize_grid())
            # print(self.colormap)
            # print(f"COLORMAP\n{self.visualize_colormap()}")
            self.results = deepcopy(self.prev_results)
            self._start_condition = False

    def make_moves_map(self):
        # print(self.visualize_grid())
        print(len(self.all_paths_list), self.winning_paths, self.all_paths)
        self.demark()
        # k = [item for sublist in self.grid for item in sublist if item._mark]
        # if k:
        #     pass
        # assert not [item for sublist in self.grid for item in sublist if item._mark], [item for sublist in self.grid for item in sublist if item._mark]
        self.prev_colormap = deepcopy(self.colormap)
        self.prev_grid = deepcopy(self.grid)
        self.prev_results = deepcopy(self.results)
        while self.find_3matches():
            # print(self.visualize_grid())
            self.check_matches()
            # print(self.visualize_grid())
            # print(self.visualize_grid_marked())
            self.update_columns()
            self.fill_gaps()
        if self._start_condition:
            self.start_colormap = deepcopy(self.colormap)
            self.start_grid = deepcopy(self.grid)
            # print(self.visualize_grid())
            # print(self.colormap)
            # print(f"COLORMAP\n{self.visualize_colormap()}")
            self.results = deepcopy(self.prev_results)
            self._start_condition = False
        moves = self.find_legal_moves()
        # if self.i == 0:
        #     pass
        # print(f"PAPAPAPAPA{moves}")
        for move in moves:  # [move for move in moves if move not in self.current_path]:
            if self.code_path(self.current_path + [move]) not in self.all_paths_list:
                self.current_path.append(move)
                # print(f"CP {self.current_path}")
                # print(f"AP {self.all_paths}")
                # print(f"WP {self.winning_paths}")
                self.swap(*move)
                self.i += 1
                # print(self.i)
            else:
                continue
            if not self.check_target() and len(self.current_path) < MAX_MOVES and self.find_legal_moves():
                # try:
                self.make_moves_map()
            # except RecursionError:
            #     self.trouble += 1
            #     print(self.trouble)
            #     continue
            # pass
            elif len(self.current_path) >= MAX_MOVES or not self.find_legal_moves():
                if self.code_path(self.current_path) not in self.all_paths_list:
                    self.all_paths_list.append(self.code_path(self.current_path))
                    self.grid = deepcopy(self.prev_grid)
                    self.colormap = deepcopy(self.prev_colormap)
                    self.results = deepcopy(self.prev_results)
                    # print(f"UNSW, path len: {len(self.current_path)}")
                    self.current_path.pop()
                    self.make_moves_map()
                else:
                    self.current_path = []
                    self.all_paths += 1
                    self.i = 0
                    # print('NO')
                    self.reset()
                    self.make_moves_map()
            else:
                self.all_paths += 1
                self.winning_paths += 1
                # print("YES")
                # print(self.visualize_grid())
                # print(self.visualize_grid_marked())
                if self.code_path(self.current_path) not in self.all_paths_list:
                    self.all_paths_list.append(self.code_path(self.current_path))
                    self.grid = deepcopy(self.prev_grid)
                    self.colormap = deepcopy(self.prev_colormap)
                    self.results = deepcopy(self.prev_results)
                    # print(f"UNSW, path len: {len(self.current_path)}")
                    self.current_path.pop()
                    self.make_moves_map()
                else:
                    self.current_path = []
                    self.i = 0
                    self.reset()
                    self.make_moves_map()
        else:
            self.all_paths_list.append(self.code_path(self.current_path))
            # print(self.current_path)
            self.current_path = []
            self.all_paths += 1
            self.i = 0
            self.reset()
            if self.check_target():
                self.winning_paths += 1
                # print("YES")
                # print(self.visualize_grid())
                # print(self.visualize_grid_marked())
            else:
                pass
                # print("NO")
            self.make_moves_map()
        # for move in moves:

    # def recurse_path(self):
    #     for path in
    # append move to current path
    # if not target and current path not 100
    # go()
    # get new moves
    # append move to current path...
    # else

    # pass

    def main(self):
        # self.check_matches()
        # self.update_columns()
        # self.fill_gaps()
        self._start_condition = True
        self.make_moves_map()
        # iterations = 0
        # while not self.check_target() and iterations < 100:
        #     self.check_matches()
        #     self.update_columns()
        #     self.fill_gaps()
        #     # self
        #     iterations += 1
        # print(f"FINISHED IN {iterations}")

    def main_iter(self):
        self._start_condition = True
        self.prepare_field()
        self.pths = set()
        self.iterative_approach()

    def _grid_to_str(self, grid):
        return '_'.join([''.join(row) for row in grid])

    def tree_iter(self):
        self._start_condition = True
        self.prepare_field()
        self.pths = set()
        self.tree = {}
        self.grid_map = {}
        self.build_tree(self.grid, 0)

    def build_tree(self, grid, depth):
        if depth > MAX_MOVES:
            return
        grid_key = self._grid_to_str(grid)
        if grid_key not in self.grid_map:
            # TODO тут нужно вынести find_legal_moves в отдельный класс
            moves = self.find_legal_moves()


    def test_some(self):
        # print(self.colormap)
        # print([[c.color for c in i] for i in x.grid])
        for i in range(len([item for sublist in self.grid for item in sublist])):
            col, row = i // self.columns, i % self.columns
            assert self.grid[self.rows-row-1][col].color == self.orig_colormap[col][row], [self.grid[self.rows-row-1][col].color,
                                                                               self.orig_colormap[col][row]]
            # print(self.grid[col][row].color, self.colormap[col][row])

    def fill_gaps(self):
        pass
