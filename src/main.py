import random
import sys

import agent
import gui as _gui
from constants import (
    DIRECTIONS, FLAG, LEFT, LOSE, MINE, MINE_HIT, MOUSEWHEEL_DOWN, MOUSEWHEEL_UP, PLAYING, RIGHT, UNEXPLORED, WIN
)

import pygame
import pygame.locals

pygame.init()


class Minesweeper:
    def __init__(self, size_x, size_y, n_mines):
        self.size_x = size_x
        self.size_y = size_y
        self.n_mines = n_mines
        self.board = [[UNEXPLORED for _ in range(self.size_y)] for _ in range(self.size_x)]
        self.mines_board = [[0 for _ in range(self.size_y)] for _ in range(self.size_x)]
        self.started = False
        self.updated_cells = []
        self.n_revealed = 0
        self.status = PLAYING
        self.agent = agent.Agent(self)

    def get_adjacent_cells(self, x, y):
        adjacent_cells = []
        for dx, dy in DIRECTIONS:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size_x and 0 <= ny < self.size_y:
                adjacent_cells.append((nx, ny))
        return adjacent_cells

    def generate_mines(self, x, y):
        print(f"Random state is {random.getstate()}")
        if self.n_mines > self.size_x * self.size_y / 2:
            self.mines_board = [[MINE for _ in range(self.size_y)] for _ in range(self.size_x)]
            self.mines_board[x][y] = 0
            no_mines = [(x, y)]
            candidates = [(i, j) for i in range(self.size_x) for j in range(self.size_y)]
            candidates.remove((x, y))
            n_removed = 1
            if self.size_x * self.size_y - self.n_mines >= 9:
                for ax, ay in self.get_adjacent_cells(x, y):
                    self.mines_board[ax][ay] = 0
                    no_mines.append((ax, ay))
                    candidates.remove((ax, ay))
                    n_removed += 1
            for nx, ny in random.sample(candidates, self.size_x * self.size_y - self.n_mines - n_removed):
                self.mines_board[nx][ny] = 0
                no_mines.append((nx, ny))
            for nx, ny in no_mines:
                for ax, ay in self.get_adjacent_cells(nx, ny):
                    if self.mines_board[ax][ay] == MINE:
                        self.mines_board[nx][ny] += 1
        else:
            mines = []
            candidates = [(i, j) for i in range(self.size_x) for j in range(self.size_y)]
            candidates.remove((x, y))
            if self.size_x * self.size_y - self.n_mines >= 9:
                for ax, ay in self.get_adjacent_cells(x, y):
                    candidates.remove((ax, ay))
            for mx, my in random.sample(candidates, self.n_mines):
                self.mines_board[mx][my] = MINE
                mines.append((mx, my))
            for mx, my in mines:
                for ax, ay in self.get_adjacent_cells(mx, my):
                    if self.mines_board[ax][ay] != MINE:
                        self.mines_board[ax][ay] += 1

    def flag(self, x, y):
        self.updated_cells.append((x, y))
        if self.board[x][y] == UNEXPLORED:
            self.board[x][y] = FLAG
            for ax, ay in self.get_adjacent_cells(x, y):
                self.agent.add_watched(ax, ay)
        elif self.board[x][y] == FLAG:
            self.board[x][y] = UNEXPLORED

    def reveal(self, x, y):
        self.board[x][y] = self.mines_board[x][y]
        self.n_revealed += 1
        self.agent.add_watched(x, y)
        self.updated_cells.append((x, y))
        for ax, ay in self.get_adjacent_cells(x, y):
            self.agent.add_watched(ax, ay)

    def reveal_neighbors(self, x, y):
        stack = [(x, y)]
        self.reveal(x, y)
        while stack:
            x, y = stack.pop()
            for ax, ay in self.get_adjacent_cells(x, y):
                if self.board[ax][ay] == UNEXPLORED:
                    if self.mines_board[ax][ay] == 0:
                        stack.append((ax, ay))
                    self.reveal(ax, ay)

    def left_click_at(self, x, y):
        if self.status == PLAYING and self.board[x][y] == UNEXPLORED:
            if not self.started:
                self.generate_mines(x, y)
                if self.mines_board[x][y] == 0:
                    self.reveal_neighbors(x, y)
                else:
                    self.reveal(x, y)
                self.started = True
            elif self.mines_board[x][y] == MINE:
                for x2 in range(self.size_x):
                    for y2 in range(self.size_y):
                        self.reveal(x2, y2)
                self.status = LOSE
                self.board[x][y] = MINE_HIT
                print("You lost !")
            else:
                if self.mines_board[x][y] == 0:
                    self.reveal_neighbors(x, y)
                else:
                    self.reveal(x, y)

    def right_click_at(self, x, y):
        if self.status == PLAYING:
            self.flag(x, y)


def wait_for_close():
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()


def main():
    if len(sys.argv) < 3:
        print("Pass the width and height of the grid as parameters.")
        sys.exit(-1)
    size_x, size_y = int(sys.argv[1]), int(sys.argv[2])
    n_mines = round(0.1 * size_x * size_y)
    solver = False
    n_mines = min(max(1, n_mines), size_x * size_y - 1)
    minesweeper = Minesweeper(size_x, size_y, n_mines)
    gui = _gui.GUI(minesweeper)

    gui.draw()
    while True:
        minesweeper.updated_cells = []
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                lx, ly = pygame.mouse.get_pos()
                x, y = gui.convert_to_game_coord(lx, ly)
                if event.button == LEFT:
                    minesweeper.left_click_at(x, y)
                elif event.button == RIGHT:
                    minesweeper.right_click_at(x, y)
                elif event.button == MOUSEWHEEL_DOWN:
                    gui.zoom_out_at(lx, ly)
                elif event.button == MOUSEWHEEL_UP:
                    gui.zoom_in_at(lx, ly)
            elif event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_SPACE:
                    solver = not solver
        if solver and minesweeper.status == PLAYING:
            move = minesweeper.agent.get_cells_to_open()
            for x, y in move:
                minesweeper.left_click_at(x, y)
        if minesweeper.status == PLAYING and minesweeper.n_revealed == minesweeper.size_x * minesweeper.size_y - minesweeper.n_mines:
            minesweeper.status = WIN
            print("You won !")
        gui.update()


if __name__ == '__main__':
    main()
