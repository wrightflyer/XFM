import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import json

class Adsr:
    def __init__(self, key, xpos, ypos):
        self.key = key
        self.xpos = xpos
        self.ypos = ypos
        self.canvas = Canvas(window, width=256, height=128, bg='#707070')
        self.canvas.place(x = xpos, y = ypos)
    
    def update(self, at, al, dt, dl, st, sl, rt, rl):
        #print(activecanvas, at, al, dt, dl, st, sl, rt, rl)
        self.canvas.delete("all")
        ax = at
        ay = 128 - al

        dx = dt + ax
        dy = 128 - dl

        sx = st + dx
        sy = 128 - sl

        rx = rt + sx
        ry = 128 - rl

        padding = 256 - (at + dt + st + rt)

        self.canvas.create_line(0, 128, ax, ay, width=3, fill='#000CFF')
        self.canvas.create_line(ax, ay, dx, dy, width=3, fill='#000CFF')
        self.canvas.create_line(dx, dy, sx, sy, width=3, fill='#000CFF')
        self.canvas.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1), fill='#000CFF')
        self.canvas.create_line(sx + padding, sy, 256, ry, width=3, fill='#000CFF')

    def init(self):
        self.update(0, 127, 0, 127, 0, 127, 0, 0)

    def draw(self):
        op = self.key
        key = op + "ATime"
        at = controllist[key][0].getIndex()
        key = op + "DTime"
        dt = controllist[key][0].getIndex()
        key = op + "STime"
        st = controllist[key][0].getIndex()
        key = op + "RTime"
        rt = controllist[key][0].getIndex()

        key = op + "ALevel"
        al = controllist[key][0].getIndex()
        key = op + "DLevel"
        dl = controllist[key][0].getIndex()
        key = op + "SLevel"
        sl = controllist[key][0].getIndex()
        key = op + "RLevel"
        rl = controllist[key][0].getIndex()
        #print("draw ADSR ", op, "with ",at, al, dt, dl, st, sl, rt, rl)
        self.update(at, al, dt, dl, st, sl, rt, rl)

class Anim:
    def __init__(self, keyname, title, ctrl, xpos, ypos):
        self.keyname = keyname
        self.ctrl = ctrl
        self.index = 0
        self.xpos = xpos
        self.ypos = ypos
        self.width = ctrlimgs[ctrl]["width"]
        self.height = ctrlimgs[ctrl]["height"]
        numFrames = ctrlimgs[ctrl]["numframes"]
        self.frameHeight = ctrlimgs[ctrl]["frameH"]
        self.numFrames = numFrames
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#202020', highlightthickness=0)
        #self.canvas.attributes("-alpha", 0.5)
        self.canvas.place(x=self.xpos, y=self.ypos)
        self.canvas.bind('<B1-Motion>', self.motion)
        self.canvas.bind('<Button>', self.button_click)
        if len(title) > 0:
            self.canvas.create_text(self.width / 2, 4, text=title, fill='#ffffff')
        self.prevy = 0
        self.prevx = 0

    def getFrame(self):
        return ctrlimgs[self.ctrl]["frames"][self.index]

    def setIndex(self, n):
        #print(self.keyname, "set value=", n, "limit=", self.numFrames)
        if n >= 0 and n < self.numFrames:
            #print("so settint it now")
            self.index = n

    def getIndex(self):
        return self.index

    def getKey(self):
        return self.keyname

    def getInfo(self):
        return (self.keyname, self.ctrl, self.index, self.xpos, self.ypos, self.width, self.frameHeight, self.height, self.numFrames)

    def inc(self):
        if (self.index < (self.numFrames - 1)):
            self.index = self.index + 1

    def dec(self):
        if self.index >= 1:
            self.index = self.index - 1

    def draw(self):
        #print("draw", self.keyname, "index=", self.index)
        self.canvas.delete(self.keyname)
        self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)

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
            ctrlType = ctrlimgs[self.ctrl]["type"]
            if ctrlType == "slideV" or ctrlType == "slideH":
                op = self.keyname.split(':')[0] + ":"
                adsrs[op].draw()

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


#============================= THE start ================================
window = Tk()
window.geometry("1720x890")
window.title("Quick Edit for Liven XFM")
window.configure(bg='#313131')
window.resizable(False, False)

