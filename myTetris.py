import pygame

# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (128, 128, 128)


def main():
    done = False
    pygame.init()
    size = (400, 500)
    screen = pygame.display.set_mode(size)
    screen.fill(WHITE)
    pygame.display.set_caption("Tetris")

    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True
        pygame.display.flip()

    pygame.quit()


if __name__ == '__main__':
    main()
