import os
import pyglet
from time import time, sleep, gmtime, strftime
from pyglet.text import Label, HTMLLabel
# see http://www.poketcode.com/pyglet.html

from pyglet.gl import *

key = pyglet.window.key
#figbg = "test.jpg"

class rev_iter():
    def __init__(self, otheriter):
        self.otheriter = otheriter
        self.buffer_ = []
    def __iter__(self):
        return self

    def modify_out(self, x):
        return x
    def __next__(self):
        if len(self.buffer_)>0:
            return self.buffer_.pop()
        else:
            return self.modify_out(next(self.otheriter))
    def append(self, item):
        self.buffer_.append(item)

class path_iter(rev_iter):
    def __init__(self, indir):
        self.buffer_ = []
        self.indir = indir
        files = os.listdir(indir)
        self.otheriter = filter(lambda x : ~os.path.isdir(x), files)
    def modify_out(self, ff):
        return os.path.join(self.indir, ff)

def img_iter(indir="img"):
    return path_iter(indir)

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

        self.img_iter = img_iter()

        if os.path.isfile(logfile):
            with open(logfile) as self.logfile:
                for line in self.logfile:
                    print(line, end='')
                    pass
                line = line.split("\t")
                assert len(line)>2, "last line:\n%s" % str(line)
                lastfile = line[1]

            for ff in self.img_iter:
                if ff==lastfile:
                    break
            self.logfile = open(logfile, "a")
        else:
            self.logfile = open(logfile, "w")

        self.prevpath = ''
        #self.img_list = list(img_iter())

        self.x, self.y = 0, 0

        #self.bg = CustomSprite(figbg)
        self.sprites = []
        self.alive = 1
        # sets the background color
        gl.glClearColor(*background_color)

    def __del__(self):
        self.logfile.close()

    def on_draw(self):
        self.render()

    def on_close(self):
        self.alive = 0

    def theend(self):
        print('The end')
        self.label = HTMLLabel(
                   '''<font face="Times New Roman" size="42" color="red">
                    END</font>''',
                   x=self.width//2, y=self.height//2,
                   anchor_x='center', anchor_y='center')
        self.label.font_size = 120
        self.label.draw()

    def on_key_press(self, symbol, modifiers):
        if hasattr(self, "label"):
            #self.label.delete()
            self.label = None
        #print(time(), self.prevpath, symbol, chr(symbol), sep="\t")

        if symbol == key.BACKSPACE:
            if hasattr(self, "prevpath"):
                #print('appending two files:\n%s\n%s' % (self.prevpath,self.prevprevpath))
                self.img_iter.append(self.prevpath)
                self.img_iter.append(self.prevprevpath)
                self.prevpath = self.prevprevpath
        else:
            self.label = HTMLLabel(
                       '''<font face="Times New Roman" size="400" color="blue">
                       {}</font>'''.format(chr(symbol).upper() ),
                       x=self.width//2, y=self.height//2,
                       height = self.height//8,
                       width = self.width//8,
                       anchor_x='center', anchor_y='center')
            self.label.font_size = 200
            self.label.draw()

    def on_key_release(self, symbol, modifiers):
        if hasattr(self, "label"):
            #self.label.delete()
            self.label = None
        if symbol == key.ESCAPE: # [ESC]
            self.alive = 0
        elif symbol == key.R:
            print('Rendering hello')
            self.label = HTMLLabel(
                       '''<font face="Times New Roman" size="42" color="red">
                       Hello, <i>world</i></font>''',
                       x=self.width//2, y=self.height//2,
                       anchor_x='center', anchor_y='center')
            self.label.font_size = 120
            self.label.draw()
        elif symbol == key.BACKSPACE:
            #self.prevpath = self.prevprevpath
            #imgpath = self.prevpath
            self.imgpath = next(self.img_iter)
            self.sprite = CustomSprite(self.imgpath, x=10, y=10)
        else:
            time_ = strftime("%Y/%m/%d %H:%M:%S", gmtime())
            if self.prevpath:
                print(time_, self.prevpath, symbol, chr(symbol), sep="\t")
                print(time_, self.prevpath, symbol, chr(symbol), sep="\t", file=self.logfile)
            try:
                self.imgpath = next(self.img_iter)
            except StopIteration:
                self.label = None
                self.theend()
                self.flip()
                sleep(1)
                self.alive = 0
                return
            self.sprite = CustomSprite(self.imgpath, x=10, y=10)
            self.prevprevpath = self.prevpath
            self.prevpath = self.imgpath

  
    def render(self):
        self.clear()
        #self.bg.draw()
        if hasattr(self, "sprite"):
            self.sprite.draw()

        if hasattr(self, "label") and self.label is not None:
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