# Textured grey used as background for all 5 sub-windows
rawback = Image.open("xfm/resources/dark-grey-texture-abstract-hd-wallpaper-1920x1200-1223.jpg")
#rawback = rawback.resize((680, 440), Image.Resampling.LANCZOS)
opback = rawback.resize((685, 440))
backimg = ImageTk.PhotoImage(opback)

# Background for OP1 edit top left
back1 = Canvas(width = 684, height = 440)
back1.place(x=0, y=0)
back1.create_image(0, 0, anchor=tk.NW, image = backimg)

# Background for OP2 edit top mid
back2 = Canvas(width = 684, height = 440)
back2.place(x=688, y=0)
back2.create_image(0, 0, anchor=tk.NW, image = backimg)

# Background for OP3 edit bot left
back3 = Canvas(width = 684, height = 440)
back3.place(x=0, y=442)
back3.create_image(0, 0, anchor=tk.NW, image = backimg)

# Background for OP4 edit bot mid
back4 = Canvas(width = 684, height = 440)
back4.place(x=688, y=442)
back4.create_image(0, 0, anchor=tk.NW, image = backimg)

# Background for pitch/master edit right
mstrback=rawback.resize((340, 882))
mstrimg = ImageTk.PhotoImage(mstrback)
backm = Canvas(width = 340, height = 882)
backm.place(x=1375, y=0)
backm.create_image(0, 0, anchor=tk.NW, image = mstrimg)

# "Quick Edit for Sonicware Liven XFM logo"
rawlogo = Image.open("logo.png")
logo = ImageTk.PhotoImage(rawlogo)
backm.create_image(30, 630, anchor=tk.NW, image = logo)

# The OP1..OP4 logos all packed into one 4 frame PNG
rawlogo = Image.open("op_logo.png")
logwidth = rawlogo.size[0]
frameH = rawlogo.size[1] / 4

# Place "OP1" top left
tup = (0, 0, logwidth, frameH)
op1logo = ImageTk.PhotoImage(rawlogo.crop(tup))
back1.create_image(0, 8, anchor=tk.NW, image = op1logo)

# Place "OP2" top mid
tup = (0, frameH, logwidth, frameH * 2)
op2logo = ImageTk.PhotoImage(rawlogo.crop(tup))
back2.create_image(0, 8, anchor=tk.NW, image = op2logo)

# Place "OP3" bot left
tup = (0, frameH * 2, logwidth, frameH * 3)
op3logo = ImageTk.PhotoImage(rawlogo.crop(tup))
back3.create_image(0, 8, anchor=tk.NW, image = op3logo)

# Place "OP4" bot mid
tup = (0, frameH * 3, logwidth, frameH * 4)
op4logo = ImageTk.PhotoImage(rawlogo.crop(tup))
back4.create_image(0, 8, anchor=tk.NW, image = op4logo)


adsrs = {}
# The five grey ADSR canvases
adsrs["OP1:"] = Adsr("OP1:", 210, 240)
adsrs["OP2:"] = Adsr("OP2:", 890, 240)
adsrs["OP3:"] = Adsr("OP3:", 210, 680)
adsrs["OP4:"] = Adsr("OP4:", 890, 680)
adsrs["Pitch:"] = Adsr("Pitch:", 1410, 270)

XOFF = 690
YOFF = 440

# There are only so many different types of control and each has an animated PNG
anims = {
    "0to127" :  [ "ctrl_0_127.png", 128 ],
    "_63to64" : [ "ctrl_-63.0_64.0.png", 128 ],
    "on_off" :  [ "ctrl_on_off.png", 2 ],
    "line_exp" :[ "ctrl_line_exp.png", 2 ],
    "_18to18" : [ "ctrl_-18_18.png", 37 ],
    "slideH" :  [ "ctrl_slide_H.png", 128],
    "slideV" :  [ "ctrl_slide_V.png", 128],
    "_63to63" : [ "ctrl_-63_63.png", 127 ],
    "C1toC7" :  [ "ctrl_C1_C7.png", 7 ],
    "chars" :   [ "lcd_chars.png", 36 ]
}

