import pygame

pygame.mixer.init(88200, allowedchanges=pygame.AUDIO_ALLOW_ANY_CHANGE)
pygame.mixer.init()
pygame.mixer.music.load('sound/tetris-music.mp3')
pygame.mixer.music.play()

while True:
    pass
