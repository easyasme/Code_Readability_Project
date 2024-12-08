import pygame
import src.theme as T


class GridField:
    def __init__(
        self,
        width_px, height_px,
        block_size,
        off_l=0, off_r=0,
        off_u=0, off_d=0
    ):
        self.width = (width_px - off_l - off_r) // block_size
        self.height = (height_px - off_u - off_d) // block_size + 1
        self.height_px = height_px
        self.width_px = width_px
        self.off_l = off_l
        self.off_r = off_r
        self.off_u = off_u
        self.off_d = off_d
        self.block_size = block_size

        new_field = []
        for _ in range(0, self.height):
            new_field.append([0] * (self.width))

        self.field = new_field

    def get_elem(self, x, y):
        return self.field[y][x]

    def set_elem(self, x, y, val):
        self.field[y][x] = val

    def is_empty(self, x, y):
        if x >= self.width or x < 0 or y >= self.height or y < 0:
            return False
        return self.field[y][x] == 0

    def draw(self, window, opt=0, bg_c=(255, 255, 255), grid_c=(192, 192, 192)):
        y_max = 0
        x_max = 0
        if opt == 1:
            rect = pygame.Rect(self.off_l - self.block_size // 2, self.off_u - self.block_size // 2,
                               self.width_px + self.block_size - self.off_r - self.off_l, self.height_px -
                               self.off_d - self.off_u + self.block_size)
            pygame.draw.rect(window, bg_c, rect)
            pygame.draw.rect(window, grid_c, rect, 1)

        for y in range(self.off_u, self.height_px - self.off_d, self.block_size):
            for x in range(self.off_l, self.width_px - self.off_r, self.block_size):
                xidx = (x - self.off_l) // self.block_size
                yidx = (y - self.off_u) // self.block_size

                if self.is_empty(xidx, yidx):
                    c = bg_c
                else:
                    c = self.get_elem(xidx, yidx)

                rect = pygame.Rect(x, y, self.block_size, self.block_size)

                if self.is_empty(xidx, yidx) and opt == 0 or not self.is_empty(xidx, yidx):
                    pygame.draw.rect(window, c, rect)
                    pygame.draw.rect(window, grid_c, rect, 1)

    def draw_tetronimo(self, window, tet, grid_c="grey"):
        squares = tet.get()
        for (sy, sx) in squares:
            rect = pygame.Rect((tet.x + sx) * self.block_size + self.off_l, (tet.y + sy)
                               * self.block_size + self.off_u, self.block_size, self.block_size)
            pygame.draw.rect(window, tet.color, rect)
            pygame.draw.rect(window, T.Color().get(grid_c), rect, 1)

    def clear_line(self, idx):
        self.field.remove(self.field[idx])

    def insert_line(self, idx, line):
        self.field.insert(idx, line)

    def clear(self):
        self.field = []
        for y in range(0, self.height):
            self.field.append([0] * (self.width))


class Screen:
    game = []
    hold = []
    queue = []
    window = None

    def __init__(self, width, height, block_size, theme):
        self.width = width
        self.height = height
        self.theme = theme
        self.window = pygame.display.set_mode((width, height))
        self.block_size = block_size

        self.game = GridField(width, height, block_size, int(width*(1/4)),
                              int(width*(1/4)), int(height*(5/80)), int(height*(5/80)))

        self.hold = GridField(width, height, block_size, block_size,
                              int(width * (3/4)) + block_size, int(height*(1/5)), int(height*(4/5)) - block_size*6)

        self.queue = GridField(width, height, block_size, int(width * (3/4)) + block_size,
                               block_size, int(height*(5/80)), int(height*(75/80) - block_size*15))

    def is_empty(self, x, y):
        if x >= self.game.width or x < 0 or y >= self.game.height or y < 0:
            return False

        return self.game.get_elem(x, y) == 0

    def try_update(self, T):
        squares = T.get()
        for (sy, sx) in squares:
            (x, y) = (sx + T.x, sy + T.y)
            if x < 0 or x >= self.game.width or y < 0 or y >= self.game.height:
                return False

        for (sy, sx) in squares:
            (x, y) = (sx + T.x, sy + T.y)
            self.game.set_elem(x, y, T.color)
        return True

    def clear_lines(self):
        lines = 0
        height = self.game.height
        width = self.game.width

        for y in range(0, height):
            square_count = 0
            for x in range(0, width):
                if not self.game.is_empty(x, y):
                    square_count += 1
            if square_count == width:
                self.game.clear_line(y)
                self.game.insert_line(0, [0] * (width))
                lines += 1

        return lines

    def update_hold(self, T):
        squares = T.get()
        self.hold.clear()
        for (sy, sx) in squares:
            (x, y) = (sx, sy + 1)
            self.hold.set_elem(x, y, T.color)

    def update_queue(self, queue):
        self.queue.clear()
        ty = 1
        ty_n = ty
        for i, T in enumerate(queue):
            for (sy, sx) in T.get():
                (x, y) = (sx, sy + ty)
                ty_n = max(ty_n, y)
                self.queue.set_elem(x, y, T.color)
            ty = ty_n + 2

    def try_shift(self, t):
        squares = t.get()
        w = self.game.width
        dx = 0
        left = False

        for (sy, sx) in squares:
            if t.x + sx >= w:
                dx = max((t.x + sx + 1) - w, dx)
                left = True
            if t.x + sx < 0:
                dx = max(sx - t.x, dx)
        if left:
            dx = -dx
        if dx != 0:
            t.shift(dx)
            return True
        return False

    def draw(self, tet, ghost_tet, s, level):
        self.window.fill(self.theme.get_bg_color())
        self.game.draw(self.window, 0, self.theme.get_bg_color())
        self.game.draw_tetronimo(self.window, ghost_tet)
        self.game.draw_tetronimo(self.window, tet)
        self.queue.draw(self.window, 1, self.theme.get_bg_color())
        self.hold.draw(self.window, 1, self.theme.get_bg_color())
        pygame.display.set_caption("Tetris")

        self.draw_text("Score: " + str(s), self.theme.get_text_color(),
                       20, (self.block_size, self.block_size))
        self.draw_text("Level: " + str(level), self.theme.get_text_color(),
                       20, (self.block_size, self.block_size * 2))

    def draw_menu(self, select, state):
        s = pygame.Surface((self.width, self.height))
        s.set_alpha(10)
        s.fill(self.theme.get_menu_color())
        self.window.blit(s, (0, 0))

        for i, opt in enumerate(select.options.values()):
            color = self.theme.get_text_color(
                select.get() == opt, state == "initial" and opt == "resume")

            text = self.theme.text_format(select.getText(opt), 75, color, True)
            rect = text.get_rect()
            self.window.blit(text, (self.width/2 - (rect[2]/2), 300 + i*100))

        title = self.theme.text_format(
            "Tetris", 90, T.Color().get("FBF8CC"), True)
        rect = title.get_rect()
        self.window.blit(title, (self.width/2 - (rect[2]/2), 80))
        pygame.display.update()

    def draw_text(self, text, color, size, coordiantes):
        t = self.theme.text_format(text, size, color, False)
        self.window.blit(t, coordiantes)