# Given the above list open each PNG in turn and break them into N separate anim frames
ctrlimgs = {}
for anim in anims:
    fname = anims[anim][0]
    numFrame = anims[anim][1]
    img = Image.open(fname)
    width = img.size[0]
    # followin is total height so if 7 frame anim and each frame is 32px high this is 224 e.g.
    height = img.size[1]
    # while this is the height of each frame (so 32 in this example)
    frameH = int(height / numFrame)
    # record everything about the multi-frames complete with empty list of frames
    ctrlimgs.update({ anim : { "type" : anim, "numframes" : numFrame, "width" : width, "height" : height, "frameH" : frameH, "frames" : []}})
    for n in range(numFrame):
        tup = (0, frameH * n, width, frameH * (n + 1))
        frame = ImageTk.PhotoImage(img.crop(tup))
        # having cropped each frame from PNG store it separatelt in "frames" list
        ctrlimgs[anim]["frames"].append(frame)

# following is list of all anumated controls - a key name, a label, an anim to use and X/Y
controls = {
    "OP1:Output" :   [ "Output",    "0to127",    100, 10 ],
    "OP1:Feedback" : [ "Feedback",  "_63to64",   10, 100 ],
    "OP1:LCurve" :   [ "L Curve",   "line_exp",  210, 10 ],
    "OP1:RCurve" :   [ "R Curve",   "line_exp",  280, 10 ],
    "OP1:PitchEnv" : [ "Pitch Env",  "on_off",    350, 10 ],
    "OP1:Fixed" :    [ "Fixed",     "on_off",    420, 10 ],
    "OP1:OP2In" :    [ "OP2 Input", "0to127",    100, 100 ],
    "OP1:OP3In" :    [ "OP3 Input", "0to127",    10, 190 ],
    "OP1:OP4In" :    [ "OP4 Input", "0to127",    100, 190 ],
    "OP1:Level" :    [ "Level",     "0to127",    10, 280 ],
    "OP1:VelSens" :  [ "Velo Sens", "0to127",    100, 280 ],
    "OP1:ATime" :    [ "A Time",    "slideH",    10, 380 ],
    "OP1:DTime" :    [ "D Time",    "slideH",    180, 380 ],
    "OP1:STime" :    [ "S Time",    "slideH",    350, 380 ],
    "OP1:RTime" :    [ "R Time",    "slideH",    520, 380 ],
    "OP1:ALevel" :   [ "A Level",   "slideV",    210, 60 ],
    "OP1:DLevel" :   [ "D Level",   "slideV",    280, 60 ],
    "OP1:SLevel" :   [ "S Level",   "slideV",    350, 60 ],
    "OP1:RLevel" :   [ "R Level",   "slideV",    420, 60 ],
    "OP1:Ratio" :    [ "Ratio",     "0to127",    500, 10 ],#not 0to127 !
    "OP1:Detune" :   [ "Detune",    "_63to63",   590, 10 ],
    "OP1:Time" :     [ "TimeScale", "0to127",    500, 100 ],
    "OP1:UpCurve" :  [ "Up Curve",  "_18to18",   590, 100 ],
    "OP1:Scale" :    [ "Scale Pos", "C1toC7",    500, 190 ],
    "OP1:DnCurve" :  [ "Down Curve","_18to18",   590, 190 ],
    "OP1:LGain" :    [ "L Gain",    "_63to63",   500, 280 ],
    "OP1:RGain" :    [ "R Gain",    "_63to63",   590, 280 ],

    "OP2:Output" :   [ "Output",    "0to127",    XOFF + 100, 10 ],
    "OP2:Feedback" : [ "Feedback",  "_63to64",   XOFF + 10, 100 ],
    "OP2:LCurve" :   [ "L Curve",   "line_exp",  XOFF + 210, 10 ],
    "OP2:RCurve" :   [ "R Curve",   "line_exp",  XOFF + 280, 10 ],
    "OP2:PitchEnv" : [ "Pitch Env",  "on_off",    XOFF + 350, 10 ],
    "OP2:Fixed" :    [ "Fixed",     "on_off",    XOFF + 420, 10 ],
    "OP2:OP1In" :    [ "OP1 Input", "0to127",    XOFF + 100, 100 ],
    "OP2:OP3In" :    [ "OP3 Input", "0to127",    XOFF + 10, 190 ],
    "OP2:OP4In" :    [ "OP4 Input", "0to127",    XOFF + 100, 190 ],
    "OP2:Level" :    [ "Level",     "0to127",    XOFF + 10, 280 ],
    "OP2:VelSens" :  [ "Velo Sens", "0to127",    XOFF + 100, 280 ],
    "OP2:ATime" :    [ "A Time",    "slideH",    XOFF + 10, 380 ],
    "OP2:DTime" :    [ "D Time",    "slideH",    XOFF + 180, 380 ],
    "OP2:STime" :    [ "S Time",    "slideH",    XOFF + 350, 380 ],
    "OP2:RTime" :    [ "R Time",    "slideH",    XOFF + 520, 380 ],
    "OP2:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, 60 ],
    "OP2:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, 60 ],
    "OP2:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, 60 ],
    "OP2:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, 60 ],
    "OP2:Ratio" :    [ "Ratio",     "0to127",    XOFF + 500, 10 ],
    "OP2:Detune" :   [ "Detune",    "_63to63",   XOFF + 590, 10 ],
    "OP2:Time" :     [ "TimeScale", "0to127",    XOFF + 500, 100 ],
    "OP2:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + 590, 100 ],
    "OP2:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + 500, 190 ],
    "OP2:DnCurve" :  [ "Down Curve","_18to18",   XOFF + 590, 190 ],
    "OP2:LGain" :    [ "L Gain",    "_63to63",   XOFF + 500, 280 ],
    "OP2:RGain" :    [ "R Gain",    "_63to63",   XOFF + 590, 280 ],

    "OP3:Output" :   [ "Output",    "0to127",    100, YOFF + 10 ],
    "OP3:Feedback" : [ "Feedback",  "_63to64",   10, YOFF + 100 ],
    "OP3:LCurve" :   [ "L Curve",   "line_exp",  210, YOFF + 10 ],
    "OP3:RCurve" :   [ "R Curve",   "line_exp",  280, YOFF + 10 ],
    "OP3:PitchEnv" : [ "Pitch Env",  "on_off",    350, YOFF + 10 ],
    "OP3:Fixed" :    [ "Fixed",     "on_off",    420, YOFF + 10 ],
    "OP3:OP1In" :    [ "OP1 Input", "0to127",    100, YOFF + 100 ],
    "OP3:OP2In" :    [ "OP2 Input", "0to127",    10, YOFF + 190 ],
    "OP3:OP4In" :    [ "OP4 Input", "0to127",    100, YOFF + 190 ],
    "OP3:Level" :    [ "Level",     "0to127",    10, YOFF + 280 ],
    "OP3:VelSens" :  [ "Velo Sens", "0to127",    100, YOFF + 280 ],
    "OP3:ATime" :    [ "A Time",    "slideH",    10, YOFF + 380 ],
    "OP3:DTime" :    [ "D Time",    "slideH",    180, YOFF + 380 ],
    "OP3:STime" :    [ "S Time",    "slideH",    350, YOFF + 380 ],
    "OP3:RTime" :    [ "R Time",    "slideH",    520, YOFF + 380 ],
    "OP3:ALevel" :   [ "A Level",   "slideV",    210, YOFF + 60 ],
    "OP3:DLevel" :   [ "D Level",   "slideV",    280, YOFF + 60 ],
    "OP3:SLevel" :   [ "S Level",   "slideV",    350, YOFF + 60 ],
    "OP3:RLevel" :   [ "R Level",   "slideV",    420, YOFF + 60 ],
    "OP3:Ratio" :    [ "Ratio",     "0to127",    500, YOFF + 10 ],
    "OP3:Detune" :   [ "Detune",    "_63to63",   590, YOFF + 10 ],
    "OP3:Time" :     [ "TimeScale", "0to127",    500, YOFF + 100 ],
    "OP3:UpCurve" :  [ "Up Curve",  "_18to18",   590, YOFF + 100 ],
    "OP3:Scale" :    [ "Scale Pos", "C1toC7",    500, YOFF + 190 ],
    "OP3:DnCurve" :  [ "Down Curve","_18to18",   590, YOFF + 190 ],
    "OP3:LGain" :    [ "L Gain",    "_63to63",   500, YOFF + 280 ],
    "OP3:RGain" :    [ "R Gain",    "_63to63",   590, YOFF + 280 ],

    "OP4:Output" :   [ "Output",    "0to127",    XOFF + 100, YOFF + 10 ],
    "OP4:Feedback" : [ "Feedback",  "_63to64",   XOFF + 10, YOFF + 100 ],
    "OP4:LCurve" :   [ "L Curve",   "line_exp",  XOFF + 210, YOFF + 10 ],
    "OP4:RCurve" :   [ "R Curve",   "line_exp",  XOFF + 280, YOFF + 10 ],
    "OP4:PitchEnv" : [ "Pitch Env",  "on_off",    XOFF + 350, YOFF + 10 ],
    "OP4:Fixed" :    [ "Fixed",     "on_off",    XOFF + 420, YOFF + 10 ],
    "OP4:OP1In" :    [ "OP1 Input", "0to127",    XOFF + 100, YOFF + 100 ],
    "OP4:OP2In" :    [ "OP2 Input", "0to127",    XOFF + 10, YOFF + 190 ],
    "OP4:OP3In" :    [ "OP3 Input", "0to127",    XOFF + 100, YOFF + 190 ],
    "OP4:Level" :    [ "Level",     "0to127",    XOFF + 10, YOFF + 280 ],
    "OP4:VelSens" :  [ "Velo Sens", "0to127",    XOFF + 100, YOFF + 280 ],
    "OP4:ATime" :    [ "A Time",    "slideH",    XOFF + 10, YOFF + 380 ],
    "OP4:DTime" :    [ "D Time",    "slideH",    XOFF + 180, YOFF + 380 ],
    "OP4:STime" :    [ "S Time",    "slideH",    XOFF + 350, YOFF + 380 ],
    "OP4:RTime" :    [ "R Time",    "slideH",    XOFF + 520, YOFF + 380 ],
    "OP4:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, YOFF + 60 ],
    "OP4:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, YOFF + 60 ],
    "OP4:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, YOFF + 60 ],
    "OP4:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, YOFF + 60 ],
    "OP4:Ratio" :    [ "Ratio",     "0to127",    XOFF + 500, YOFF + 10 ],
    "OP4:Detune" :   [ "Detune",    "_63to63",   XOFF + 590, YOFF + 10 ],
    "OP4:Time" :     [ "TimeScale", "0to127",    XOFF + 500, YOFF + 100 ],
    "OP4:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + 590, YOFF + 100 ],
    "OP4:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + 500, YOFF + 190 ],
    "OP4:DnCurve" :  [ "Down Curve","_18to18",   XOFF + 590, YOFF + 190 ],
    "OP4:LGain" :    [ "L Gain",    "_63to63",   XOFF + 500, YOFF + 280 ],
    "OP4:RGain" :    [ "R Gain",    "_63to63",   XOFF + 590, YOFF + 280 ],


    "Name:chr0" :    [ "",          "chars",   1430, 10 ],
    "Name:chr1" :    [ "",          "chars",   1430 + 64 - 11, 10 ],
    "Name:chr2" :    [ "",          "chars",   1430 + ((64 - 11) * 2), 10 ],
    "Name:chr3":     [ "",          "chars",   1430 + ((64 - 11) * 3), 10 ],
    "Pitch:ATime" :  [ "A Time",    "slideH",    1410, 410 ],
    "Pitch:DTime" :  [ "D Time",    "slideH",    1410, 460 ],
    "Pitch:STime" :  [ "S Time",    "slideH",    1410, 510 ],
    "Pitch:RTime" :  [ "R Time",    "slideH",    1410, 560 ],
    "Pitch:ALevel" : [ "A Level",   "slideV",    1410, 90 ],
    "Pitch:DLevel" : [ "D Level",   "slideV",    1480, 90 ],
    "Pitch:SLevel" : [ "S Level",   "slideV",    1550, 90 ],
    "Pitch:RLevel" : [ "R Level",   "slideV",    1620, 90 ],
    "Mixer:Level" :  [ "Mixer Level","_63to63",   1600, 500 ],
}

