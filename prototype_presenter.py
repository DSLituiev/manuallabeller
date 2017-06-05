import os
import pyglet
from time import time, sleep
from pyglet.text import Label, HTMLLabel
# see http://www.poketcode.com/pyglet.html

from pyglet.gl import *

key = pyglet.window.key
#figbg = "test.jpg"

def img_iter(indir="img"):
    files = os.listdir(indir)
    files = filter(lambda x : ~os.path.isdir(x), files)
    for ff in files:
        yield os.path.join(indir, ff)

class LabelPgl(Label):
    def __init__(self, text, x=0, y=0, font_name = 'Times New Roman',
                 font_size=36):
        super(LabelPgl, self).__init__('Hello, world',
                  font_name=font_name,
                  font_size=font_size,
                  anchor_x='center', anchor_y='center')

    def _draw(self):
        self.draw()


class CustomSprite(pyglet.sprite.Sprite):
    def __init__(self, texture_file, x=0, y=0):
        ## Must load the texture as a image resource before initializing class:Sprite()
        self.texture = pyglet.image.load(texture_file)

        super(CustomSprite, self).__init__(self.texture)
        self.x = x
        self.y = y

    def _draw(self):
        self.draw()

class MainScreen(pyglet.window.Window):
    def __init__ (self,
            indir="img",
            logfile="labels.txt",
            width=800,
            height=600,
            background_color = (0, .5, .8, 1)):
        super(MainScreen, self).__init__(width, height, fullscreen = False)

        self.prevpath = ''
        self.img_iter = img_iter()

        self.x, self.y = 0, 0

        #self.bg = CustomSprite(figbg)
        self.sprites = []
        self.alive = 1
        # sets the background color
        gl.glClearColor(*background_color)

    def on_draw(self):
        self.render()

    def on_close(self):
        self.alive = 0

    def clear_sprites(self):
        try:
            self.clear()
            self.sprites.pop()
        except:
            pass

    def on_key_press(self, symbol, modifiers):
        print(time(), self.prevpath, symbol, chr(symbol), sep="\t")
        imgpath = next(self.img_iter)

        if symbol == key.ESCAPE: # [ESC]
            self.alive = 0
        elif symbol == key.C:
            print('Rendering cat')
            self.clear_sprites()
            self.sprites.append(
                    CustomSprite('img/cat.jpg', x=10, y=10)
                               )
        elif symbol == key.R:
            print('Rendering hello')
            self.label = HTMLLabel(
                       '''<font face="Times New Roman" size="42" color="white">
                       Hello, <i>world</i></font>''',
                       x=self.width//2, y=self.height//2,
                       anchor_x='center', anchor_y='center')
            self.label.draw()
        else:
            self.sprites.append(
                                CustomSprite(imgpath, x=10, y=10)
                               )
        self.prevpath = imgpath
       
    def render(self):
        self.clear()
        #self.bg.draw()

        for sprite_obj in self.sprites:
            sprite_obj._draw()

        if hasattr(self, "label"):
            # Draw text
            self.label.draw()

        self.flip()

    def run(self):
        while self.alive == 1:
            self.render()

            # -----------> This is key <----------
            # This is what replaces pyglet.app.run()
            # but is required for the GUI to not freeze
            #
            event = self.dispatch_events()

x = MainScreen()
x.run()


