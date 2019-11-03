import pyglet

pyglet.resource.path = ["./resources/"]
pyglet.resource.reindex()

player = pyglet.resource.image("triangle.png")