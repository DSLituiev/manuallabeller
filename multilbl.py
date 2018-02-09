#!/usr/bin/env python3

from __future__ import print_function, division
import io
import os
import sys
import yaml
import urllib.request
from http.client import RemoteDisconnected
from itertools import cycle
import numpy as np
import pyglet
from time import time, sleep, gmtime, strftime
from pyglet.text import Label, HTMLLabel
# see http://www.poketcode.com/pyglet.html

from pyglet.gl import *

key = pyglet.window.key
#figbg = "test.jpg"

def url_exists(url):
    try:
        _ = urllib.request.urlopen(url)
        return True
    except urllib.error.HTTPError:
        return False

class rev_iter():
    def __init__(self, otheriter, processing=None):
        self.otheriter = otheriter
        self.buffer_ = []
        if processing is None:
            self.processing = lambda x: x
        else:
            self.processing = processing 

    def __iter__(self):
        return self

    def __next__(self):
        if len(self.buffer_)>0:
            return self.buffer_.pop()
        else:
            return self.processing(next(self.otheriter))

    def append(self, item):
        self.buffer_.append(item)

    def extend(self, items):
        assert type(items) in (list, tuple), "extend takes lists or tuples"
        self.buffer_.extend(items)

    def cache(self, num):
        for ii in range(num):
            try:
                self.buffer_.append(self.__next__())
            except StopIteration:
                pass


def filenames_from_file(filepath, indir=""):
    with open(filepath) as fh:
        for line in fh:
            line = line.split("\t")[0].split(",")[0]
            line = line.lstrip().rstrip()
            line = os.path.join(indir, line)
            if os.path.isfile(line):
                yield line
            else:
                print("not a file:\t%s" % line, file=sys.stderr)


class path_iter(rev_iter):
    def __init__(self, indir, filelist=None):
        self.buffer_ = []
        self.indir = indir
        if os.path.isdir(indir):
            if os.path.isfile(filelist):
                self.otheriter = filenames_from_file(indir=indir, filepath=filelist)
            else:
                files = os.listdir(indir)
                self.otheriter = filter(lambda x : ~os.path.isdir(x), files)

    def processing(self, ff):
        return os.path.join(self.indir, ff)


class LabelPgl(Label):
    def __init__(self, text, x=0, y=0, font_name = 'Times New Roman',
                 font_size=30):
        super(LabelPgl, self).__init__('Hello, world',
                  font_name=font_name,
                  font_size=font_size,
                  anchor_x='center', anchor_y='center')

    def _draw(self):
        self.draw()


def symbol_cycle(inp, symbols = ["", "M", "T", "X", "W"]):
    symcycle = cycle(symbols)
    for ii,ss in enumerate(symcycle):
        if inp.upper() == ss:
            outp = next(symcycle)
            break
        if ii==len(symbols):
            outp = symbols[0]
            break
    return outp


class NamedImage(pyglet.image.ImageData):
    def __init__(self, filename, *args, file=None, name=None, **kwargs):
        if name is None:
            self.filename = filename
        else:
            self.filename=name
        img  = pyglet.image.load(filename, *args, file=file, **kwargs)

        super(NamedImage, self).__init__(img.width, img.height, img.format, img._get_data(), img.pitch)
        #super(NamedImage, self).__init__(filename, *args, **kwargs)
    def __repr__(self):
        return self.filename

def get_pyglet_img_from_url(img_url, outf = 'noname.jpg'):
    try:
        web_response = urllib.request.urlopen(img_url)
    except urllib.error.HTTPError:
        raise FileNotFoundError("{} not found".format(img_url))
    img_data = web_response.read()
    dummy_file = io.BytesIO(img_data)
    pygimg = NamedImage(outf, file=dummy_file,
                        name=img_url.split('/')[-1])
    return pygimg


class CustomSprite(pyglet.sprite.Sprite):
    def __init__(self, texture_file, x=0, y=0, batch=None, ):
        ## Must load the texture as a image resource before initializing class:Sprite()
        if isinstance(texture_file, pyglet.image.ImageData):
            self.texture = texture_file
        elif texture_file.startswith("http"):
            self.texture = get_pyglet_img_from_url(texture_file)
        else:
            self.texture = pyglet.image.load(texture_file)

        super(CustomSprite, self).__init__(self.texture, x=x,y=y, batch=batch)
        #self.x = x
        #self.y = y

    def _draw(self):
        self.draw()

