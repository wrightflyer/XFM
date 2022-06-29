import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

index = 0
index2 = 0
prevy = 0

class Anim:
    def __init__(self, fname, numFrames, xpos, ypos):
        self.fname = fname
        self.frames = []
        self.index = 0
        self.xpos = xpos
        self.ypos = ypos
        self.img = Image.open(fname)
        self.width = self.img.size[0]
        self.height = self.img.size[1]
        self.frameHeight = self.height / numFrames
        self.numFrames = numFrames
        for n in range(numFrames):
            tup = (0, self.frameHeight * n, self.width, self.frameHeight * (n + 1))
            frame = ImageTk.PhotoImage(self.img.crop(tup))
            self.frames.append(frame)
        print(self.width, self.height, self.frameHeight, self.numFrames)

    def getFrame(self):
        print(self.fname, "returning frame ", self.index)
        return self.frames[self.index]

    def setIndex(self, n):
        self.index = n

    def getSize(self):
        returrn (self.width, self.height, self.frameHeight)

    def inc(self):
        #print("consider inc, index=", self.index, "limit = ", self.numFrames)
        if (self.index < (self.numFrames - 1)):
            self.index = self.index + 1
            print(self.fname, "inc to", self.index)

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1
            print(self.fname, "dec to", self.index)

    def draw(self, cv):
        cv.delete(self.fname)
        cv.create_image(self.xpos, self.ypos, anchor=tk.NW, image = self.getFrame(), tag=self.fname)

    def click(self, cv, x, y):
        if x >= self.xpos and x <= (self.xpos + self.width):
            if y >= self.ypos and y <= (self.ypos + self.frameHeight):
                self.index = self.index + 1
                if self.index >= self.numFrames:
                    self.index = 0
                self.draw(cv)

def motion(event):
    global prevy
    newFrame = False

    if event.y < prevy:
        anim1.inc()
        #anim2.inc()
        newFrame = True

    if event.y > prevy:
        anim1.dec()
        #anim2.dec()
        newFrame = True

    if newFrame == True:
        anim1.draw(canvas)
        #anim2.draw(canvas)

    prevy = event.y

def button(event):
    anim2.click(canvas, event.x, event.y)
    #print(event)

window = Tk()
window.geometry("640x480")
window.bind('<B1-Motion>', motion)
window.bind('<Button>', button)

anim1 = Anim("possible2.png", 128, 10, 10)
anim2 = Anim("on_off2.png", 2, 130, 10)

canvas = Canvas(window, width = 300, height = 140, bg='#313132')
canvas.place(x=40, y=40)

anim1.draw(canvas)
anim2.draw(canvas)

window.mainloop()
