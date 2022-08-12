from constants import *


class Agent:
    def __init__(self, minesweeper):
        self.flag = minesweeper.flag
        self.board = minesweeper.board
        self.size_x, self.size_y = minesweeper.size_x, minesweeper.size_y
        self.watched_list = []
        self.watched_board = [[False for _ in range(self.size_y)] for _ in range(self.size_x)]

    def get_move(self):
        while len(self.watched_list) > 0:
            x, y = self.watched_list.pop()
            self.watched_board[x][y] = False
            mines = []
            unexplored = []
            for (dx, dy) in DIRECTIONS:
                if 0 <= x + dx < self.size_x and 0 <= y + dy < self.size_y:
                    if self.board[x + dx][y + dy] == FLAG:
                        mines.append((x + dx, y + dy))
                    elif self.board[x + dx][y + dy] == UNEXPLORED:
                        unexplored.append((x + dx, y + dy))
            if len(mines) == self.board[x][y] and len(unexplored) > 0:
                return unexplored
            elif len(mines) + len(unexplored) == self.board[x][y]:
                for (ux, uy) in unexplored:
                    self.flag(ux, uy)
        return []

    def add_watched(self, x, y):
        if not self.watched_board[x][y] and 1 <= self.board[x][y] <= 8:
            self.watched_list.append((x, y))
            self.watched_board[x][y] = True
