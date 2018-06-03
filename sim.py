import pygame
import sys
from pygame.locals import *


# constants
SCREEN_WIDTH    = 640
SCREEN_HEIGHT   = 480
SCREEN_RECT     = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

CAR_LENGTH      = 30
CAR_WIDTH       = 20

ROAD_WIDTH      = 25

BLACK           = Color(0, 0, 0)
WHITE           = Color(255, 255, 255)

# globals
dirtyrects = [] # list of update_rects

# images
class ImgFactory:
    def carImg(self):
        car = pygame.image.load("resources/car.png").convert()
        car.set_colorkey(WHITE)
        car = pygame.transform.scale(car, (CAR_LENGTH, CAR_WIDTH))
        return car

    def backgroundImg(self, width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
        bg = pygame.Surface((int(width), int(height)))
        bg.fill(BLACK)
        return bg

    def intersectionImg(self, width = ROAD_WIDTH, height = ROAD_WIDTH):
        img = pygame.Surface((int(width), int(height)))
        img.fill(WHITE)
        return img


imgFactory = ImgFactory()


class Drawable:
    "A parent class for image rendering"
    def __init__(self, image):
        self.image = image
        self.rect = image.get_rect()

    def draw(self, screen):
        r = screen.blit(self.image, self.rect)
        dirtyrects.append(r)

    def clear(self, screen, background):
        r = screen.blit(background, self.rect, self.rect)
        print("clearing " + str(self.rect.clip(SCREEN_RECT)))
        #r = screen.blit(backgroun, (0,0))
        dirtyrects.append(r)


class Position:
    def __init__(self, x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT / 2):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " +  str(self.y) + ")"

    def get_center(self):
        return (self.x, self.y)

    def move(self, x, y):
        self.x += x
        self.y += y

    def move_by_speed(self, speed):
        offset = speed.get_offset()
        self.x += offset.x
        self.y += offset.y


class Speed:
    def __init__(self, x = 0, y = 0):
        self.x = x
        self.y = y

    def get_offset(self):
        return (self.x, self.y)


class TrafficController:
    def should_stop(from_intersect, to_intersect):
        return True

    def should_proceed(from_intersect, to_intersect):
        return True


class Intersection(Drawable):
    def __init__(self, center = Position(), outs = dict(), ins = dict(), traffic_control = None):
        Drawable.__init__(self, imgFactory.intersectionImg())
        self.pos = center
        self.rect = self.image.get_rect(center=self.pos.get_center())
        self.outs = outs
        self.ins = ins
        if traffic_control != None: 
            self.traffic_control = traffic_control.get_controller(self)
        else:
            self.traffic_control = TrafficController()

    def __str__(self):
        return "Intersection " + str(self.pos)

    def add_outlet(self, out_intersect, out_road):
        if out_intersect in outs:
            raise Exception("A road to " + str(out_intersect) + " already exists")
        self.outs[out_intersect] = out_road

    def add_inlet(self, in_intersect, in_road):
        if in_intersect in ins:
            raise Exception("A road from " + str(in_interset) + " already exists")
        self.ins[in_intersect] = in_road


class Road(Drawable):
    pass

class TrafficLightController(TrafficController):
    def get_controller(self, intersection):
        pass


class Car(Drawable):
    def __init__(self, center = Position(), angle = 0, destination = Position()):
        Drawable.__init__(self, imgFactory.carImg())
        self.pos = center
        self.ang = angle
        self.dest = destination
        self.speed = Speed()
        self.original_image = self.image
        self.image = pygame.transform.rotate(self.original_image, self.ang)
        self.rect = self.image.get_rect(center=self.pos.get_center())
        print("initiated new Car " + str(self.pos))

    def __str__(self):
        return "Car " + str(self.pos)

    def move(self, x, y):
        "move by offset (x, y)"
        old_pos = str(self.pos)
        self.pos.move(x, y)
        self.rect.center = self.pos.get_center()
        print(str(self) + " moved from " + old_pos)

    def move_to(self, position):
        "move to a new position"
        old_pos = str(self.pos)
        self.pos = position
        self.rect.center = self.pos.get_center()
        print(str(self) + " moved from " + old_pos)

    def rotate(self, angle):
        "rotate counter-clockwise for (angle) degrees"
        self.rotate_to(self.ang + angle)

    def rotate_to(self, angle):
        "rotate to a certain angle"
        self.image = pygame.transform.rotate(self.original_image, angle)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.ang = angle


def main():
    global dirtyrects

    # init
    pygame.init()
    clock = pygame.time.Clock()
    screen = pygame.display.set_mode(SCREEN_RECT.size)

    # draw intersections and roads
    background = pygame.Surface(SCREEN_RECT.size)
    background.fill(BLACK)

    intersect = Intersection()
    intersect.draw(background)

    screen.blit(background, SCREEN_RECT)

    # create cars
    car = Car()

    direction = 1
    while True:
        clock.tick(40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        car.clear(screen, background)
        car.move(10 * direction, 0)
        car.rotate(10)
        print(car.pos)
        if not SCREEN_RECT.contains(car.rect):
            direction = direction * -1
        
        car.draw(screen)

        pygame.display.update(dirtyrects)
        dirtyrects = []
        
        print(clock.get_rawtime())


if __name__ == "__main__":
    main()
