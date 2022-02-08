import pygame
import neat
import time
import os
import random

pygame.font.init()

WIN_WIDTH = 500
WIN_HEIGHT = 800

GEN = 0

BIRD_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
STAT_FONT = pygame.font.SysFont("comicsans", 50)


class Bird:
    IMGS = BIRD_IMGS
    MAX_ROTATION = 25  # Rotating Bird
    ROT_VEL = 20  # How much we're rotating on each frame or when we move the bird
    ANIMATION_TIME = 5  # How long we're going to show Bird's animation if increased it increases speed of bird flapping wings

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0  # Going to be looking flat
        self.tick_count = 0  # Dealing with Physics of Bird
        self.vel = 0  # Bird not moving
        self.height = self.y
        self.img_count = 0  # Knows which image we're showing for bird position
        self.img = self.IMGS[0]  # References BIRD_IMGS

    def jump(self):
        self.vel = -10.5
        self.tick_count = 0  # We need to know when we're changing direction/velocity so physics formulas work
        self.height = self.y

    def move(self):
        self.tick_count += 1  # Keeps track of movements since last jump

        d = self.vel * self.tick_count + 1.5 * self.tick_count ** 2  # Pixels we move up or down in frame ( Displacement = Vel * Time )

        if d >= 16:
            d = 16  # So if we're moving down more than 16 we should just move down 16

        if d < 0:
            d -= 2  # If we're moving upwards let's move up a little more (best number to make it jump nicely)

        self.y = self.y + d  # Adds what we calculated to y position

        if d < 0 or self.y < self.height + 50:  # Tilting bird upwards (Bird must only tilt downwards when below certain point and tilt upwards when above certain point)
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION  # Rather than rotating slowly it rotates quickly  ( Sets to 25 degrees)
        else:
            if self.tilt > -90:
                self.tilt -= self.ROT_VEL  # Rotates Bird completely 90 degrees when falling down

    def draw(self, win):
        self.img_count += 1  # Keep track of how many ticks we've shown a current image for

        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]  # If image count < 5 then we show the first image of the flappy bird
        elif self.img_count < self.ANIMATION_TIME * 2:
            self.img = self.IMGS[1]
        elif self.img_count < self.ANIMATION_TIME * 3:
            self.img = self.IMGS[2]
        elif self.img_count < self.ANIMATION_TIME * 4:
            self.img = self.IMGS[1]
        elif self.img_count == self.ANIMATION_TIME * 4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0  # If image count = 21 then it will show the first image and reset the image count

        if self.tilt <= -80:
            self.img = self.IMGS[
                1]  # We're going to go to image where wings are level so looks like it's nose diving downwards
            self.img_count = self.ANIMATION_TIME * 2  # When we jump back up it doesn't look like it's skipping an animation frame (Starts at what it should be)

        rotated_image = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_image.get_rect(
            center=self.img.get_rect(topleft=(self.x, self.y)).center)  # Rotates the image around the centre
        win.blit(rotated_image, new_rect.topleft)  # .blit just means "draw"

    def get_mask(self):
        return pygame.mask.from_surface(self.img)  #


class Pipe:
    GAP = 200  # Distance between the two pipes
    VEL = 5  # We're moving pipes towards bird the bird only moves in y direction

    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True)  # Flips Pipe = PIPE TOP
        self.PIPE_BOTTOM = PIPE_IMG

        self.passed = False
        self.set_height()

    def set_height(self):  # Implementing positions of pipe
        self.height = random.randrange(50, 450)
        self.top = self.height - self.PIPE_TOP.get_height()
        self.bottom = self.height + self.GAP

    def move(self):
        self.x -= self.VEL  # -= means that when we call the move method it moves pipe to left (+= is the right)

    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top))
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        top_offset = (self.x - bird.x, self.top - round(bird.y))
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False


class Base:
    VEL = 5
    WIDTH = BASE_IMG.get_width()
    IMG = BASE_IMG

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH  # We're creating 2 base images

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + self.WIDTH < 0:  # Checks if 1 image is off the screen completely and if it is it is recycled
            self.x1 = self.x2 + self.WIDTH

        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x1 + self.WIDTH

    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))


def draw_window(win, birds, pipes, base, score, gen):
    win.blit(BG_IMG, (0, 0))

    for pipe in pipes:
        pipe.draw(win)

    text = STAT_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))

    text = STAT_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (10, 10))

    base.draw(win)

    for bird in birds:
        bird.draw(win)

    pygame.display.update()  # Updates display and refreshes it


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []  # These genomes are a bunch of neural networks which control each of our birds
    birds = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g,
                                                config)  # Setting up a neural network for our genome - give it genome and config
        nets.append(net)  # Appends it to the list
        birds.append(Bird(230, 350))  # Appending bird object to list as well
        g.fitness = 0
        ge.append(
            g)  # Appending gnome to same position as bird and neural network objects - We can change fitness as we desire

    base = Base(730)
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock()  # Adding clock stops bird from immediately falling so quickly when starting - Falls Slower
    score = 0

    run = True
    while run and len(birds) > 0:
        clock.tick(30)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
                break

        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width():  # determine whether to use the first or second
                pipe_ind = 1  # pipe on the screen for neural network input

        for x, bird in enumerate(birds):  # give each bird a fitness of 0.1 for each frame it stays alive
            ge[x].fitness += 0.1
            bird.move()

            # send bird location, top pipe location and bottom pipe location and determine from network whether to jump or not
            output = nets[birds.index(bird)].activate(
                (bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))

            if output[0] > 0.5:  # we use a tanh activation function so result will be between -1 and 1. if over 0.5 jump
                bird.jump()

        base.move()

        # bird.move()
        rem = []
        add_pipe = False

        for pipe in pipes:
            for x, bird in enumerate(birds):  # enumerate - Can get position of bird in list as well
                if pipe.collide(bird):
                    ge[x].fitness -= 1  # If bird hits pipe we -1 fitness score (encouraging it not to hit pipe)
                    birds.pop(x)  # Gets rid of bird, genome, neural network and everything associated with it
                    nets.pop(x)
                    ge.pop(x)

                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    add_pipe = True

            if pipe.x + pipe.PIPE_TOP.get_width() < 0:
                rem.append(pipe)

            pipe.move()

        if add_pipe:
            score += 1
            for g in ge:  # If bird gets through pipe it gets a fitness score of +5 so it's encouraged to go through the pipes
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in rem:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < -50:  # Some birds might jump far above the screen and they won't die - bird.y > 0 = fix
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

        draw_window(win, birds, pipes, base, score, GEN)


def run(config_file):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, neat.DefaultSpeciesSet,
                                neat.DefaultStagnation, config_file)  # All these properties are on the file

    p = neat.Population(config)  # Set a population and configuration file

    p.add_reporter(neat.StdOutReporter(True))  # Gives us output/ Stats that come from running the program
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main, 50)  # Runs main 50 times - acts as fitness function


if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    run(config_path)
