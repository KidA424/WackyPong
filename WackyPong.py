# To install the pygame module, enter the following command into a Unix terminal:
# sudo apt-get install python-pygame

import pygame, sys, random
from pygame.locals import *

GAMESPEED = 60
WINDOWWIDTH = 700
WINDOWHEIGHT = 700
LINETHICKNESS = 10
BALLRADIUS = 7
BALLSPEED = 4
PADDLEHEIGHT = 10
PADDLEWIDTH = 80
PADDLESPEED = 5
WINDOWMARGIN = 5

BLACK = (0,0,0)
RED   = (255,0,0)
GREEN = (0,255,0)
BLUE  = (0,0,255)
WHITE = (255,255,255)

"""
All objects in this game inherit from this class.  Each object has a horizontal and vertical
velocity direction, dx and dy, respectively, and a speed.  The applies to both the horizontal
and vertical components.
"""
class GameObject:
    def __init__(self, x, y, color, speed = 0, dx = 0, dy = 0):
        self.x = x
        self.y = y
        self.dx = dx*speed
        self.dy = dy*speed
        self.speed = speed
        self.color = color
        self.colliding = False

    def left(self):
        return self.x
    def right(self):
        return self.x
    def top(self):
        return self.y
    def bot(self):
        return self.y
    def move(self):
        self.x += self.dx
        self.y += self.dy

"""
The ball class.
"""
class Ball(GameObject):
    def __init__(self, x, y, radius, speed = BALLSPEED, color = GREEN, dx = 0, dy = 0):
        GameObject.__init__(self, x = x, y = y, speed = speed, dx = dx, dy = dy, color = color)
        self.radius = radius
    def left(self):
        return self.x - self.radius
    def right(self):
        return self.x + self.radius
    def top(self):
        return self.y - self.radius
    def bot(self):
        return self.y + self.radius
    def draw(self):
        pygame.draw.circle(DISPLAY, self.color, (self.x, self.y), self.radius, 0)

"""
The paddle class.
"""
class Paddle(GameObject):
    def __init__(self, x, y, width, height, color, speed = 0):
        GameObject.__init__(self, x = x, y = y, speed = speed, color = color)
        self.width = width
        self.height = height
        self.speed = speed
    def left(self):
        return self.x
    def right(self):
        return self.x + self.width
    def top(self):
        return self.y
    def bot(self):
        return self.y + self.height
    def move(self, ball_left):
        """
        Overrides the move method of parent class in order to implement the
        computer player's strategy, which is simply to move horizontally
        towards the ball which is closest to the side it is defending.  This
        method also ensures that the paddle does not move beyond the left or
        right boundaries of the game window.
        """
        if ball_left > self.x + self.width/2 and self.right() <= WINDOWWIDTH:
            self.dx = self.speed
        elif ball_left < self.x + self.width/2 and self.left() >= 0:
            self.dx = self.speed*(-1)
        else:
            self.dx = 0
        GameObject.move(self)
    def draw(self):
        pygame.draw.rect(DISPLAY, self.color, pygame.Rect(self.x, self.y, self.width, self.height))

"""
Throughout the game, rectangular obstacles will randomly appear.  The function detectCollisions
can determine whether a ball is currently in collision with one of these obstacles.  Two invisible
obstacles also exist: the left and right walls of the game.
"""
class Obstacle(GameObject):
    def __init__(self, x, y, width, height, dx = 0, dy = 0, color = BLACK, visible = True):
        GameObject.__init__(self, x = x, y = y, dx = dx, dy = dy, color = color)
        self.width = width
        self.height = height
        self.visible = visible

    def draw(self):
        if self.visible:
            pygame.draw.rect(DISPLAY, self.color, pygame.Rect(self.x, self.y, self.width, self.height))




###################
#    Functions    #
###################

"""
This function randomly generates an obstacle, subject to some spatial constraints.
"""
def randomObstacle(balls, objects):
    lefts = []          ## The left coordinates of all obstacles present in the game
    rights = []         ## The right coordinates of all obstacles present in the game
    for obj in objects[2:]:
        lefts.append(obj.left())
        rights.append(obj.right())
    for ball in balls:
        lefts.append(ball.left())
        rights.append(ball.right())
    lefts = sorted(lefts)
    rights = sorted(rights)
    difs = [lefts[i+1] - rights[i] for i in range(len(objects) - 2 + len(balls) - 1)]  ## Holds the width of all horizontal gaps between obstacles
    i = difs.index(max(difs))
    a = rights[i]
    b = lefts[i+1]
    x = random.randint(a + BALLRADIUS + 1, b - 2*BALLRADIUS - 1)    ## randomly generate the x-coordinate of the obstacle
    y = random.randint(4*BALLRADIUS, WINDOWHEIGHT - 4*BALLRADIUS)   ## randomly generate the y-coordinate of the obstacle
    width = random.randint(1, b - a - 2*BALLRADIUS)                 ## randomly generate the width of the obstacle
    height = random.randint(3*BALLRADIUS, 10*BALLRADIUS)            ## randomly generate the height of the obstacle
    return Obstacle(x = x, y = y, width = width, height = height, color = (random.randint(100,200), random.randint(100,200), random.randint(100,200)))


"""
Calls the move methods of each object present in the game.
"""
def move(balls, objects):
    tops = []           ## Stores the top coordinate of each ball
    for ball in balls:
        ball.move()
        tops.append(ball.top())
    i = tops.index(min(tops))           ## Find the highest ball
    objects[1].move(balls[i].left())    ## Move the computer paddle
    for obj in objects[2:]:
        obj.move()

