"""
myTetris by Netanel Attali
Based on https://levelup.gitconnected.com/writing-tetris-in-python-2a16bddb5318

TODO:
* Add a frame around "Next Piece" - Done
* Use backgrounds:
    Make Play field semi-transparent - Done
    Resize bg to fit screen - Done
* Change music tempo
* Add new music?
"""

import random
from enum import Enum, auto
from typing import Tuple

import pygame
from pygame import mixer
import pygame_menu


class Colors(Enum):
    BLACK = (1, 1, 1)
    WHITE = (255, 255, 255, 220)
    GRAY = (128, 128, 128)
    COLOR_1 = (120, 37, 179)
    COLOR_2 = (100, 179, 179)
    COLOR_3 = (80, 34, 22)
    COLOR_4 = (80, 134, 22)
    COLOR_5 = (180, 34, 22)
    COLOR_6 = (180, 34, 122)
    COLOR_7 = (255, 125, 0)


# noinspection PyArgumentList
class Direction(Enum):
    DOWN = auto()
    LEFT = auto()
    RIGHT = auto()
    DROP = auto()
    ROTATE = auto()


# noinspection PyArgumentList
class GameState(Enum):
    RUNNING = auto()
    GAME_OVER = auto()
    PAUSE = auto()


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
    x = 0
    y = 0

    def __init__(self, width, height):
        self.block_size = int(SCREEN_WIDTH * 0.02)
        self.score = 0
        self.state = GameState.RUNNING
        self.height = height
        self.width = width
        self.field = [[Colors.WHITE] * width for _ in range(height)]
        self.figure = None
        self.next_figure = Figure()
        self.level = 1
        # set play-field to middle of screen horizontally
        self.x = SCREEN_WIDTH // 2 - (self.width // 2 * self.block_size)
        # set play-field to bottom + 3 rows vertically
        self.y = int(SCREEN_HEIGHT - (self.height * self.block_size) - self.block_size * 3)
        self.game_over = False

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
            sfx['nope'].play()
            self.figure.x = old_x
        else:
            sfx['move'].play()

    def go_down(self):
        self.figure.y += 1
        if self.intersects():
            self.figure.y -= 1
            self.freeze()

    def rotate(self):
        old_rotation = self.figure.rotation
        self.figure.rotate()
        if self.intersects():
            sfx['nope'].play()
            self.figure.rotation = old_rotation
        else:
            sfx['rotate'].play()

    def go_drop(self):
        while not self.intersects():
            self.figure.y += 1
        self.figure.y -= 1
        self.freeze()

    def find_ghost_y(self):
        ghost_y = self.figure.y
        while not self.intersects(ghost_y):
            ghost_y += 1
        return ghost_y - 1

    def intersects(self, figure_y=None):
        if not figure_y:
            figure_y = self.figure.y
        intersection = False
        for i in range(4):
            for j in range(4):
                if i * 4 + j in self.figure.image():
                    if i + figure_y > self.height - 1 or \
                            j + self.figure.x > self.width - 1 or \
                            j + self.figure.x < 0 or \
                            self.field[i + figure_y][j + self.figure.x] != Colors.WHITE:
                        intersection = True
        return intersection

    def freeze(self):
        sfx['drop'].play()
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
                sfx['break_line'].play()
                lines += 1
                for i1 in range(i, 1, -1):
                    self.field[i1] = self.field[i1 - 1].copy()
        self.score += lines ** 2
        self.level = self.score // 3 + 1

    def resize(self):
        self.block_size = int(SCREEN_WIDTH * 0.02)
        # set play-field to middle of screen horizontally
        self.x = SCREEN_WIDTH // 2 - (self.width // 2 * self.block_size)
        # set play-field to bottom + 3 rows vertically
        self.y = int(SCREEN_HEIGHT - (self.height * self.block_size) - self.block_size * 3)


def new_game():
    mixer.music.play(loops=-1)
    return Tetris(width=10, height=20)


