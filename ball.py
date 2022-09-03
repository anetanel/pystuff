import sys, pygame

pygame.init()

size = width, height = 1920, 1080

speed = [2, 2]

black = 0, 0, 0

screen = pygame.display.set_mode(size)
s = pygame.Surface((width,height),pygame.SRCALPHA)
# s.set_alpha(128)
ball = pygame.image.load("intro_ball.gif")
bg = pygame.image.load("images/bg1.jpg")
ballrect = ball.get_rect()

while 1:

    for event in pygame.event.get():

        if event.type == pygame.QUIT: sys.exit()

    ballrect = ballrect.move(speed)

    if ballrect.left < 0 or ballrect.right > width:
        speed[0] = -speed[0]

    if ballrect.top < 0 or ballrect.bottom > height:
        speed[1] = -speed[1]

    pygame.draw.rect(s, (0, 200, 0, 125), [200, 300, 100, 100])
    screen.fill(black)
    screen.blit(bg, (0, 0))
    screen.blit(s,(0,0))

    screen.blit(ball, ballrect)

    pygame.display.flip()
