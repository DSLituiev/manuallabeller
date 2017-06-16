from __future__ import print_function, division
import os
from itertools import cycle
import numpy as np
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


class LabelPgl(Label):
    def __init__(self, text, x=0, y=0, font_name = 'Times New Roman',
                 font_size=36):
        super(LabelPgl, self).__init__('Hello, world',
                  font_name=font_name,
                  font_size=font_size,
                  anchor_x='center', anchor_y='center')

    def _draw(self):
        self.draw()


def symbol_cycle(inp, symbols = ["", "S", "M", "X"]):
    symcycle = cycle(symbols)
    for ii,ss in enumerate(symcycle):
        if inp.upper() == ss:
            outp = next(symcycle)
            break
        if ii==len(symbols):
            outp = symbols[0]
            break
    return outp

class CustomSprite(pyglet.sprite.Sprite):
    def __init__(self, texture_file, x=0, y=0, batch=None):
        ## Must load the texture as a image resource before initializing class:Sprite()
        self.texture = pyglet.image.load(texture_file)

        super(CustomSprite, self).__init__(self.texture, x=x,y=y, batch=batch)
        #self.x = x
        #self.y = y

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

        self.IMAGE_ROWS = 2
        self.N_IMAGES = 4
        if type(indir) is list:
            "in the case of list input"
            self.img_iter = rev_iter(iter(indir))
        elif type(indir) is iter:
            self.img_iter = rev_iter(indir)
        elif os.path.isdir(indir):
            self.img_iter = path_iter(indir)


        if os.path.isfile(logfile):
            with open(logfile) as self.logfile:
                line = ''
                for line in self.logfile:
                    print(line, end='')
                    pass
                line = line.split("\t")
                if len(line)>2:
                    lastfile = line[1]
                    for ff in self.img_iter:
                        if ff==lastfile:
                            break
                    self.logfile = open(logfile, "a")
                else:
                    self.logfile = open(logfile, "w")
        else:
            self.logfile = open(logfile, "w")


        self.x, self.y = 0, 0

        #self.bg = CustomSprite(figbg)
        self.sprites = []
        self.alive = 1
        # sets the background color
        gl.glClearColor(*background_color)

        ######################3
        self.label = HTMLLabel(
                   '''<font face="Times New Roman" size="400" color="blue">
                   {}</font>'''.format("Press space or return to start"),
                   x=self.width//2, y=self.height//2,
                   height = self.height//8,
                   width = self.width//8,
                   anchor_x='center', anchor_y='center')
        self.label.font_size = 30
        self.label.draw()


    def __del__(self):
        self.logfile.close()

    def on_draw(self):
        if hasattr(self, 'batch'):
             self.batch.draw()
        self.render()

    def on_close(self):
        self.alive = 0

    def theend(self):
        print('The end')
        self.label = HTMLLabel(
                   '''<font face="Times New Roman" size="42" color="blue">
                    END</font>''',
                   x=self.width//2, y=self.height//2,
                   anchor_x='center', anchor_y='center')
        self.label.font_size = 120
        self.label.draw()

    def on_mouse_press(self, x, y, button, modifiers):
        SYMBOLS = ["", "S", "M", "X"]
        for nn, sub_sprite in enumerate(self.sprites):
            if (x > sub_sprite.x and
                x < (sub_sprite.x + sub_sprite.width) and
                y > sub_sprite.y and
                y < (sub_sprite.y + sub_sprite.height)
                ):
                print("click on: %d\tbutton: %d" % (nn, button))
                if button == pyglet.window.mouse.LEFT:
                    symbol = symbol_cycle(self.symbols[nn], symbols=SYMBOLS)
                elif button == pyglet.window.mouse.RIGHT:
                    symbol = symbol_cycle(self.symbols[nn], symbols=SYMBOLS[::-1])
                self.symbols[nn] = symbol
                 
                label = HTMLLabel(
                       '''<font face="Times New Roman" size="400" color="red">
                       {}</font>'''.format((symbol).upper() ),
                       x = sub_sprite.x + sub_sprite.width//2,
                       y = sub_sprite.y + sub_sprite.height,
                       height = sub_sprite.height//8,
                       width = sub_sprite.width//8,
                       anchor_x='center', anchor_y='center')
                label.font_size = 200
                label.draw()
                self.labels[nn] = label


    def on_key_press(self, symbol, modifiers):
        if hasattr(self, "label"):
            #self.label.delete()
            self.label = None
        #print(time(), self.prevpath, symbol, chr(symbol), sep="\t")

        if symbol == key.BACKSPACE:
            self.labels = [None]
        else:
            self.label = HTMLLabel(
                       '''<font face="Times New Roman" size="400" color="red">
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
        elif symbol == key.BACKSPACE:
            #self.prevpath = self.prevprevpath
            #imgpath = self.prevpath
            self.imgpath = next(self.img_iter)
            self.sprite = CustomSprite(self.imgpath, x=10, y=10)
        elif symbol in [key.ENTER, key.RETURN, key.SPACE]:
            time_ = strftime("%Y/%m/%d %H:%M:%S", gmtime())
            if hasattr(self, "imgpaths"):
                for nn, pp in enumerate(self.imgpaths):
                    symbol = self.symbols[nn]
                    print(time_, pp, ord(symbol) if len(symbol) is 1 else "", symbol, sep="\t")
                    print(time_, pp, ord(symbol) if len(symbol) is 1 else "", symbol, sep="\t", file=self.logfile)
            try:
                self.imgpaths = []
                for nn in range(self.N_IMAGES):
                    self.imgpaths.append(next(self.img_iter))
            except StopIteration:
                self.label = None
                self.theend()
                self.flip()
                sleep(1)
                self.alive = 0
                return
            self.batch = pyglet.graphics.Batch()
            self.sprites = []
            self.labels = []
            self.symbols = []
            XSTEP = 300
            for ii, pp in enumerate(self.imgpaths):
                print('displaying', ii, pp)
                x = (ii//self.IMAGE_ROWS) * XSTEP 
                y = (ii % self.IMAGE_ROWS) * XSTEP
                self.sprites.append(
                        CustomSprite(pp, x, y, batch=self.batch)
                                   )
            self.symbols = np.asarray(['']*(ii+1))
            self.labels = np.asarray([None]*(ii+1))
        else:
            print(str(symbol))
            # self.sprite = CustomSprite(self.imgpath, x=10, y=10)
            # self.prevprevpath = self.prevpath
            #self.prevpath = self.imgpath

  
    def render(self):
        self.clear()
        #self.bg.draw()
        if hasattr(self, "sprites"):
            for ss in self.sprites:
                ss.draw()

        if hasattr(self, "label") and self.label is not None:
            # Draw text
            self.label.draw()
        if hasattr(self, "labels") and self.labels is not None:
            for label in self.labels:
                if label:
                    label.draw()

        self.flip()

    def run(self):
        while self.alive == 1:
            self.render()

            # -----------> This is key <----------
            # This is what replaces pyglet.app.run()
            # but is required for the GUI to not freeze
            #
            event = self.dispatch_events()


if __name__=='__main__':
    with open("datadescr.yaml", 'r') as stream:
        descr = yaml.load(stream)

    x = MainScreen(indir=descr["indir"], logfile=descr["logfile"])
    x.run()
