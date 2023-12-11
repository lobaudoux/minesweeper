from constants import FLAG, NO_MINE, UNEXPLORED


class Agent:
    def __init__(self, minesweeper):
        self.flag = minesweeper.flag
        self.get_adjacent_cells = minesweeper.get_adjacent_cells
        self.board = minesweeper.board
        self.size_x, self.size_y = minesweeper.size_x, minesweeper.size_y
        self.n_mines = minesweeper.n_mines
        self.watched_list = []
        self.watched_board = [[False for _ in range(self.size_y)] for _ in range(self.size_x)]
        self.stuck = False

    def _is_clue(self, x, y):
        return 1 <= self.board[x][y] <= 8

    def _get_number_of_mines_left(self, board):
        return (
            self.n_mines - sum(
                1 if board[x][y] == FLAG else 0
                for x in range(self.size_x)
                for y in range(self.size_y)
            )
        )

    def _get_unexplored_left(self, board):
        return [
            (x, y)
            for x in range(self.size_x)
            for y in range(self.size_y)
            if board[x][y] == UNEXPLORED
        ]

    def _guess_and_check_for_contradiction(self, board, x, y):
        """ Assume that there is a mine at (x, y) and check for a contradiction.
            Returns True if there is one, False otherwise.
        """

        def _flag(_x, _y):
            board[_x][_y] = FLAG
            for _ax, _ay in self.get_adjacent_cells(_x, _y):
                _add_watched(_ax, _ay)

        def _no_mine(_x, _y):
            board[_x][_y] = NO_MINE
            for _ax, _ay in self.get_adjacent_cells(_x, _y):
                _add_watched(_ax, _ay)

        def _add_watched(_x, _y):
            if not watched_board[_x][_y] and self._is_clue(_x, _y):
                watched_list.append((_x, _y))
                watched_board[_x][_y] = True

        # Copy the board
        board = [[board[x][y] for y in range(self.size_y)] for x in range(self.size_x)]
        watched_board = [[False for y in range(self.size_y)] for x in range(self.size_x)]
        watched_list = []

        _flag(x, y)
        while watched_list:
            x, y = watched_list.pop()
            watched_board[x][y] = False
            mines = []
            unexplored = []
            for ax, ay in self.get_adjacent_cells(x, y):
                if board[ax][ay] == FLAG:
                    mines.append((ax, ay))
                elif board[ax][ay] == UNEXPLORED:
                    unexplored.append((ax, ay))
            if len(mines) > board[x][y] or (not unexplored and len(mines) != board[x][y]):
                return True
            elif len(mines) == board[x][y] and len(unexplored) > 0:
                for ux, uy in unexplored:
                    _no_mine(ux, uy)
            elif len(mines) + len(unexplored) == board[x][y]:
                for ux, uy in unexplored:
                    if board[ux][uy] == UNEXPLORED:
                        _flag(ux, uy)
                        if not self._get_number_of_mines_left(board):
                            for x, y in self._get_unexplored_left(board):
                                _no_mine(x, y)
                        for ax, ay in self.get_adjacent_cells(ux, y):
                            _add_watched(ax, ay)

        unexplored = self._get_unexplored_left(board)
        n_mines_left = self._get_number_of_mines_left(board)
        if n_mines_left < 0 or (not unexplored and n_mines_left):
            return True

        if unexplored and not len(unexplored) == n_mines_left:
            guesses_to_attempts = set()
            for ux, uy in unexplored:
                if any(self._is_clue(ax, ay) for ax, ay in self.get_adjacent_cells(ux, uy)):
                    guesses_to_attempts.add((ux, uy))
            if (
                guesses_to_attempts
                and all(self._guess_and_check_for_contradiction(board, x, y) for x, y in guesses_to_attempts)
            ):
                return True

        return False

    def get_cells_to_open(self):
        if self.stuck:
            return []

        # Naive algorithm
        while self.watched_list:
            x, y = self.watched_list.pop()
            self.watched_board[x][y] = False
            mines = []
            unexplored = []
            for ax, ay in self.get_adjacent_cells(x, y):
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
        unexplored = self._get_unexplored_left(self.board)

        # Find the clue cells adjacent to those unexplored cells
        clues_to_check = set()
        for x, y in unexplored:
            clues_to_check.update(filter(lambda pos: self._is_clue(pos[0], pos[1]), self.get_adjacent_cells(x, y)))

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
            for ax, ay in self.get_adjacent_cells(cx, cy):
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

        # If we still don't have a solution, try to guess and deduce by contradiction
        attempted_guesses = set()
        for cx, cy in clues_to_check:
            adjacent_unexplored = adjacent_unexplored_per_cell[(cx, cy)]
            n_mines_left = self.board[cx][cy] - n_adjacent_mines_per_cell[(cx, cy)]
            if n_mines_left == 1:
                for ax, ay in filter(lambda _cell: _cell not in attempted_guesses, adjacent_unexplored):
                    if self._guess_and_check_for_contradiction(self.board, ax, ay):
                        return [(ax, ay)]
                    attempted_guesses.add((ax, ay))

        # If there are no more mines, the remaining cells should be opened
        if not self._get_number_of_mines_left(self.board):
            return unexplored

        if len(unexplored) == self._get_number_of_mines_left(self.board):
            for x, y in unexplored:
                self.flag(x, y)

        self.stuck = True
        return []

    def add_watched(self, x, y):
        if not self.watched_board[x][y] and self._is_clue(x, y):
            self.watched_list.append((x, y))
            self.watched_board[x][y] = True
            self.stuck = False
