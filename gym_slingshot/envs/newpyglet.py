import pyglet
import math
from pyglet.gl import *

class main(pyglet.window.Window):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        glClearColor(0, 0, 0, 1)

        self.x, self.y = 0, 0
        rocket = pyglet.image.load('rocket.png')
        planet = pyglet.image.load('planet.png')
        target = pyglet.image.load('deathstar.png')
        flame = pyglet.image.load('flame.png')
        rocket.anchor_x = rocket.width // 2
        rocket.anchor_y = rocket.height // 2
        planet.anchor_x = planet.width // 2
        planet.anchor_y = planet.height // 2
        flame.anchor_x = flame.width // 2
        flame.anchor_y = flame.height // 2
        self.rocket = pyglet.sprite.Sprite(rocket, x=50, y=50)
        self.rocket.scale = 0.05
        self.planet = pyglet.sprite.Sprite(planet, x=50, y=50)
        self.planet.scale = 0.05
        self.target = pyglet.sprite.Sprite(target, x=50, y=50)
        self.target.scale = 0.05
        self.flame = pyglet.sprite.Sprite(flame, x=50, y=50)
        self.flame.scale = 0.01
        self.vertex_list = pyglet.graphics.vertex_list(0, ('v2i', ()))

        self.alive = 1

    def on_draw(self):
        self.render()

    def on_close(self):
        self.alive = 0

    def render(self, rocketx, rockety, rocket_angle, planetx, planety, targetx, targety, positions, flame):
        self.clear()
        self.rocket.update(rocketx, rockety,-rocket_angle*180/math.pi + 90)
        self.planet.update(planetx, planety)
        self.target.update(targetx, targety)
        self.flame.update(rocketx-(20+flame*3)*math.cos(rocket_angle), rockety-(20+flame*3)*math.sin(rocket_angle), -rocket_angle*180/math.pi - 90, 0.02*flame)
        self.vertex_list = pyglet.graphics.vertex_list(int(len(positions) / 2), ('v2i', positions))
        self.flame.draw()
        self.target.draw()
        self.planet.draw()
        self.rocket.draw()
        self.vertex_list.draw(GL_LINES)
        self.flip() # This updates the screen, very much important.

    def run(self):
        while self.alive == 1:
            self.render(1, 2)
            # -----------> This is key <----------
            # This is what replaces pyglet.app.run()
            # but is required for the GUI to not freeze.
            # Basically it flushes the event pool that otherwise
            # fill up and block the buffers and hangs stuff.
            event = self.dispatch_events()

# x = main()
# x.run()