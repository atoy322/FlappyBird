import random

from Box2D import b2
from Box2D.Box2D import b2RayCastCallback
from Box2D.b2 import world
from Box2D import b2Vec2
import pyglet


PPM = 20


class RayCastObserver(b2RayCastCallback):
    def __init__(self):
        super().__init__()
        self.hit = False

    def ReportFixture(self, fixture, point, normal, fraction):
        self.hit = True
        return fraction


class Bird(pyglet.sprite.Sprite):
    def __init__(self, world, x, y, birdcolor="yellow"):
        self.initial_pos = b2Vec2(x, y)
        self.PPM = PPM
        self.world = world
        load_img = lambda color, flap: pyglet.image.load(f"assets/{color}bird-{flap}flap.png")
        self.bird_images = {i:load_img(birdcolor, i) for i in ["up", "mid", "down"]}
        self.state = "mid"
        super().__init__(self.bird_images["mid"], x, y)
        self.bird_body = self.world.CreateDynamicBody(position=(x/self.PPM, y/self.PPM))
        self.fixture = self.bird_body.CreatePolygonFixture(box=(0.7, 0.5), density=0.01, restitution=0.3, friction=0.6)

    def force(self):
        #self.bird_body.ApplyForceToCenter([0, 600], True)
        self.bird_body.linearVelocity = b2Vec2(0, 12)

    def up(self):
        self.state = "up"
        self.image = self.bird_images[self.state]

    def mid(self):
        self.state = "mid"
        self.image = self.bird_images[self.state]

    def down(self):
        self.state = "down"
        self.image = self.bird_images[self.state]

    def toggle_bird_state(self):
        if self.state == "up":
            self.mid()
        elif self.state == "mid":
            self.down()
        elif self.state == "down":
            self.up()

    def draw(self):
        self.bird_body.angle = 0
        self.bird_body.angulerVelocity = 0
        t = self.bird_body.transform
        v = self.bird_body.linearVelocity.y
        self.rotation = -v
        distance = self.initial_pos/self.PPM - t.position
        distance.y = 0
        distance *= 0.02
        self.bird_body.ApplyForceToCenter(distance, True)
        self.x, self.y = t.position.x*self.PPM-20, t.position.y*self.PPM-10
        if v > 3:
            self.toggle_bird_state()
        super().draw()

    def destroy_body(self):
        self.world.DestroyBody(self.bird_body)


class Ground(pyglet.sprite.Sprite):
    def __init__(self, world, x=0, y=0, velocity=7):
        self.PPM = PPM
        self.world = world
        self.base = pyglet.image.load("assets/base.png")
        super().__init__(self.base, x=x, y=y)
        self.ground_body = self.world.CreateKinematicBody(position=(x/self.PPM, 0))
        self.fixture = self.ground_body.CreatePolygonFixture(box=(336/self.PPM, 112/self.PPM))

        self.ground_body.linearVelocity = b2Vec2(-velocity, 0)

    def draw(self):
        t = self.ground_body.transform
        self.x, self.y = t.position.x*self.PPM, 0
        super().draw()

    def destroy_body(self):
        self.world.DestroyBody(self.ground_body)



class Pipes:
    def __init__(self, world, pos, height, width=100, pipecolor="green", velocity=7):
        self.PPM = PPM
        self.world = world
        self.height = height
        self.width = width
        top_pipe_image = pyglet.image.load(f"assets/pipe-{pipecolor}-top.png")
        bottom_pipe_image = pyglet.image.load(f"assets/pipe-{pipecolor}-bottom.png")
        self.top_pipe = pyglet.sprite.Sprite(top_pipe_image, pos, 320+height+width)
        self.bottom_pipe = pyglet.sprite.Sprite(bottom_pipe_image, pos, height)
        self.top_pipe_body = world.CreateKinematicBody(position=((pos+52)/self.PPM, (2*320+height+width)/self.PPM))
        self.top_pipe_fixture = self.top_pipe_body.CreatePolygonFixture(box=(26/self.PPM, 320/self.PPM))
        self.bottom_pipe_body = world.CreateKinematicBody(position=((pos+52)/self.PPM, height/self.PPM))
        self.bottom_pipe_fixture = self.bottom_pipe_body.CreatePolygonFixture(box=(26/self.PPM, 320/self.PPM))
        self.raycastcallback = RayCastObserver()
        self.raycast_first_hit = True

        self.top_pipe_body.linearVelocity = b2Vec2(-velocity, 0)
        self.bottom_pipe_body.linearVelocity = b2Vec2(-velocity, 0)

    def draw(self):
        self.top_pipe.position = self.top_pipe_body.position*self.PPM - b2Vec2(26, 320)
        self.bottom_pipe.position = self.bottom_pipe_body.position*self.PPM - b2Vec2(26, 0)
        self.top_pipe.draw()
        self.bottom_pipe.draw()

    def raycast(self):
        if not self.raycast_first_hit:
            return False
        xy = self.top_pipe_body.position
        xy2 = self.bottom_pipe_body.position
        xy = xy - b2Vec2(0, 16.05)
        xy2 = xy2 + b2Vec2(0, 16.05)
        self.world.RayCast(self.raycastcallback, xy, xy2)
        hit = self.raycastcallback.hit

        if hit:
            self.raycast_first_hit = False

        return hit

    def destroy_body(self):
        self.world.DestroyBody(self.top_pipe_body)
        self.world.DestroyBody(self.bottom_pipe_body)
