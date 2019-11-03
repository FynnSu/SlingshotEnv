import pyglet
import resources

game_window = pyglet.window.Window()

player = pyglet.sprite.Sprite(resources.player, x=100, y=100)
player_x = 0
player_y = 0


@game_window.event
def on_draw():
    game_window.clear()
    player.draw()

def update(x):
    player.scale = 0.5
    player.rotation += 5
    player.x += 1

if __name__ == '__main__':

    pyglet.clock.schedule_interval(update, 0.01)
    pyglet.app.run()