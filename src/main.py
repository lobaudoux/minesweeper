import math
import pygame
import random
import sys
from agent import *
from constants import *
from gui import *
from pygame.locals import *

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
        self.agent = Agent(self)

    def generate_mines(self, x, y):
        if self.n_mines > self.size_x*self.size_y/2:
            self.mines_board = [[MINE for _ in range(self.size_y)] for _ in range(self.size_x)]
            self.mines_board[x][y] = 0
            no_mines = [(x, y)]
            candidates = [(i, j) for i in range(self.size_x) for j in range(self.size_y)]
            candidates.remove((x, y))
            n_removed = 1
            if self.size_x*self.size_y-self.n_mines >= 9:
                for (dx, dy) in DIRECTIONS:
                    if 0 <= x+dx < self.size_x and 0 <= y+dy < self.size_y:
                        self.mines_board[x+dx][y+dy] = 0
                        no_mines.append((x+dx, y+dy))
                        candidates.remove((x+dx, y+dy))
                        n_removed += 1
            for nx, ny in random.sample(candidates, self.size_x*self.size_y-self.n_mines-n_removed):
                self.mines_board[nx][ny] = 0
                no_mines.append((nx, ny))
            for nx, ny in no_mines:
                for (dx, dy) in DIRECTIONS:
                    if 0 <= nx+dx < self.size_x and 0 <= ny+dy < self.size_y and self.mines_board[nx+dx][ny+dy] == MINE:
                        self.mines_board[nx][ny] += 1
        else:
            mines = []
            candidates = [(i, j) for i in range(self.size_x) for j in range(self.size_y)]
            candidates.remove((x, y))
            if self.size_x*self.size_y-self.n_mines >= 9:
                for (dx, dy) in DIRECTIONS:
                    if 0 <= x+dx < self.size_x and 0 <= y+dy < self.size_y:
                        candidates.remove((x+dx, y+dy))
            for mx, my in random.sample(candidates, self.n_mines):
                self.mines_board[mx][my] = MINE
                mines.append((mx, my))
            for mx, my in mines:
                for (dx, dy) in DIRECTIONS:
                    if 0 <= mx+dx < self.size_x and 0 <= my+dy < self.size_y and self.mines_board[mx+dx][my+dy] != MINE:
                        self.mines_board[mx+dx][my+dy] += 1

    def flag(self, x, y):
        self.updated_cells.append((x, y))
        if self.board[x][y] == UNEXPLORED:
            self.board[x][y] = FLAG
            for (dx, dy) in DIRECTIONS:
                if 0 <= x+dx < self.size_x and 0 <= y+dy < self.size_y:
                    self.agent.add_watched(x+dx, y+dy)
        elif self.board[x][y] == FLAG:
            self.board[x][y] = UNEXPLORED

    def reveal(self, x, y):
        self.board[x][y] = self.mines_board[x][y]
        self.n_revealed += 1
        self.agent.add_watched(x, y)
        self.updated_cells.append((x, y))
        for (dx, dy) in DIRECTIONS:
            if 0 <= x+dx < self.size_x and 0 <= y+dy < self.size_y:
                self.agent.add_watched(x+dx, y+dy)

    def reveal_neighbors(self, x, y):
        stack = [(x, y)]
        self.reveal(x, y)
        while stack:
            x, y = stack.pop()
            for (dx, dy) in DIRECTIONS:
                if 0 <= x+dx < self.size_x and 0 <= y+dy < self.size_y:
                    if self.board[x+dx][y+dy] == UNEXPLORED:
                        if self.mines_board[x+dx][y+dy] == 0:
                            stack.append((x+dx, y+dy))
                        self.reveal(x+dx, y+dy)

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
            if event.type == QUIT:
                pygame.quit()
                sys.exit()


def main():
    if len(sys.argv) < 3:
        print("Pass the width and height of the grid as parameters.")
        sys.exit(-1)
    size_x, size_y = int(sys.argv[1]), int(sys.argv[2])
    n_mines = round(0.1 * size_x * size_y)
    solver = False
    n_mines = min(max(1, n_mines), size_x*size_y-1)
    minesweeper = Minesweeper(size_x, size_y, n_mines)
    gui = GUI(minesweeper)

    gui.draw()
    while True:
        # pygame.time.Clock().tick(fps)
        minesweeper.updated_cells = []
        for event in pygame.event.get():
            if event.type == QUIT:
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
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    solver = not solver
        if solver and minesweeper.status == PLAYING:
            move = minesweeper.agent.get_move()
            for (x, y) in move:
                minesweeper.left_click_at(x, y)
        if minesweeper.status == PLAYING and minesweeper.n_revealed == minesweeper.size_x*minesweeper.size_y - minesweeper.n_mines:
            minesweeper.status = WIN
            print("You won !")
        gui.update()


if __name__ == '__main__':
    main()
