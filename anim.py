import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk

class Anim:
    def __init__(self, keyname, title, fname, numFrames, xpos, ypos):
        self.keyname = keyname
        self.fname = fname
        self.frames = []
        self.index = 0
        self.xpos = xpos
        self.ypos = ypos
        self.img = Image.open(fname)
        self.width = self.img.size[0]
        self.height = self.img.size[1]
        self.frameHeight = int(self.height / numFrames)
        self.numFrames = numFrames
        for n in range(numFrames):
            tup = (0, self.frameHeight * n, self.width, self.frameHeight * (n + 1))
            frame = ImageTk.PhotoImage(self.img.crop(tup))
            self.frames.append(frame)
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#313132', highlightthickness=0)
        self.canvas.place(x=self.xpos, y=self.ypos)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<Button>', self.button_click)
        if len(title) > 0:
            self.canvas.create_text(self.width / 2, 4, text=title, fill='#ffffff')
        self.prevy = 0
        self.prevx = 0

    def getFrame(self):
        return self.frames[self.index]

    def setIndex(self, n):
        if n >= 0 and n < (self.numFrames - 1):
            self.index = n

    def getIndex(self):
        return self.index

    def getInfo(self):
        return (self.keyname, self.fname, self.index, self.xpos, self.ypos, self.width, self.frameHeight, self.height, self.numFrames)

    def inc(self):
        if (self.index < (self.numFrames - 1)):
            self.index = self.index + 1

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1

    def draw(self):
        self.canvas.delete(self.fname)
        self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.fname)

    def motion(self, event):
        newFrame = False

        if event.y < self.prevy or event.x > self.prevx:
            self.inc()
            newFrame = True

        if event.y > self.prevy or event.x < self.prevx:
            self.dec()
            newFrame = True

        if newFrame == True:
            self.draw()

        self.prevy = event.y
        self.prevx = event.x

    def button_click(self, event):
        if event.num == 1:
            self.index = self.index + 1
            if self.index >= self.numFrames:
                self.index = 0
        if event.num == 3:
            self.index = self.index - 1
            if self.index < 0:
                self.index = (self.numFrames - 1)
        self.draw()

window = Tk()
window.geometry("1290x1100")
window.configure(bg='#31FF32')
rawback = Image.open("xfm/resources/dark-grey-texture-abstract-hd-wallpaper-1920x1200-1223.jpg")
rawback = rawback.resize((680, 440), Image.Resampling.LANCZOS)
backimg = ImageTk.PhotoImage(rawback)
Label(image=backimg).place(x=2, y=4)
Label(image=backimg).place(x=690, y=4)
Label(image=backimg).place(x=2, y=442)
Label(image=backimg).place(x=632, y=442)
#window.wm_attributes('-transparentcolor', '#123456')

anims = {
    "OP1:Output" :   [ "Output",    "possible2_0_127.png",      128,    140, 10 ],
    "OP1:Feedback" : [ "Feedback",  "possible2-63.0_64.0.png",  128,    40, 100 ],
    "OP1:Lgain" :    [ "L Gain",    "on_off3.png",              2,      240, 10 ],
    "OP1:Rgain" :    [ "R Gain",    "on_off3.png",              2,      310, 10 ],
    "OP1:Peq" :      [ "Pitch EQ",  "on_off3.png",              2,      380, 10 ],
    "OP1:Fixed" :    [ "Fixed",     "on_off3.png",              2,      450, 10 ],
    "OP1:OP2In" :    [ "OP2 Input", "possible2_0_127.png",      128,    140, 100 ],
    "OP1:OP3In" :    [ "OP3 Input", "possible2_0_127.png",      128,    40, 190 ],
    "OP1:OP4In" :    [ "OP4 Input", "possible2_0_127.png",      128,    140, 190 ],
    "OP1:Level" :    [ "Level",     "possible2-18_18.png",      37,      40, 280 ],
    "OP1:Atime" :    [ "A Time",    "slide_back_h.png",         128,    10, 380 ],
    "OP1:Dtime" :    [ "D Time",    "slide_back_h.png",         128,    180, 380 ],
    "OP1:Stime" :    [ "S Time",    "slide_back_h.png",         128,    350, 380 ],
    "OP1:Rtime" :    [ "R Time",    "slide_back_h.png",         128,    520, 380 ],
    "OP2:DLevel" :   [ "D Level",   "slide_back_v.png",         128,    240, 140 ],
#    "Name:chr0" :    [ "",          "lcd_chars.png",            36,     240, 10 ],
#    "Name:chr1" :    [ "",          "lcd_chars.png",            36,     240 + 64 - 11, 10 ],
#    "Name:chr2" :    [ "",          "lcd_chars.png",            36,     240 + ((64 - 11) * 2), 10 ],
#    "Name:chr3":     [ "",          "lcd_chars.png",            36,     240 + ((64 - 11) * 3), 10 ]
}

animlist = []
for key in anims:
    #print(key, anims[key])
    thisanim = Anim(key, anims[key][0], anims[key][1], anims[key][2], anims[key][3], anims[key][4])
    animlist.append(thisanim)
    thisanim.draw()
    
for a in animlist:
    print(a.getInfo())

window.mainloop()
