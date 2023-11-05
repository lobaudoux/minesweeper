from constants import DIRECTIONS, FLAG, UNEXPLORED


class Agent:
    def __init__(self, minesweeper):
        self.flag = minesweeper.flag
        self.board = minesweeper.board
        self.size_x, self.size_y = minesweeper.size_x, minesweeper.size_y
        self.watched_list = []
        self.watched_board = [[False for _ in range(self.size_y)] for _ in range(self.size_x)]

    def _get_adjacent_cells(self, x, y):
        adjacent_cells = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size_x and 0 <= ny < self.size_y:
                adjacent_cells.append((nx, ny))
        return adjacent_cells

    def _is_clue(self, x, y):
        return 1 <= self.board[x][y] <= 8

    def get_move(self):
        # Naive algorthm
        while len(self.watched_list) > 0:
            x, y = self.watched_list.pop()
            self.watched_board[x][y] = False
            mines = []
            unexplored = []
            for ax, ay in self._get_adjacent_cells(x, y):
                if self.board[ax][ay] == FLAG:
                    mines.append((ax, ay))
                elif self.board[ax][ay] == UNEXPLORED:
                    unexplored.append((ax, ay))
            if len(mines) == self.board[x][y] and len(unexplored) > 0:
                return unexplored
            elif len(mines) + len(unexplored) == self.board[x][y]:
                for ux, uy in unexplored:
                    self.flag(ux, uy)

        # Naive algorithm is stuck, we have to move to more advanced resolution
        # Find the remaining unexplored cells
        unexplored = []
        for x in range(self.size_x):
            for y in range(self.size_y):
                if self.board[x][y] == UNEXPLORED:
                    unexplored.append((x, y))

        # Find the clue cells adjacent to those unexplored cells
        clues_to_check = set()
        for x, y in unexplored:
            clues_to_check.update(filter(lambda pos: self._is_clue(pos[0], pos[1]), self._get_adjacent_cells(x, y)))

        # This dictionary where the key is the unexplored cell coordinate and the value is another dictionary where the
        # key is a group of cells and the value is the number of mines that are contained in this group of cells
        groups_per_cell = {}

        # This dictionary contains the unexplored cells adjacent to each clue to check
        adjacent_unexplored_per_cell = {}

        # This dictionary contains the number of known mines adjacent to each clue to check
        n_adjacent_mines_per_cell = {}

        for cx, cy in clues_to_check:
            adjacent_unexplored = []
            n_adjacent_mines = 0
            for ax, ay in self._get_adjacent_cells(cx, cy):
                if self.board[ax][ay] == UNEXPLORED:
                    adjacent_unexplored.append((ax, ay))
                elif self.board[ax][ay] == FLAG:
                    n_adjacent_mines += 1

            adjacent_unexplored_per_cell[(cx, cy)] = adjacent_unexplored
            n_adjacent_mines_per_cell[(cx, cy)] = n_adjacent_mines

            adjacent_unexplored = tuple(sorted(adjacent_unexplored))
            for cell in adjacent_unexplored:
                groups_per_cell.setdefault(cell, {})[adjacent_unexplored] = self.board[cx][cy] - n_adjacent_mines

        # Now use these information to find out which cells can be explored
        for cx, cy in clues_to_check:
            adjacent_unexplored = adjacent_unexplored_per_cell[(cx, cy)]
            mines_left = self.board[cx][cy] - n_adjacent_mines_per_cell[(cx, cy)]

            candidate_groups_dict = {}
            for ux, uy in adjacent_unexplored:
                for group, n_mines in groups_per_cell[(ux, uy)].items():
                    if all((cx, cy) in adjacent_unexplored for cx, cy in group):
                        candidate_groups_dict[group] = n_mines

            for group, n_mines in candidate_groups_dict.items():
                cells_left = set(adjacent_unexplored) - set(group)
                if cells_left and mines_left == n_mines:
                    return list(cells_left)

        return []

    def add_watched(self, x, y):
        if not self.watched_board[x][y] and 1 <= self.board[x][y] <= 8:
            self.watched_list.append((x, y))
            self.watched_board[x][y] = True
