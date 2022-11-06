class Cell:
    def __init__(self, col, row, blocked=False, color=None, mark=False, is_empty=False):
        self.col = col
        self.row = row
        self.coords = (self.row, self.col)
        self.blocked = blocked
        self._color = color
        self.is_empty = is_empty
        if color == '-':
            self.blocked = True
            self.is_empty = True
            self._color = None

        self._mark = mark
        if self.blocked:
            assert self.is_empty, " ".join(
                [str(x) for x in [self._color, self.blocked, self.is_empty, self.row, self.col]])
        # if not self.is_empty:
        #     assert self._color, " ".join([str(x) for x in [self._color, self.blocked, self.is_empty]])
        self.is_not_empty = not is_empty

    def mark(self):
        self._mark = True

    def unmark(self):
        self._mark = False

    @property
    def marked(self):
        return self._mark

    @property
    def color(self):
        return self._color

    @color.setter
    def color(self, value):
        self._color = value