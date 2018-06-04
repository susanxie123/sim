import pygame, sys, math
from pygame.locals import *


# constants
SCREEN_WIDTH    = 640
SCREEN_HEIGHT   = 480
SCREEN_RECT     = Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT)

CAR_LENGTH      = 30
CAR_WIDTH       = 20

ROAD_WIDTH      = 25
CURB_WIDTH      = 3

BLACK           = Color(0, 0, 0)
WHITE           = Color(255, 255, 255)
GRAY            = Color(180, 180, 180)

# globals
dirtyrects = [] # list of update_rects

# images
class Img:
    def car():
        car = pygame.image.load("resources/car.png").convert()
        car.set_colorkey(WHITE)
        car = pygame.transform.scale(car, (CAR_LENGTH, CAR_WIDTH))
        return car

    def background(width = SCREEN_WIDTH, height = SCREEN_HEIGHT):
        bg = pygame.Surface((width, height))
        bg.fill(BLACK)
        return bg

    def intersection(width = ROAD_WIDTH, height = ROAD_WIDTH):
        img = pygame.Surface((width, height))
        img.fill(GRAY)
        return img

    def road(length, width = ROAD_WIDTH):
        img = pygame.Surface((length, width + 2 * CURB_WIDTH))
        img.fill(GRAY)
        img.fill(WHITE, Rect(0, 0, length, CURB_WIDTH))
        img.fill(WHITE, Rect(0, width + CURB_WIDTH, length, CURB_WIDTH))
        print(img.get_rect())
        return img


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
        dirtyrects.append(r)


class Position:
    def __init__(self, x = SCREEN_WIDTH / 2, y = SCREEN_HEIGHT / 2):
        self.x = x
        self.y = y

    def __str__(self):
        return "(" + str(self.x) + ", " +  str(self.y) + ")"

    def get_center(self):
        return (self.x, self.y)

    def dist(self, dest):
        return math.sqrt((self.x - dest.x) * (self.x - dest.x) + (self.y - dest.y) * (self.y - dest.y))

    def dir(self, dest):
        if self.x == dest.x:
            return 90
        elif self.y == dest.y:
            return 0
        else:
            return math.atan((self.y - dest.y) / (self.x - dest.x)) * 180 / math.pi

    def mid(self, dest):
        return Position((self.x + dest.x) / 2, (self.y + dest.y) / 2)

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
    def __init__(self, center = Position(), traffic_control = None, outs = dict(), ins = dict()):
        Drawable.__init__(self, Img.intersection())
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
        if out_intersect in self.outs:
            raise Exception("A road to " + str(out_intersect) + " already exists")
        self.outs[out_intersect] = out_road

    def add_inlet(self, in_intersect, in_road):
        if in_intersect in self.ins:
            raise Exception("A road from " + str(in_interset) + " already exists")
        self.ins[in_intersect] = in_road


class Road(Drawable):
    def __init__(self, start, end):
        self.length = start.pos.dist(end.pos)
        Drawable.__init__(self, Img.road(self.length))
        self.start = start
        self.end = end
        self.start.add_outlet(self.end, self)
        self.end.add_inlet(self.start, self)
        self.angle = self.start.pos.dir(self.end.pos)
        self.image = pygame.transform.rotate(self.image, self.angle)
        self.rect = self.image.get_rect(center=self.start.pos.mid(self.end.pos).get_center())
        print("length ", self.length, "angle ", self.angle, "mid ", self.start.pos.mid(self.end.pos))
        print(self.rect)
        print("inistiated new Road from ", self.start, " to ", self.end)


class TrafficLightController(TrafficController):
    def get_controller(self, intersection):
        pass


class Car(Drawable):
    def __init__(self, center = Position(), angle = 0, destination = Position()):
        Drawable.__init__(self, Img.car())
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
        #print(str(self) + " moved from " + old_pos)

    def move_to(self, position):
        "move to a new position"
        old_pos = str(self.pos)
        self.pos = position
        self.rect.center = self.pos.get_center()
        #print(str(self) + " moved from " + old_pos)

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

    intersect1 = Intersection(Position(100, 300))
    intersect1.draw(background)
    intersect2 = Intersection(Position(400, 300))
    intersect2.draw(background)
    road = Road(intersect1, intersect2)
    road.draw(background)

    screen.blit(background, SCREEN_RECT)

    # create cars
    car = Car(Position(105, 300))

    direction = 1
    while True:
        clock.tick(40)

        for event in pygame.event.get():
            if event.type == pygame.QUIT: sys.exit()

        car.clear(screen, background)
        car.move(5 * direction, 0)
        print(car.pos)
        if not road.rect.unionall([intersect1.rect, intersect2.rect]).contains(car.rect):
            direction = direction * -1
        
        car.draw(screen)

        pygame.display.update(dirtyrects)
        dirtyrects = []
        
        print(clock.get_rawtime())


if __name__ == "__main__":
    main()
