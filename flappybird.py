import random
from threading import Thread
from Box2D.Box2D import b2RayCastCallback

from Box2D.b2 import world
from Box2D import b2Vec2
from Box2D import b2ContactListener
import pyglet
from pyglet.window import key, Window
from pyglet.shapes import Line
from playsound import playsound

from objects import Bird, Ground, Pipes



PPM = 20


class ContactObserver(b2ContactListener):
    def __init__(self, on_collision_enter):
        super().__init__()
        self.on_collision_enter = on_collision_enter
    
    def BeginContact(self, contact):
        self.on_collision_enter()

class RayCastObserver(b2RayCastCallback):
    def __init__(self):
        super().__init__()
        self.passed = False

    def ReportFixture(self, fixture, point, normal, fraction):
        self.passed = True
        return fraction


class FlappyBird(Window):
    def __init__(self, theme="day", birdcolor="yellow", pipecolor="green", speed=7, *args, **kwargs):
        super().__init__(width=288, height=512, *args, **kwargs)
        self.set_caption("Flappy Bird")
        self.birdcolors = ["blue", "red", "yellow"]
        self.themes = ["day", "night"]
        self.pipecolors = ["green", "red"]
        self.pressing = []
        self.pipecolor = pipecolor
        self.birdcolor = birdcolor
        self.speed = speed
        self.pipewidth = 100
        #self.clear_sound = pyglet.media.load("sounds/clear.mp3")
        #self.die_sound = pyglet.media.load("sounds/die.mp3")
        self.clear_sound = "sounds/clear.mp3"
        self.die_sound = "sounds/die.mp3"
        self.background = pyglet.image.load(f"assets/background-{theme}.png")
        contactlistener = ContactObserver(self.on_collision_enter)
        self.world = world(gravity=(0, -50), contactListener=contactlistener)
        self.bird = Bird(self.world, 100, 300, birdcolor=birdcolor)
        self.grounds = [Ground(self.world, velocity=speed), Ground(self.world, x=336, velocity=speed)]
        self.pipes = []
        self.raycastline = Line(0, 0, 0, 0, width=5)
        self.is_scrolling = True
        self.world_time = 0
        self.last_append_time = 0
        self.is_dead = False
        self.score = 0
        self.set_icon(pyglet.image.load("flappy.png"))
        pyglet.clock.schedule_interval(self.update, 1/100)

    def on_draw(self):
        self.background.blit(0, 0)

        for pipe in self.pipes:
            pipe.draw()
        
        self.bird.draw()

        for ground in self.grounds:
            ground.draw()

        self.raycastline.draw()


    def update(self, dt):
        if self.is_scrolling:
            self.world_time += dt

        if self.is_pressing(key.SPACE) and not self.is_dead:
            self.bird.force()

        for pipe in self.pipes:
            hit = pipe.raycast()
            
            if hit:
                self.score += 1
                print(self.score)
                self.play_in_thread(self.clear_sound)

            if pipe.bottom_pipe.x < -330:
                self.pipes.remove(pipe)

        for ground in self.grounds:
            if ground.x < -336:
                self.grounds.remove(ground)
                self.grounds.append(Ground(self.world, x=288, velocity=self.speed))

        if (self.world_time - self.last_append_time) > 1.2:
            self.append_pipe()
            self.last_append_time = self.world_time

        #print(self.bird.bird_body.position)
        #print(1/dt)
        #self.set_caption(f"FPS: {round(1/dt, 2)}")
        #print(self.score)

        self.world.Step(dt, 10, 10)

    def append_pipe(self, dt=None):
        if self.is_scrolling:
            self.pipes.append(Pipes(self.world, 336, random.choice(range(-100, 50)), self.pipewidth, pipecolor=self.pipecolor, velocity=self.speed))

    def on_key_press(self, symbol, modifiers):
        self.pressing.append(symbol)

        if symbol == key.ENTER:
            self.reset(randomize_color=True)
            self.start_scroll()

    def on_key_release(self, symbol, modifiers):
        self.pressing.remove(symbol)

    def is_pressing(self, symbol):
        return symbol in self.pressing

    def on_mouse_press(self, x, y, button, modifiers):
        self.pressing.append(key.SPACE)

    def on_mouse_release(self, x, y, button, modifiers):
        self.pressing.remove(key.SPACE)

    def on_mouse_motion(self, x, y, dx, dy):
        #print(x, y)
        pass

    def on_collision_enter(self):
        self.stop_scroll()

        if not self.is_dead:
            self.play_in_thread(self.die_sound)
        
        self.is_dead = True

    def start_scroll(self):
        self.is_scrolling = True

        for pipe in self.pipes:
            pipe.top_pipe_body.linearVelocity = b2Vec2(-self.speed, 0)
            pipe.bottom_pipe_body.linearVelocity = b2Vec2(-self.speed, 0)

        for ground in self.grounds:
            ground.ground_body.linearVelocity = b2Vec2(-self.speed, 0)

    def stop_scroll(self):
        self.is_scrolling = False

        for pipe in self.pipes:
            pipe.top_pipe_body.linearVelocity = b2Vec2(0, 0)
            pipe.bottom_pipe_body.linearVelocity = b2Vec2(0, 0)

        for ground in self.grounds:
            ground.ground_body.linearVelocity = b2Vec2(0, 0)

    def reset(self, randomize_color=False):
        if randomize_color:
            self.background = pyglet.image.load(f"assets/background-{random.choice(self.themes)}.png")
            self.birdcolor = random.choice(self.birdcolors)
            self.pipecolor = random.choice(self.pipecolors)

        contactlistener = ContactObserver(self.on_collision_enter)
        raycastcallback = RayCastObserver()
        self.world = world(gravity=(0, -50), contactListener=contactlistener, raycastcallback=raycastcallback)
        self.bird = Bird(self.world, 100, 300, birdcolor=self.birdcolor)
        self.grounds = [Ground(self.world, velocity=self.speed), Ground(self.world, x=336, velocity=self.speed)]
        self.pipes = []
        self.is_scrolling = True
        self.world_time = 0
        self.last_append_time = 0
        self.is_dead = False
        self.score = 0

    def play_in_thread(self, sound):
        #thread = Thread(target=sound.play)
        thread = Thread(target=playsound, args=(sound,))
        thread.daemon = True
        thread.start()


if __name__ == "__main__":
    fb = FlappyBird("day", "yellow", "green", speed=7)
    pyglet.app.run()
