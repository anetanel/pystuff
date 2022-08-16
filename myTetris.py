import random
from enum import Enum

import pygame

# # Define some UI colors
# BLACK = (0, 0, 0)
# WHITE = (255, 255, 255)
# GRAY = (128, 128, 128)
#
# # Figures colors
# colors = [
#     (0, 0, 0),
#     (120, 37, 179),
#     (100, 179, 179),
#     (80, 34, 22),
#     (80, 134, 22),
#     (180, 34, 22),
#     (180, 34, 122),
# ]


class Colors(Enum):
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    GRAY = (128, 128, 128)
    COLOR_1 = (120, 37, 179)
    COLOR_2 = (100, 179, 179)
    COLOR_3 = (80, 34, 22)
    COLOR_4 = (80, 134, 22)
    COLOR_5 = (180, 34, 22)
    COLOR_6 = (180, 34, 122)


class Direction(Enum):
    DOWN = 1
    LEFT = 2
    RIGHT = 3
    DROP = 4
    ROTATE = 5


class GameState(Enum):
    RUNNING = 1
    GAME_OVER = 2


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

    def __init__(self):
        self.set_position(0, 0)
        self.type = random.randint(0, len(self.figures) - 1)
        self.color = random.choice([i for i in Colors if i not in [Colors.WHITE, Colors.GRAY]])
        self.rotation = 0

    def image(self):
        return self.figures[self.type][self.rotation]

    def rotate(self):
        self.rotation = (self.rotation + 1) % len(self.figures[self.type])

    def set_position(self, x, y):
        self.x = x
        self.y = y


class Tetris:
    height = 0
    width = 0
    block_size = 20
    x = 0
    y = 0
    field = []
    figure = None
    next_figure = None

    def __init__(self, width, height):
        self.state = GameState.RUNNING
        self.height = height
        self.width = width
        self.field = [[Colors.WHITE] * width for _ in range(height)]
        self.figure = None
        self.next_figure = Figure()

    def new_figure(self):
        self.figure = self.next_figure
        self.figure.set_position(self.width // 2 - 2, 0)
        self.next_figure = Figure()

    def move(self, direction: Direction):
        if self.state != GameState.RUNNING:
            return

        match direction:
            case Direction.DOWN:
                self.go_down()
            case Direction.DROP:
                self.go_drop()
            case Direction.ROTATE:
                self.rotate()
            case Direction.LEFT:
                self.go_side(-1)
            case Direction.RIGHT:
                self.go_side(1)

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

    def go_drop(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def intersects(self):
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + self.figure.y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + self.figure.y][j + self.figure.x] != Colors.WHITE:
                        intersection = True
        return intersection

    def freeze(self):
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    self.field[i + self.figure.y][j + self.figure.x] = self.figure.color
        self.break_lines()
        self.new_figure()
        if self.intersects():
            self.state = GameState.GAME_OVER

    def break_lines(self):
        lines = 0
        for i in range(1, self.height):
            if Colors.WHITE not in self.field[i]:
                lines += 1
                for i1 in range(i, 1, -1):
                    self.field[i1] = self.field[i1 - 1]


def main():
    # Initialize game
    pygame.init()
    screen_size = (800, 600)
    screen = pygame.display.set_mode(size=screen_size, flags=pygame.SCALED)
    pygame.display.set_caption("Tetris")
    game = Tetris(width=10, height=20)
    # set play-field to middle of screen horizontally
    game.x = screen_size[0] // 2 - (game.width // 2 * game.block_size)
    # set play-field to bottom + 3 rows vertically
    game.y = screen_size[1] - (game.height * game.block_size) - game.block_size * 3
    done = False
    pressing_down = False
    clock = pygame.time.Clock()
    fps = 15
    counter = 0

    # Text
    font1 = pygame.font.SysFont('Calibri', 65, True, False)
    text_game_over = font1.render("Game Over", True, (255, 125, 0))

    # Main game loop
    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if counter % fps == 0 or pressing_down:
            game.move(Direction.DOWN)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_n:  # TODO: remove this
                    game.new_figure()
                elif event.key == pygame.K_LEFT:
                    game.move(Direction.LEFT)
                elif event.key == pygame.K_RIGHT:
                    game.move(Direction.RIGHT)
                elif event.key == pygame.K_DOWN:
                    pressing_down = True
                elif event.key == pygame.K_UP:
                    game.move(Direction.ROTATE)
                elif event.key == pygame.K_SPACE:
                    game.move(Direction.DROP)
                elif event.key == pygame.K_q:
                    done = True
                elif event.key == pygame.K_ESCAPE:
                    game.__init__(width=10, height=20)
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        # Prepare frame
        screen.fill(Colors.WHITE.value)

        # Draw play-field
        for y in range(game.height):
            for x in range(game.width):
                # Draw grid
                pygame.draw.rect(screen, Colors.GRAY.value, [game.x + game.block_size * x, game.y + (game.block_size * y),
                                                game.block_size, game.block_size], 1)
                # Draw frozen figures
                # if game.field[y][x] != Colors.WHITE.name:
                pygame.draw.rect(screen, game.field[y][x].value,
                                 [game.x + (game.block_size * x) + 1, game.y + (game.block_size * y) + 1,
                                  game.block_size - 2, game.block_size - 2])

        # Draw active figure with 1px offset in respect to grid
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, game.figure.color.value,
                                         [game.x + game.block_size * (j + game.figure.x) + 1,
                                          game.y + game.block_size * (i + game.figure.y) + 1,
                                          game.block_size - 2, game.block_size - 2])
                    # Draw next figure preview
                    if p in game.next_figure.image():
                        pygame.draw.rect(screen, game.next_figure.color.value,
                                         [game.block_size * (j + game.next_figure.x) + game.block_size * 2,
                                          game.block_size * (i + game.next_figure.y) + game.block_size * 2,
                                          game.block_size - 1, game.block_size - 1])

        if game.state == GameState.GAME_OVER:
            screen.blit(text_game_over, [20, 200])
            # screen.blit(text_game_over1, [25, 265])
        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


if __name__ == '__main__':
    main()