# For all the above controls simply create their anm objects but don't draw until inits set
controllist = {}
for key in controls:
    thisanim = Anim(key, controls[key][0], controls[key][1], controls[key][2], controls[key][3])
    controllist.update({key : [thisanim]})

def loadJSON(event):
    with open("mypatch.json") as f:
        data = json.load(f)

        for i in data:
            print("=====", i, "=====")
            if (i != "Name"):
                for j in data[i]:
                    key = f'{i}:{j}'
                    print(f'{key} = ', data[i][j])
                    controllist[key][0].setIndex(data[i][j])
                    controllist[key][0].draw()
            else:
                for n in range(4):
                    key = f'{i}:chr{n}'
                    print(f'{key} = ', data[i][n])
                    controllist[key][0].setIndex(ord(data[i][n]))
                    controllist[key][0].draw()
            for j in ['OP1:', 'OP2:', 'OP3:', 'OP4:', 'Pitch:']:
                adsrs[j].draw()

load = Canvas(width=32, height=32, highlightthickness=0)
load.place(x=1650, y=450)
load.create_rectangle(0,0, 31, 31, fill='#C00000')
load.create_text(0, 0, anchor=tk.NW, text="JSON\ntest", fill='#FFFFFF')
load.bind('<Button>', loadJSON)


