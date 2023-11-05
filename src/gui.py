import math
import os

import pygame


class GUI:
    def __init__(self, minesweeper):
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        pygame.init()
        self.minesweeper = minesweeper
        self.size_x, self.size_y = self.minesweeper.size_x, self.minesweeper.size_y
        width = pygame.display.Info().current_w / 2
        height = pygame.display.Info().current_h / 2
        self.size_case = 1
        max_size_case = 128
        while self.size_case * self.size_x <= width and self.size_case * self.size_y <= height and self.size_case < max_size_case:
            self.size_case *= 2
        self.res_x, self.res_y = self.size_case * self.size_x, self.size_case * self.size_y
        self.zoom = 1
        self.zoom_max = max_size_case / self.size_case
        self.zoom_pos = self.res_x / 2, self.res_y / 2
        self.sprites = []
        for i in range(0, int(math.log2(max_size_case / self.size_case)) + 1):
            s = []
            for j in range(9):
                sprite = pygame.image.load(f"../res/{j}.png")
                sprite = pygame.transform.scale(sprite, (self.size_case * 2 ** i, self.size_case * 2 ** i))
                s.append(sprite)
            sprite = pygame.image.load("../res/unexplored.png")
            sprite = pygame.transform.scale(sprite, (self.size_case * 2 ** i, self.size_case * 2 ** i))
            s.append(sprite)
            sprite = pygame.image.load("../res/flag.png")
            sprite = pygame.transform.scale(sprite, (self.size_case * 2 ** i, self.size_case * 2 ** i))
            s.append(sprite)
            sprite = pygame.image.load("../res/mine.png")
            sprite = pygame.transform.scale(sprite, (self.size_case * 2 ** i, self.size_case * 2 ** i))
            s.append(sprite)
            sprite = pygame.image.load("../res/mine_hit.png")
            sprite = pygame.transform.scale(sprite, (self.size_case * 2 ** i, self.size_case * 2 ** i))
            s.append(sprite)
            self.sprites.append(s)

        self.display = pygame.display.set_mode((self.res_x, self.res_y))
        pygame.display.set_caption("Minesweeper")

    def convert_to_global_coord(self, lx, ly):
        if self.zoom == 1:
            return lx, ly
        else:
            zx, zy = self.zoom_pos
            return zx + (lx - self.res_x / 2) / self.zoom, zy + (ly - self.res_y / 2) / self.zoom

    def convert_to_game_coord(self, lx, ly):
        gx, gy = self.convert_to_global_coord(lx, ly)
        return int(gx / self.size_case), int(gy / self.size_case)

    def convert_to_local_coord(self, x, y):
        if self.zoom == 1:
            return x * self.size_case * self.zoom, y * self.size_case * self.zoom
        else:
            zx, zy = self.zoom_pos
            gx, gy = x * self.size_case, y * self.size_case
            return self.res_x / 2 + (gx - zx) * self.zoom, self.res_y / 2 + (gy - zy) * self.zoom

    def zoom_in_at(self, lx, ly):
        if self.zoom < self.zoom_max:
            gx, gy = self.convert_to_global_coord(lx, ly)
            self.zoom_pos = gx, gy
            self.zoom *= 2
            gx2, gy2 = self.convert_to_global_coord(lx, ly)
            gx2, gy2 = gx + 0.75 * (gx - gx2), gy + 0.75 * (gy - gy2)
            gx2 = max(gx2, self.res_x / (2 * self.zoom))
            gx2 = min(gx2, self.res_x - self.res_x / (2 * self.zoom))
            gy2 = max(gy2, self.res_y / (2 * self.zoom))
            gy2 = min(gy2, self.res_y - self.res_y / (2 * self.zoom))
            self.zoom_pos = gx2, gy2
            self.draw()

    def zoom_out_at(self, lx, ly):
        if self.zoom > 1:
            gx, gy = self.convert_to_global_coord(lx, ly)
            self.zoom_pos = gx, gy
            self.zoom = int(self.zoom / 2)
            gx2, gy2 = self.convert_to_global_coord(lx, ly)
            gx2, gy2 = gx + 0.75 * (gx - gx2), gy + 0.75 * (gy - gy2)
            gx2 = max(gx2, self.res_x / (2 * self.zoom))
            gx2 = min(gx2, self.res_x - self.res_x / (2 * self.zoom))
            gy2 = max(gy2, self.res_y / (2 * self.zoom))
            gy2 = min(gy2, self.res_y - self.res_y / (2 * self.zoom))
            self.zoom_pos = gx2, gy2
            self.draw()

    def update(self):
        if self.zoom == 1:
            for x, y in self.minesweeper.updated_cells:
                self.display.blit(self.sprites[0][self.minesweeper.board[x][y]], (x * self.size_case, y * self.size_case))
        else:
            sprites = self.sprites[int(math.log2(self.zoom))]
            lb_x, lb_y = self.convert_to_game_coord(0, 0)
            ub_x, ub_y = self.convert_to_game_coord(int(self.res_x - 1), int(self.res_y - 1))
            for x, y in self.minesweeper.updated_cells:
                if lb_x <= x <= ub_x and lb_y <= y <= ub_y:
                    lx, ly = self.convert_to_local_coord(x, y)
                    self.display.blit(sprites[self.minesweeper.board[x][y]], (lx, ly))
        pygame.display.update()

    def draw(self):
        if self.zoom == 1:
            for x in range(self.size_x):
                for y in range(self.size_y):
                    self.display.blit(self.sprites[0][self.minesweeper.board[x][y]], (x * self.size_case, y * self.size_case))
        else:
            sprites = self.sprites[int(math.log2(self.zoom))]
            lb_x, lb_y = self.convert_to_game_coord(0, 0)
            ub_x, ub_y = self.convert_to_game_coord(self.res_x - 1, self.res_y - 1)
            for x in range(lb_x, ub_x + 1):
                for y in range(lb_y, ub_y + 1):
                    lx, ly = self.convert_to_local_coord(x, y)
                    self.display.blit(sprites[self.minesweeper.board[x][y]], (lx, ly))
        pygame.display.update()
