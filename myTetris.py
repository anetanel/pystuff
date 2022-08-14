import random

import pygame

# Define some UI colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)

# Figures colors
colors = [
    (0, 0, 0),
    (120, 37, 179),
    (100, 179, 179),
    (80, 34, 22),
    (80, 134, 22),
    (180, 34, 22),
    (180, 34, 122),
]


class Figure:
    x = 0
    y = 0

    figures = [
        [[1, 5, 9, 13], [4, 5, 6, 7]],
        [[4, 5, 9, 10], [2, 6, 5, 9]],
        [[6, 7, 9, 10], [1, 5, 6, 10]],
        [[1, 2, 5, 9], [0, 4, 5, 6], [1, 5, 9, 8], [4, 5, 6, 10]],
        [[1, 2, 6, 10], [5, 6, 7, 9], [2, 6, 10, 11], [3, 5, 6, 7]],
        [[1, 4, 5, 6], [1, 4, 5, 9], [4, 5, 6, 9], [1, 5, 6, 9]],
        [[1, 2, 5, 6]],
    ]

    def __init__(self, x, y):
        self.x = int(x)
        self.y = int(y)
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.randint(1, len(colors) - 1)
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])


class Tetris:
    height = 0
    width = 0
    block_size = 20
    x = 0
    y = 0
    field = []
    figure = None

    def __init__(self, width, height):
        self.height = height
        self.width = width
        self.field = [[0] * width for _ in range(height)]

    def new_figure(self):
        self.figure = Figure(self.width / 2 - 2, 0)

    def go_side(self, dx):
        old_x = self.figure.x
        self.figure.x += dx
        if self.intersects():
            self.figure.x = old_x

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            self.figure.rotation = old_rotation

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] > 0:
                        intersection = True
        return intersection

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.new_figure()

    def go_space(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()


def main():
    # Initialize game
    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(size=screen_size)
    pygame.display.set_caption("Tetris")
    game = Tetris(width=10, height=20)
    # set play-field to middle of screen horizontally
    game.x = int(screen_size[0] / 2 - (game.width / 2 * game.block_size))
    # set play-field to bottom + 3 rows vertically
    game.y = int(screen_size[1] - (game.height * game.block_size) - game.block_size * 3)
    done = False
    pressing_down = False
    clock = pygame.time.Clock()
    fps = 15

    # Main game loop
    while not done:

        if pressing_down:
            game.go_down()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # TODO: remove this
                    game.new_figure()
                elif event.key == pygame.K_LEFT:
                    game.go_side(-1)
                elif event.key == pygame.K_RIGHT:
                    game.go_side(1)
                elif event.key == pygame.K_DOWN:
                    pressing_down = True
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_SPACE:
                    game.go_space()
                elif event.key == pygame.K_q:
                    done = True
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        screen.fill(WHITE)
        # Draw play-field grid
        for y in range(game.height):
            for x in range(game.width):
                pygame.draw.rect(screen, GRAY, [game.x + game.block_size * x, game.y + (game.block_size * y),
                                                game.block_size, game.block_size], 1)
                if game.field[y][x] > 0:
                    pygame.draw.rect(screen, colors[game.field[y][x]],
                                     [game.x + (game.block_size * x) + 1, game.y + (game.block_size * y) + 1,
                                      game.block_size - 2, game.block_size - 2])

        # Draw active figure with 1px offset in respect to grid
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, colors[game.figure.color],
                                         [game.x + game.block_size * (j + game.figure.x) + 1,
                                          game.y + game.block_size * (i + game.figure.y) + 1,
                                          game.block_size - 2, game.block_size - 2])
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    main()