"""
Draws each object present in the game.
"""
def draw(balls, objects):
    DISPLAY.fill(WHITE)
    for obj in objects:
         obj.draw()
    for ball in balls:
        ball.draw()

"""
Detects collisions between a ball and each obstacle or paddle.
"""
def detectCollisions(ball, objects):
    collisions = []
    ball_left = ball.left()
    ball_right = ball.right()
    ball_top = ball.top()
    ball_bot = ball.bot()

    # Find the previous location of the ball
    prev_left = ball_left - ball.dx
    prev_right = ball_right - ball.dx
    prev_top = ball_top - ball.dy
    prev_bot = ball_bot - ball.dy

    for obj in objects:
        dx2 = 1         ## The ball's dx variable will eventually get multiplied by this value, which will either be -1 or 1.
        dy2 = 1         ## The ball's dy variable will eventually get multiplied by this value, which will either be -1 or 1.

        obj_left = obj.x
        obj_right = obj.x + obj.width
        obj_top = obj.y
        obj_bot = obj.y + obj.height

        ## Determine if the ball was previously outside the object, but is now within its borders
        if ball_bot > obj_top and ball_top < obj_bot:
            if prev_right < obj_left and ball_right >= obj_left:
                dx2 = dx2*(-1)
            if prev_left > obj_right and ball_left <= obj_right:
                dx2 = dx2*(-1)
        if obj.width != 0 and ball_right > obj_left and ball_left < obj_right:
            if prev_bot < obj_top and ball_bot >= obj_top:
                dy2 = dy2*(-1)
            if prev_top > obj_top and ball_top <= obj_bot:
                dy2 = dy2*(-1)

        ## We must allow the ball time to leave the object's borders.  If the ball was colliding with this
        ## object on the previous iteration, do not reverse its direction.
        if obj.colliding:
            collisions.append((1,1))
            if dx2 == 1 and dy2 == 1:
                obj.colliding = False
        else:
            collisions.append((dx2,dy2))
            if dx2 != 1 or dy2 != 1:
                obj.colliding = True

    return collisions

        


def main():

    # Initialization
    pygame.init()
    pygame.mouse.set_visible(0)
    global DISPLAY, CLOCK, FONTSIZE, FONT
    DISPLAY = pygame.display.set_mode((WINDOWWIDTH,WINDOWHEIGHT))
    CLOCK = pygame.time.Clock()
    FONTSIZE = 20
    FONT = pygame.font.Font('freesansbold.ttf', FONTSIZE)
    pygame.display.set_caption('Pong')

    balls = []
    objects = []

    balls.append(Ball(x = int(round(WINDOWWIDTH/2)), y = int(round(WINDOWHEIGHT/2)), radius = BALLRADIUS, color = BLACK, dy = 1, dx = 1))
    objects.append(Paddle(x = int(round((WINDOWWIDTH - PADDLEWIDTH)/2)), y = WINDOWHEIGHT - PADDLEHEIGHT - WINDOWMARGIN, width = PADDLEWIDTH, height = PADDLEHEIGHT, color = BLUE))
    objects.append(Paddle(x = int(round((WINDOWWIDTH - PADDLEWIDTH)/2)), y = WINDOWMARGIN, color = RED, width = PADDLEWIDTH, height = PADDLEHEIGHT, speed = PADDLESPEED))
    objects.append(Obstacle(x = 0, y = 0, width = 0, height = WINDOWHEIGHT, visible = False))
    objects.append(Obstacle(x = WINDOWWIDTH, y = 0, width = 0, height = WINDOWHEIGHT, visible = False))

    draw(balls, objects)

    done = False        ## Triggers the ending of a game
    time = 0            ## The current iteration

    while(True):
        if done == True:
            balls = [Ball(x = int(round(WINDOWWIDTH/2)), y = int(round(WINDOWHEIGHT/2)), radius = BALLRADIUS, color = BLACK, dy = 1, dx = 1)]   ## Reset the game
            done = False

        ## Every 150 iterations, we will either randomly generate or randomaly remove some objects.
        if time % 150 == 0:
            r = random.random()
            if r < .2:
                objects.append(randomObstacle(balls, objects))
            elif r > .7 and len(objects) > 4:
                objects.pop(4)                      ## Remove the first randomly generated obstacle, if one exists.
            elif r > .4 and r < .5:
                balls.append(Ball(x = int(round(WINDOWWIDTH/2)), y = int(round(WINDOWHEIGHT/2)), radius = BALLRADIUS,
                    color = BLACK, dy = 1, dx = 2*random.randint(0,1) - 1))

        ## Handles mouse events for the player's movement.
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == MOUSEMOTION:
                x = event.pos[0]
                if x >= 0 and x + PADDLEWIDTH <= WINDOWWIDTH:
                    objects[0].x = x                                ## Update the position of the player's paddle.

        ## Check if any of the balls have gotten past one of the paddles.
        for ball in balls:
            if ball.top() < PADDLEHEIGHT/2 or ball.bot() > WINDOWHEIGHT - PADDLEHEIGHT/2:
                done = True
            collisions = detectCollisions(ball, objects)
            for col in collisions:
                ball.dx = ball.dx*col[0]
                ball.dy = ball.dy*col[1]
        
        move(balls, objects)
        draw(balls,objects)
        pygame.display.update()
        CLOCK.tick(GAMESPEED)
        time += 1

if __name__=='__main__':
    main()