class MainScreen(pyglet.window.Window):
    def __init__ (self,
            indir="img",
            filelist=None,
            cache=False,
            logfile="labels.txt",
            width=800,
            height=600,
            background_color = (0, .5, .8, 1),
            symbols=["E", "T", "X", "W", "",]):
        """
        symbols: last is the default
        """
        super(MainScreen, self).__init__(width, height, fullscreen = False, vsync=False)
        pyglet.clock.schedule_interval(self.update, 1.0/128.0)
        pyglet.clock.set_fps_limit(128)

        self.symbol_list = symbols 
        self.IMAGE_ROWS = 2
        self.N_IMAGES = 4
        self.img_count = 0
        self.imgpaths = []
        self.prev_imgpaths = []

        if type(indir) is list:
            "in the case of list input"
            self.img_iter = rev_iter(iter(indir))
        elif type(indir) is iter:
            self.img_iter = rev_iter(indir)
        elif os.path.isdir(indir): 
            self.img_iter = path_iter(indir, filelist=filelist)
        else:
            raise ValueErroe("Unknown type of `indir`")

        if os.path.isfile(logfile):
            with open(logfile) as self.logfile:
                line = ''
                nn = 0
                for nn, line in enumerate(self.logfile):
                    #print(line, end='')
                    pass
                self.img_count = nn
                line = line.split("\t")
                if len(line)>2 or nn>1:
                    lastfile = line[1]
                    # !!!
                    for ff in self.img_iter:
                        if ff==lastfile:
                            print("%d records found" % (nn+1))
                            print("last line in previous session:\n%s" % line)
                            print("=" * 20)
                            break
                    self.logfile = open(logfile, "a")
                else:
                    self.logfile = open(logfile, "w")
        else:
            self.logfile = open(logfile, "w")

        if cache:
            self.cache = True

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
        self.logfile.flush()
        self.logfile.close()

    def on_draw(self):
        if hasattr(self, 'batch'):
             self.batch.draw()
        self.render()

    def update(self):
        if self.cache:
            self.cache = None
            print("caching...")
            self.img_iter.processing = get_pyglet_img_from_url


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
        for nn, sub_sprite in enumerate(self.sprites):
            if (x > sub_sprite.x and
                x < (sub_sprite.x + sub_sprite.width) and
                y > sub_sprite.y and
                y < (sub_sprite.y + sub_sprite.height)
                ):
                print("click on: %d\tbutton: %d" % (nn, button))
                if button == pyglet.window.mouse.LEFT:
                    symbol = symbol_cycle(self.symbols[nn], symbols=self.symbol_list)
                elif button == pyglet.window.mouse.RIGHT:
                    symbol = symbol_cycle(self.symbols[nn], symbols=self.symbol_list[::-1])
                self.symbols[nn] = symbol
                 
                label = HTMLLabel(
                       '''<font face="Times New Roman" size="400" color="red">
                       {}</font>'''.format((symbol).upper() ),
                       x = sub_sprite.x + sub_sprite.width//2,
                       y = sub_sprite.y + sub_sprite.height,
                       height = sub_sprite.height//8,
                       width = sub_sprite.width//8,
                       anchor_x='center', anchor_y='center')
                label.font_size = 100
                label.draw()
                self.labels[nn] = label


    def on_key_press(self, symbol, modifiers):
        if hasattr(self, "label"):
            #self.label.delete()
            self.label = None
        #print(time(), self.prevpath, symbol, chr(symbol), sep="\t")

        if symbol == key.BACKSPACE or symbol == key.LEFT:
            if hasattr(self, "prev_imgpaths") and len(self.prev_imgpaths)>0:
                self.img_count -= 2*self.N_IMAGES
                #print('appending two files:\n%s\n%s' % (self.prevpath,self.prevprevpath))
                self.img_iter.extend(self.prev_imgpaths[::-1])
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

    def _output_labels_(self, time=""):
        if hasattr(self, "imgpaths"):
            print("saving to", self.logfile)
            for nn, pp in enumerate(self.imgpaths):
                symbol = self.symbols[nn]
                print(time, pp, ord(symbol) if len(symbol) is 1 else "", symbol, sep="\t")
                print(time, pp, ord(symbol) if len(symbol) is 1 else "", symbol, sep="\t", file=self.logfile)


    def on_key_release(self, symbol, modifiers):
        if hasattr(self, "label"):
            #self.label.delete()
            self.label = None
        if symbol == key.ESCAPE: # [ESC]
            self.alive = 0
        #elif symbol == key.BACKSPACE:
        #    pass
            #self.prevpath = self.prevprevpath
            #imgpath = self.prevpath
            # self.imgpath = next(self.img_iter)
            # self.sprite = CustomSprite(self.imgpath, x=10, y=10)
        elif symbol in [key.ENTER, key.RETURN, key.SPACE, key.RIGHT, key.LEFT, key.BACKSPACE]:
            XLOC = YLOC = 300
            XDIM = YDIM = 40
            time_ = strftime("%Y/%m/%d %H:%M:%S", gmtime())
            self.label = HTMLLabel(
                       '''<font face="Times New Roman" size="400" color="red">
                       {}</font>'''.format(self.img_count),
                       x = 2.125 *XLOC,
                       y = YLOC,
                       height = XDIM,
                       width = YDIM,
                       anchor_x='center', anchor_y='center')
            self.label.font_size = 40
            self.label.draw()
            self._output_labels_(time=time_)
            try:
                self.prev_imgpaths = self.imgpaths
                self.imgpaths = []
                for nn in range(self.N_IMAGES):
                    self.img_count += 1
                    self.imgpaths.append(next(self.img_iter))
            except StopIteration:
                print("saving the rest of files") 
                self._output_labels_(time=time_)
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
                print('displaying', self.img_count + ii - self.N_IMAGES, pp)
                x = (ii//self.IMAGE_ROWS) * XSTEP 
                y = (ii % self.IMAGE_ROWS) * XSTEP
                try:
                    self.sprites.append(
                            CustomSprite(pp, x, y, batch=self.batch)
                                       )
                except FileNotFoundError as ee:
                    print(ee, file=sys.stderr)
                    self.imgpaths[ii] = ''
            self.symbols = np.asarray(['']*(ii+1))
            self.labels = np.asarray([None]*(ii+1))
        else:
            print(str(symbol))

        if symbol is not key.BACKSPACE:
            self.flip()
            self.img_iter.cache(self.N_IMAGES)
  
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

import subprocess
import sys


def sshconnect(host, inport=5000, outport=5000, cmd=None):
    cmdlist =["ssh", "-L", "{}:localhost:{}".format(inport,outport),
                host] 
    if cmd is not None:
        cmdlist.append(cmd)
    print('>' + " ".join(cmdlist))
    ssh = subprocess.Popen(cmdlist,
                           shell=False,
                           stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE)
    result = ssh.stdout.readlines()
    if result == []:
        error = ssh.stderr.readlines()
        print("ERROR: %s" % error, file=sys.stderr)
    else:
        print(result)
    return


if __name__=='__main__':
    with open("config.yaml", 'r') as stream:
        descr = yaml.load(stream)

    if 'host' in descr:
        sshconnect(descr['host'], cmd=descr.get('cmd'))
    if 'url' in descr:
        url = descr['url']
        indir = 'data'
        if 'meta' not in descr:
            ls_url = 'http://{}/ls'.format(url)
            print("reading file list:\t{}".format(ls_url))
            filelist = urllib.request.urlopen(ls_url).read().decode().split('\n')
            filelist = ['http://{}/{}/{}'.format(url, indir, x) for x in filelist 
                if x.endswith("jpeg") or
                x.endswith("png")]
            
            print(filelist)
        else:
            ls_url = 'http://{}/{}'.format(descr['url'], descr["meta"])
            print("reading file list:\t{}".format(ls_url))
            try:
                abort = False
                filelist = urllib.request.urlopen(ls_url).read().decode().split('\n')
            except RemoteDisconnected as ee:
                abort = True
            finally:
                if abort:
                    raise RemoteDisconnected("MAKE SURE THE SERVER IS RUNNING")
            filelist = ['http://{}/{}/{}'.format(url, indir, x) for x in filelist
                if x.endswith("jpeg") or
                x.endswith("png")]

            print("RECEIVED A LIST OF {} FILES".format(len(filelist)))
            filelist= [ff for ff in filelist if url_exists(ff)]
            print("READING A LIST OF {} FILES".format(len(filelist)))

    for kk in sorted(descr.keys()):
        print("{}\t{}".format(kk,descr[kk]))

    if 'url' in descr:
        descr["meta"] = None
        descr["indir"] = filelist

    app = MainScreen(indir=descr["indir"], logfile=descr["logfile"], 
            filelist=descr["meta"],
            cache=True,
            symbols=descr.get("symbols", ["E", "T", "X", "W", "",])
            )
    app.run()
