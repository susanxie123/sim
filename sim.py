import pygame
import sys
from pygame.locals import *


# constants
SCREENRECT     = Rect(0, 0, 640, 480)

# globals
dirtyrects = [] # list of update_rects


def main():
    global dirtyrects

    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREENRECT.size)

    car = pygame.image.load("resources/car.png")
    car_rect = car.get_rect()
    car_rect.top = 200

    direction = 1
    while True:
        clock.tick(40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        screen.fill((0, 0, 0))
        car_rect = car_rect.move(10 * direction, 0)
        print(car_rect.x, car_rect.y)
        if not SCREENRECT.contains(car_rect):
            direction = direction * -1
        screen.blit(car, car_rect)

        print(clock.get_rawtime())
        pygame.display.flip()
    pygame.time.wait(50)


if __name__ == "__main__":
    main()