# set all the non-0 init values into controls as if an "init" patch
controllist["OP1:ALevel"][0].setIndex(127)
controllist["OP1:DLevel"][0].setIndex(127)
controllist["OP1:SLevel"][0].setIndex(127)
adsrs["OP1:"].init()
controllist["OP2:ALevel"][0].setIndex(127)
controllist["OP2:DLevel"][0].setIndex(127)
controllist["OP2:SLevel"][0].setIndex(127)
adsrs["OP2:"].init()
controllist["OP3:ALevel"][0].setIndex(127)
controllist["OP3:DLevel"][0].setIndex(127)
controllist["OP3:SLevel"][0].setIndex(127)
adsrs["OP3:"].init()
controllist["OP4:ALevel"][0].setIndex(127)
controllist["OP4:DLevel"][0].setIndex(127)
controllist["OP4:SLevel"][0].setIndex(127)
adsrs["OP4:"].init()
controllist["Pitch:ALevel"][0].setIndex(127)
controllist["Pitch:DLevel"][0].setIndex(127)
controllist["Pitch:SLevel"][0].setIndex(127)
adsrs["Pitch:"].init()
controllist["OP1:Output"][0].setIndex(127)
controllist["OP1:Level"][0].setIndex(63)
controllist["OP2:Level"][0].setIndex(63)
controllist["OP3:Level"][0].setIndex(63)
controllist["OP4:Level"][0].setIndex(63)
controllist["OP1:Feedback"][0].setIndex(63)
controllist["OP2:Feedback"][0].setIndex(63)
controllist["OP3:Feedback"][0].setIndex(63)
controllist["OP4:Feedback"][0].setIndex(63)
controllist["OP1:Ratio"][0].setIndex(1)
controllist["OP2:Ratio"][0].setIndex(1)
controllist["OP3:Ratio"][0].setIndex(1)
controllist["OP4:Ratio"][0].setIndex(1)
controllist["Mixer:Level"][0].setIndex(63)
controllist["OP1:Detune"][0].setIndex(63)
controllist["OP2:Detune"][0].setIndex(63)
controllist["OP3:Detune"][0].setIndex(63)
controllist["OP4:Detune"][0].setIndex(63)
controllist["OP1:UpCurve"][0].setIndex(18)
controllist["OP2:UpCurve"][0].setIndex(18)
controllist["OP3:UpCurve"][0].setIndex(18)
controllist["OP4:UpCurve"][0].setIndex(18)
controllist["OP1:DnCurve"][0].setIndex(18)
controllist["OP2:DnCurve"][0].setIndex(18)
controllist["OP3:DnCurve"][0].setIndex(18)
controllist["OP4:DnCurve"][0].setIndex(18)
controllist["OP1:Scale"][0].setIndex(3)
controllist["OP2:Scale"][0].setIndex(3)
controllist["OP3:Scale"][0].setIndex(3)
controllist["OP4:Scale"][0].setIndex(3)
controllist["Name:chr0"][0].setIndex(18)  #'I'
controllist["Name:chr1"][0].setIndex(23)  #'N'
controllist["Name:chr2"][0].setIndex(18)  #'I'
controllist["Name:chr3"][0].setIndex(29)  #'T'
controllist["OP1:LGain"][0].setIndex(63)
controllist["OP2:LGain"][0].setIndex(63)
controllist["OP3:LGain"][0].setIndex(63)
controllist["OP4:LGain"][0].setIndex(63)
controllist["OP1:RGain"][0].setIndex(63)
controllist["OP2:RGain"][0].setIndex(63)
controllist["OP3:RGain"][0].setIndex(63)
controllist["OP4:RGain"][0].setIndex(63)

# Now init values are set run throught the list and draw all animated controls
for entry in controllist:
    controllist[entry][0].draw()

window.mainloop()