def text_drop_shadow(font, message, offset, fontcolor, shadowcolor):
    base = font.render(message, 0, fontcolor)
    size = base.get_width() + offset, base.get_height() + offset
    img = pygame.Surface(size, pygame.SRCALPHA)
    base.set_palette_at(1, shadowcolor)
    img.blit(base, (offset, offset))
    base.set_palette_at(1, fontcolor)
    img.blit(base, (0, 0))
    return img


def main():
    def set_music_volume(value):
        pygame.mixer.music.set_volume(value / 10)

    def set_sfx_volume(value, play=True):
        for s in sfx.values():
            s.set_volume(value / 10)
        if play:
            sfx['game_over'].play()

    def toggle_grid(_=None):
        global draw_grid, next_rect
        draw_grid = not draw_grid
        settings_menu.get_widget(widget_id='grid_toggle').set_value(draw_grid)

    def toggle_ghost(_=None):
        global show_ghost
        show_ghost = not show_ghost
        settings_menu.get_widget(widget_id='ghost_toggle').set_value(show_ghost)

    def toggle_fullscreen(_=None):
        global fullscreen
        fullscreen = not fullscreen
        settings_menu.get_widget(widget_id='fullscreen_toggle').set_value(fullscreen)
        pygame.display.toggle_fullscreen()

    def change_window_size(selected: Tuple, new_width, new_height) -> None:
        global SCREEN_WIDTH
        global SCREEN_HEIGHT
        global screen
        global small_font
        global large_font
        global alpha_surface
        global bg
        SCREEN_WIDTH = new_width
        SCREEN_HEIGHT = new_height
        screen = new_screen()
        alpha_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        game.resize()
        small_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.02), True, False)
        large_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.1), True, False)
        create_menus(resize=True)
        bg = prepare_backgrounds()

    def new_screen():
        return pygame.display.set_mode(size=(SCREEN_WIDTH, SCREEN_HEIGHT))

    def create_menus(resize=False):
        global main_menu, settings_menu, help_menu, about_menu, quit_menu

        theme = pygame_menu.themes.THEME_DEFAULT.copy()
        theme.widget_font_size = int(SCREEN_HEIGHT * 0.045)
        theme.set_background_color_opacity(0.8)

        if resize:
            for menu in main_menu, settings_menu, help_menu, about_menu, quit_menu:
                menu.resize(width=SCREEN_WIDTH, height=SCREEN_HEIGHT)
                for widget in menu.get_widgets():
                    if isinstance(widget, pygame_menu.widgets.widget.toggleswitch.ToggleSwitch):
                        widget._state_text_font_size = None
                    widget.update_font({'size': int(SCREEN_HEIGHT * 0.045)})

            return

        main_menu = pygame_menu.Menu(
            center_content=True,
            height=SCREEN_HEIGHT,
            theme=theme,
            title='Tetris - Main Menu',
            width=SCREEN_WIDTH,
            onclose=pygame_menu.events.NONE,
            mouse_visible=False
        )

        about_menu = pygame_menu.Menu(
            center_content=True,
            height=main_menu.get_height(),
            mouse_visible=False,
            title='About',
            width=main_menu.get_width(),
            theme=main_menu.get_theme(),
            onclose=pygame_menu.events.BACK
        )
        for m in ABOUT:
            about_menu.add.label(m, margin=(0, 0))
        about_menu.add.label('')
        about_menu.add.button('Return to Menu', pygame_menu.events.BACK)

        help_menu = pygame_menu.Menu(
            center_content=True,
            height=main_menu.get_height(),
            mouse_visible=False,
            title='Help',
            width=main_menu.get_width(),
            theme=main_menu.get_theme(),
            onclose=pygame_menu.events.BACK
        )
        help_menu.add.label('Keys', underline=True, underline_width=5).set_font_shadow(enabled=True)
        for m in HELP:
            help_menu.add.label(m, align=pygame_menu.locals.ALIGN_LEFT)
        help_menu.add.label('')
        help_menu.add.button('Return to Menu', pygame_menu.events.BACK)

        settings_menu = pygame_menu.Menu(
            center_content=True,
            height=main_menu.get_height(),
            mouse_visible=False,
            title='Settings',
            width=main_menu.get_width(),
            theme=main_menu.get_theme(),
            onclose=pygame_menu.events.BACK
        )
        settings_menu.add.selector(title='Window Size: ', items=RESOLUTIONS, onchange=change_window_size)
        settings_menu.add.range_slider(title='Music Volume: ', default=MUSIC_DEFAULT, range_values=[*range(0, 11)],
                                       onchange=set_music_volume, range_text_value_enabled=False)
        settings_menu.add.range_slider(title='SFX Volume: ', default=SFX_DEFAULT, range_values=[*range(0, 11)],
                                       onchange=set_sfx_volume, range_text_value_enabled=False)
        settings_menu.add.toggle_switch(title="Full Screen", default=fullscreen, onchange=toggle_fullscreen,
                                        toggleswitch_id='fullscreen_toggle')
        settings_menu.add.toggle_switch(title="Grid", default=draw_grid, onchange=toggle_grid,
                                        toggleswitch_id='grid_toggle')
        settings_menu.add.toggle_switch(title="Ghost Piece", default=show_ghost, onchange=toggle_ghost,
                                        toggleswitch_id='ghost_toggle')
        settings_menu.add.label('')
        settings_menu.add.button('Return to Menu', pygame_menu.events.BACK)

        quit_menu = pygame_menu.Menu(
            center_content=True,
            height=main_menu.get_height(),
            mouse_visible=False,
            title='Quit?',
            width=main_menu.get_width(),
            theme=main_menu.get_theme(),
            onclose=pygame_menu.events.BACK
        )
        quit_menu.add.label('Do you want to quit?')
        quit_menu.add.button('NO', pygame_menu.events.BACK)
        quit_menu.add.button('YES', pygame_menu.events.EXIT)

        main_menu.add.button('Play', main_menu.disable)
        main_menu.add.button(settings_menu.get_title(), settings_menu)
        main_menu.add.button(help_menu.get_title(), help_menu)
        main_menu.add.button(about_menu.get_title(), about_menu)
        main_menu.add.button(quit_menu.get_title(), quit_menu)

    # Initialize game
    global fullscreen
    global draw_grid
    global show_ghost
    global screen
    global SCREEN_WIDTH
    global SCREEN_HEIGHT
    global alpha_surface
    screen = new_screen()
    alpha_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    pygame.display.set_caption("Tetris")
    game = new_game()
    clock = pygame.time.Clock()
    done = False
    pressing_down = False
    fps = 25
    counter = 0
    next_rect = None

    set_music_volume(MUSIC_DEFAULT)
    set_sfx_volume(SFX_DEFAULT, play=False)

    # Create menus
    global main_menu
    global settings_menu
    global help_menu
    global about_menu
    create_menus()
    main_menu.enable()

    # Text
    global small_font
    global large_font
    small_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.02), True, False)
    large_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.1), True, False)

    # Main game loop
    while not done:
        if game.figure is None:
            game.new_figure()
        counter += 1
        if counter > 100000:
            counter = 0

        if (counter % (fps // game.level) == 0 or pressing_down) and not main_menu.is_enabled():
            game.move(Direction.DOWN)

        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                done = True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and not main_menu.is_enabled():
                    game.move(Direction.LEFT)
                elif event.key == pygame.K_RIGHT and not main_menu.is_enabled():
                    game.move(Direction.RIGHT)
                elif event.key == pygame.K_DOWN and not main_menu.is_enabled():
                    pressing_down = True
                elif event.key == pygame.K_UP and not main_menu.is_enabled():
                    game.move(Direction.ROTATE)
                elif event.key == pygame.K_SPACE and not main_menu.is_enabled():
                    game.move(Direction.DROP)
                elif event.key == pygame.K_p and not main_menu.is_enabled():
                    sfx['pause'].play()
                    if game.state == GameState.RUNNING:
                        game.state = GameState.PAUSE
                        mixer.music.pause()
                    elif game.state == GameState.PAUSE:
                        game.state = GameState.RUNNING
                        mixer.music.unpause()
                elif event.key == pygame.K_ESCAPE:
                    if main_menu.is_enabled():
                        if main_menu.get_current() == main_menu:
                            main_menu.disable()
                        else:
                            main_menu.get_current().close()
                            main_menu.enable()
                    else:
                        main_menu.enable()
                elif event.key == pygame.K_r:
                    game = new_game()
                elif event.key == pygame.K_g:
                    toggle_grid()
                elif event.key == pygame.K_h:
                    toggle_ghost()
                elif event.key == pygame.K_f:
                    toggle_fullscreen()

            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    pressing_down = False

        # Prepare frame
        screen.fill("white")
        screen.blit(bg[(game.level - 1) % len(bg)], (0, 0))
        screen.blit(alpha_surface, (0, 0))

        # Draw play-field
        play_field_rect = pygame.draw.rect(alpha_surface, Colors.WHITE.value,
                                           [game.x - 1, game.y, game.block_size * game.width + 2,
                                            game.block_size * game.height + 2])
        pygame.draw.rect(screen, Colors.GRAY.value, play_field_rect, 1)

        for y in range(game.height):
            for x in range(game.width):
                # Draw grid
                if draw_grid:
                    pygame.draw.rect(screen, Colors.GRAY.value,
                                     [game.x + game.block_size * x + 1, game.y + (game.block_size * y),
                                      game.block_size, game.block_size], 1)
                # Draw frozen figures
                if game.field[y][x] != Colors.WHITE:
                    pygame.draw.rect(screen, game.field[y][x].value,
                                     [game.x + (game.block_size * x) + 1, game.y + (game.block_size * y) + 1,
                                      game.block_size - 1, game.block_size - 1])

        # Draw Next Figure frame
        next_rect = pygame.draw.rect(alpha_surface, Colors.WHITE.value,
                                     [game.x - game.block_size * 10, game.y, game.block_size * 6,
                                      game.block_size * 6])
        pygame.draw.rect(screen, "red4", next_rect, 5)

        # Draw active figure with 1px offset in respect to grid
        if game.figure is not None:
            for i in range(4):
                for j in range(4):
                    p = i * 4 + j
                    if p in game.figure.image():
                        pygame.draw.rect(screen, game.figure.color.value,
                                         [game.x + game.block_size * (j + game.figure.x) + 1,
                                          game.y + game.block_size * (i + game.figure.y) + 1,
                                          game.block_size - 1, game.block_size - 1])
                        # Draw "ghost" figure
                        if show_ghost:
                            pygame.draw.rect(screen, pygame.Color("red"),
                                             [game.x + game.block_size * (j + game.figure.x) + 1,
                                              game.y + game.block_size * (i + game.find_ghost_y()) + 1,
                                              game.block_size - 2, game.block_size - 2], 1)

                    # Draw next figure preview
                    if p in game.next_figure.image():
                        pygame.draw.rect(screen, game.next_figure.color.value,
                                         [game.block_size * (j + game.next_figure.x)
                                          + next_rect.centerx - game.block_size * 2,
                                          game.block_size * (i + game.next_figure.y)
                                          + next_rect.centery - game.block_size * 2,
                                          game.block_size - 1, game.block_size - 1])

        # Blit text
        if game.state == GameState.GAME_OVER:
            if not game.game_over:
                mixer.music.stop()
                sfx['game_over'].play()
                game.game_over = True
            text_game_over1 = large_font.render("Game Over", True, Colors.WHITE.value, Colors.BLACK.value)
            text_game_over2 = small_font.render("Press 'r' to Restart...", True, Colors.WHITE.value, Colors.BLACK.value)
            screen.blit(text_game_over1, text_game_over1.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
            screen.blit(text_game_over2, text_game_over2.get_rect(
                center=(SCREEN_WIDTH / 2,
                        SCREEN_HEIGHT / 2 + text_game_over1.get_size()[1] / 2 + text_game_over2.get_size()[1] / 2)
            ))
        if game.state == GameState.PAUSE:
            text_pause = large_font.render("PAUSE", True, Colors.BLACK.value, Colors.GRAY.value)
            screen.blit(text_pause, text_pause.get_rect(center=(SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2)))
        text_score = text_drop_shadow(small_font, "Score: " + str(game.score), 5, Colors.WHITE.value,
                                      Colors.BLACK.value)
        text_level = text_drop_shadow(small_font, "Level: " + str(game.level), 5, Colors.WHITE.value,
                                      Colors.BLACK.value)
        text_help = text_drop_shadow(small_font, "<ESC>: Menu", 5, Colors.WHITE.value, Colors.BLACK.value)
        text_next_piece = text_drop_shadow(small_font, "Next:", 5, pygame.color.Color("red"),
                                           pygame.color.Color("black"))
        screen.blit(text_score, [0, 0])
        screen.blit(text_level, [0, text_score.get_size()[1] * 1.5])
        screen.blit(text_help, [0, SCREEN_HEIGHT - text_help.get_size()[1]])
        screen.blit(text_next_piece, [next_rect.x, next_rect.y - text_next_piece.get_height()])

        # Draw menu
        if main_menu.is_enabled():
            main_menu.update(events)
            if main_menu.is_enabled():
                main_menu.draw(screen)

        pygame.display.flip()
        clock.tick(fps)

    pygame.quit()


__version__ = '0.1'
__author__ = 'Netanel Attali'
__email__ = 'netanel.attali@gmail.com'
__title__ = 'myTetris'

pygame.init()
mixer.music.load('sound/tetris-music.mp3')
sfx = {
    'move': mixer.Sound('sound/move.mp3'),
    'rotate': mixer.Sound('sound/rotate.mp3'),
    'drop': mixer.Sound('sound/drop.mp3'),
    'game_over': mixer.Sound('sound/game_over.mp3'),
    'break_line': mixer.Sound('sound/break_line.mp3'),
    'nope': mixer.Sound('sound/nope2.mp3'),
    'pause': mixer.Sound('sound/pause.mp3')
}

SCREEN_WIDTH = pygame.display.Info().current_w
SCREEN_HEIGHT = pygame.display.Info().current_h

global main_menu
global settings_menu
global help_menu
global about_menu
global quit_menu

ABOUT = [f'{__title__} {__version__}',
         f'Author: {__author__}',
         '',
         f'Email: {__email__}']

HELP = ['ESC : Main Menu',
        'R : Restart Game',
        'P : Pause Game',
        'F : Toggle Full Screen',
        'G : Toggle Grid',
        'H : Toggle "Ghost" Piece',
        'LEFT/RIGHT/DOWN : Move Piece',
        'UP : Rotate Piece',
        'SPACE : Drop Piece'
        ]

draw_grid = False
show_ghost = False
fullscreen = False

MUSIC_DEFAULT = 6
SFX_DEFAULT = 7

RESOLUTIONS = [('Full Screen Resolution', SCREEN_WIDTH, SCREEN_HEIGHT),
               ('800x600', 800, 600),
               ('1024x768', 1024, 768),
               ('1366x768', 1366, 768),
               ('1440x900', 1440, 900),
               ('1920x1080', 1920, 1080),
               ('2560x1440', 2560, 1440)]
screen = None
alpha_surface = None
small_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.02), True, False)
large_font = pygame.font.SysFont('Calibri', int(SCREEN_WIDTH * 0.1), True, False)


def prepare_backgrounds():
    return [pygame.transform.scale(pygame.image.load('images/bg1.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            pygame.transform.scale(pygame.image.load('images/bg2.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            pygame.transform.scale(pygame.image.load('images/bg3.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT)),
            pygame.transform.scale(pygame.image.load('images/bg4.jpg'), (SCREEN_WIDTH, SCREEN_HEIGHT))]


bg = prepare_backgrounds()

if __name__ == '__main__':
    main()
