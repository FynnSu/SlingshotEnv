from pyglet.gl import *
from math import *
import pyglet

class MyWindow(pyglet.window.Window):
  def __init__(self, *args, **kwargs):
    super().__init__(*args, **kwargs)
    glClearColor(1, 1, 1, 1)
    self.vertex_list = pyglet.graphics.vertex_list(0, ('v2i', ()))
    self.planet = pyglet.graphics.vertex_list(0, ('v2i', ()))
    self.circle = pyglet.graphics.vertex_list(0, ('v2i', ()))

  def set_planet(self, x, y):
    self.planet = pyglet.graphics.vertex_list(1, ('v2i', (x, y)), ('c3B', (0, 255, 0)))
    self.planet_circle = self.makeCircle(100, x, y)
  
  def set_target(self, x, y):
    self.target_circle = self.makeCircle(100, x, y)



  def makeCircle(self, numPoints, x, y):
    verts = []
    for i in range(numPoints):
        angle = radians(float(i)/numPoints * 360.0)
        x = cos(angle) + x
        y = sin(angle) + y
        verts += [x,y]
    return pyglet.graphics.vertex_list(numPoints, ('v2f', verts))

  def update_points(self, new_points):
    # colors = []
    # for i in range(int(len(new_points) / 2)):
    #   colors.append(255)
    #   colors.append(0)
    #   colors.append(0)
    self.vertex_list = pyglet.graphics.vertex_list(int(len(new_points) / 2), ('v2i', new_points)) # ('c3B', colors))
  
  
  def on_draw(self):
    # self.clear()
    # vertex_list = pyglet.graphics.vertex_list(2, ('v2i', (10, 15, 30, 35)), ('c3B', (0, 255, 0, 255, 0, 0)))
    self.vertex_list.draw(GL_LINES)
    # self.planet.draw(pyglet.gl.GL_POINTS)
    self.planet_circle.draw(GL_LINE_LOOP)
    self.target_circle.draw(GL_LINE_LOOP)

if __name__ == '__main__':
  window = MyWindow(100, 100, "Test")
  pyglet.app.run()
