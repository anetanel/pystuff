"""
example non-animated entry for the pygame text contest

if you would like to change this for your own entry, modify
the first function that renders the text. you'll also probably
want to change the arguments that your function used. simply
running the script should show some sort of example for your
text rendering
"""
import os, sys, pygame, pygame.font, pygame.image
from pygame.locals import *


def textDropShadow(font, message, offset, fontcolor, shadowcolor):
    base = font.render(message, 0, fontcolor)
    size = base.get_width() + offset, base.get_height() + offset
    img = pygame.Surface(size)
    base.set_palette_at(1, shadowcolor)
    img.blit(base, (offset, offset))
    base.set_palette_at(1, fontcolor)
    img.blit(base, (0, 0))
    return img


entry_info = 'Drop Shadow, by Pete Shinners'

# this code will display our work, if the script is run...
if __name__ == '__main__':
    pygame.init()

    # create our fancy text
    white = 255, 255, 255
    grey = 100, 100, 100
    bigfont = pygame.font.Font(None, 60)
    text = textDropShadow(bigfont, entry_info, 3, white, grey)

    # create a window the correct size
    win = pygame.display.set_mode((800,600))
    win.fill("red")
    winrect = win.get_rect()
    win.blit(text, (0, 0))
    pygame.display.flip()

    # wait for the finish
    while 1:
        event = pygame.event.wait()
        if event.type is KEYDOWN and event.key == K_s:  # save it
            name = os.path.splitext(sys.argv[0])[0] + '.bmp'
            print
            'Saving image to:', name
            pygame.image.save(win, name)
        elif event.type in (QUIT, KEYDOWN, MOUSEBUTTONDOWN):
            break
