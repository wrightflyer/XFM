import tkinter as tk
from tkinter import *
from PIL import Image, ImageTk
import json
import mido
import json

class Adsr:
    def __init__(self, key, xpos, ypos):
        self.key = key
        self.xpos = xpos
        self.ypos = ypos
        self.canvas = Canvas(window, width=256, height=128, bg='#707070')
        self.canvas.create_image(0, 0, anchor=tk.NW, image = ctrlimgs["litegrey"]["frames"][0], tag = "adsrback")
        self.canvas.place(x = xpos, y = ypos)
    
    def update(self, at, al, dt, dl, st, sl, rt, rl):
        # horizontally 128+128+128+128 is 512 but the window is only 256 wide
        # so start by halving all the horizontal values (but just for display)
        at = at / 2
        dt = dt / 2
        st = st / 2
        rt = rt / 2
        self.canvas.delete("adsrline")
        ax = at
        ay = 128 - al

        dx = dt + ax
        dy = 128 - dl

        sx = st + dx
        sy = 128 - sl

        rx = rt + sx
        ry = 128 - rl

        padding = 256 - (at + dt + st + rt)

        ystart = 128 # as Y coordinates start at top left this is bottom left pixel
        if self.key == "Pitch:":
            # pitch curve is -48..+48 bi-polar so start at mid height
            ystart = 64
        #print("start=(", 0, ystart, ") end= (", ax, ay, ")")
        self.canvas.create_line(0, ystart, ax, ay, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(ax, ay, dx, dy, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(dx, dy, sx, sy, width=3, fill='#000CFF', tag="adsrline")
        self.canvas.create_line(sx, sy, sx + padding, sy, width=3, dash=(3,1), fill='#000CFF', tag="adsrline")
        self.canvas.create_line(sx + padding, sy, 256, ry, width=3, fill='#000CFF', tag="adsrline")

    def init(self):
        self.update(0, 127, 0, 127, 0, 127, 0, 0)

    def draw(self):
        op = self.key
        key = op + "ATime"
        at = controllist[key][0].getValue()
        key = op + "DTime"
        dt = controllist[key][0].getValue()
        key = op + "STime"
        st = controllist[key][0].getValue()
        key = op + "RTime"
        rt = controllist[key][0].getValue()

        offset = 0
        if op == "Pitch:":
            offset = 64
        key = op + "ALevel"
        al = controllist[key][0].getValue() + offset
        key = op + "DLevel"
        dl = controllist[key][0].getValue() + offset
        key = op + "SLevel"
        sl = controllist[key][0].getValue() + offset
        key = op + "RLevel"
        rl = controllist[key][0].getValue() + offset
        #print("draw ADSR ", op, "with ",at, al, dt, dl, st, sl, rt, rl)
        self.update(at, al, dt, dl, st, sl, rt, rl)

class Anim:
    def __init__(self, keyname, title, ctrl, xpos, ypos, offset = 0):
        self.keyname = keyname
        self.ctrl = ctrl
        self.index = 0
        self.fraction = 0
        self.xpos = xpos
        self.ypos = ypos
        self.offset = offset # difference between 0 frame and lowest value (maybe -63 or -48 etc)
        self.width = ctrlimgs[ctrl]["width"]
        self.height = ctrlimgs[ctrl]["height"]
        numFrames = ctrlimgs[ctrl]["numframes"]
        self.frameHeight = ctrlimgs[ctrl]["frameH"]
        self.numFrames = numFrames
        self.canvas = Canvas(window, width = self.width, height = self.frameHeight + 10, bg='#202020', highlightthickness=0)
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
            self.index = n

    def getIndex(self):
        return self.index

    def getValue(self):
        return self.index + self.offset # likely negative so really a subtraction

    def setValue(self, n):
        n = n - self.offset
        self.setIndex(n)

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

    def make_inbounds(self):
        ctrl = self.keyname.split(':')[1]
        if ctrl == "Feedback":
            value = self.getValue() * 10
            if value > 0:
                value = value + self.fraction
            else:
                value = value - self.fraction
            if value < -630:
                self.index = 0 # that is -63
                self.fraction = 0
            if value > 640:
                self.fraction = 0
        if ctrl == "Ratio":
            value = self.getValue() * 100
            value = value + self.fraction
            if value < 50: # can't go lower than 0.50
                self.fraction = 50;
            if value > 3200: # can't go above 32.00
                self.fraction = 0
        if ctrl == "Freq":
            value = self.getValue() * 100
            value = value + self.fraction
            if value > 9755:
                self.fraction = 55
            if value == 0:
                self.fraction = 1

    def draw(self):
        op = self.keyname.split(':')[0]
        ctrl = self.keyname.split(':')[1]
        self.make_inbounds()
        self.canvas.delete(self.keyname)
        self.canvas.delete("digits")
        if ctrl[:3] != "chr":
            self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)
        else:
            # for the characters in name special handling because index>100 means char + dot overlay
            if self.index < 100:
                self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)
            else:
                self.canvas.create_image(0, 11, anchor=tk.NW, image = ctrlimgs[self.ctrl]["frames"][self.index - 100], tag=self.keyname)
                self.canvas.create_image(47, 60, anchor=tk.NW, image = ctrlimgs["dot"]["frames"][0], tag=self.keyname)
        if ctrl == "Fixed":
            ctrl_w = controllist[op + ":Freq"][0].width
            ctrl_h = controllist[op + ":Freq"][0].frameHeight + 10 # +10 for the label above
            if self.index == 0:
                controllist[op + ":Freq"][0].canvas.config(width=0, height=0)
                controllist[op + ":Ratio"][0].canvas.config(width = ctrl_w, height = ctrl_h)
            else:
                controllist[op + ":Freq"][0].canvas.config(width = ctrl_w, height = ctrl_h)
                controllist[op + ":Ratio"][0].canvas.config(width=0, height=0)

        # following to handle "big knobs" that need their digits drawn separately...
        if ctrl == "Feedback":
            if self.getValue() < 0:
                # a leading negative sign
                self.canvas.create_image(1, 80, anchor=tk.NW, image = ctrlimgs["neg"]["frames"][0], tag = "digits")
            self.canvas.create_image(18, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][abs(self.getValue())], tag = "digits")
            self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["dig_d_9"]["frames"][self.fraction], tag = "digits")
        if ctrl == "Freq":
            # no leading 0 if only fraction
            if self.getValue() != 0:
                if self.getValue() < 10:
                    self.canvas.create_image(20, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
                else:
                    self.canvas.create_image(16, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
                self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["digits0"]["frames"][self.fraction], tag = "digits")
            else:
                self.canvas.create_image(38, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.fraction], tag = "digits")
        if ctrl == "Ratio":
            self.canvas.create_image(17, 80, anchor=tk.NW, image = ctrlimgs["digits"]["frames"][self.getValue()], tag = "digits")
            self.canvas.create_image(39, 80, anchor=tk.NW, image = ctrlimgs["dig_d_99"]["frames"][self.fraction], tag = "digits")

    def motion(self, event):
        newFrame = False
        ctrl = self.keyname.split(':')[1]

        if event.y < self.prevy:
            self.inc()
            newFrame = True

        if event.y > self.prevy:
            self.dec()
            newFrame = True

        if event.x > self.prevx:
            if ctrl == "Feedback":
                if self.fraction < 9:
                    self.fraction = self.fraction + 1
                    newFrame = True
            elif ctrl == "Freq" or ctrl == "Ratio":
                if self.fraction < 99:
                    self.fraction = self.fraction + 1
                    newFrame = True
            elif ctrl == "Ratio":
                if self.fraction < 99:
                    self.fraction = self.fraction + 1
                    newFrame = True
            else:
                self.inc()
                newFrame = True

        if event.x < self.prevx:
            if ctrl == "Feedback" or ctrl == "Freq" or ctrl == "Ratio":
                if self.fraction > 0:
                    self.fraction = self.fraction - 1
                    newFrame = True
            else:
                self.dec()
                newFrame = True

        if newFrame == True:
            self.draw()
            routeWin.draw()
            # if a control just moved that would change ADSR then redraw the ADSR graph
            ctrlType = ctrlimgs[self.ctrl]["type"]
            if ctrlType == "slideV" or ctrlType == "slideH" or ctrlType == "slideVbi":
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


class Backdrop:
    def __init__(self, id, xpos, ypos, width, height, img, logo, xlog, ylog):
        self.id = id
        self.width = width
        self.height = height
        self.xpos = xpos
        self.ypos = ypos
        self.canvas = Canvas(width = width, height = height, bg='#202020', highlightbackground = '#404040')
        self.canvas.place(x = xpos, y = ypos)
        self.canvas.create_image(0, 0, anchor=tk.NW, image = img)
        self.canvas.create_image(xlog, ylog, anchor=tk.NW, image = logo)

class RouteWindow:
    def __init__(self):
        self.routeWin = Toplevel(window)
        self.routeWin.geometry("940x670")
        self.routeWin.title("Operator signal routing                       (close using Hide button not X)")
        self.routeWin.resizable(False, False)
        self.routeWin.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.canvas = Canvas(self.routeWin, width = 940, height = 670, bg='#313131')
        self.canvas.place(x = 0, y = 0)
        self.showNums = True
        self.canvas.bind('<Button>', self.toggleNums)
        self.hide()

    def show(self):
        self.routeWin.deiconify()
        self.Showing = True
        self.draw()

    def hide(self):
        self.routeWin.withdraw()
        self.Showing = False

    def toggleNums(self, event):
        if self.showNums == True:
            self.showNums = False
        else:
            self.showNums = True
        self.draw()
    
    def disable_event(self):
        pass

    def getStipple(self, key):
        val = abs(controllist[key][0].getValue())
        name = "@./stipple/stip"
        # there are 0..255 stipple files but values are only 0..63 or 0..127 so need *2 or *4
        mult = 2
        if "Feedback" in key:
            mult = 4
        name = name + str(val * mult) + ".xbm"
        # feedback can be +64 and *4 that is 256 but stipples are 0 .. 255 so...
        if name == "@./stipple/stip256.xbm":
            name = "@./stipple/stip255.xbm"
        return name
        
    def getDigits(self, key):
        if "Feedback" in key:
            fb = controllist[key][0].getValue() * 10
            if fb < 0.0:
                fb = fb - controllist[key][0].fraction
            else:
                fb = fb + controllist[key][0].fraction
            fb = fb / 10
            val = "{:03.1f}".format(fb)
        else:
            val = "{:03d}".format(controllist[key][0].getValue())
        if val == "000" or val == "0.0":
            val = ""
        if not self.showNums:
            val = ""
        return val

    def getWave(self, fbk):
        if fbk < -32.0:
            return waveSquareImage
        elif fbk >= -32.0 and fbk < 32.0:
            return waveSineImage
        elif fbk >= 32.0 and fbk < 63.0:
            return waveSawImage
        else:
            return waveNoiseImage

    def draw(self):
        if not self.Showing:
            return
        self.canvas.delete("route") # delete everything already on the canvas (if any)
        OP_W = 280
        OP_H = 180
        OP1_LOCX1 = 80
        OP1_LOCY1 = 90
        OP1_LOCX2 = OP1_LOCX1 + OP_W
        OP1_LOCY2 = OP1_LOCY1 + OP_H

        OP2_LOCX1 = 450
        OP2_LOCY1 = 90
        OP2_LOCX2 = OP2_LOCX1 + OP_W
        OP2_LOCY2 = OP2_LOCY1 + OP_H

        OP3_LOCX1 = 80
        OP3_LOCY1 = 390
        OP3_LOCX2 = OP3_LOCX1 + OP_W
        OP3_LOCY2 = OP3_LOCY1 + OP_H

        OP4_LOCX1 = 450
        OP4_LOCY1 = 390
        OP4_LOCX2 = OP4_LOCX1 + OP_W
        OP4_LOCY2 = OP4_LOCY1 + OP_H

        # four coloured OP rectangles
        self.canvas.create_rectangle(OP1_LOCX1, OP1_LOCY1, OP1_LOCX2, OP1_LOCY2, fill='#FF1818', tag="route")
        self.canvas.create_rectangle(OP2_LOCX1, OP2_LOCY1, OP2_LOCX2, OP2_LOCY2, fill='#00FF00', tag="route")
        self.canvas.create_rectangle(OP3_LOCX1, OP3_LOCY1, OP3_LOCX2, OP3_LOCY2, fill='#2828FF', tag="route")
        self.canvas.create_rectangle(OP4_LOCX1, OP4_LOCY1, OP4_LOCX2, OP4_LOCY2, fill='#FFFF00', tag="route")

        # labels for the rectangles
        self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 40, anchor=tk.NW, text="OP1", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 40, anchor=tk.NW, text="OP2", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 40, anchor=tk.NW, text="OP3", fill='#000000', font=('Helvetica','48','bold'), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 40, anchor=tk.NW, text="OP4", fill='#000000', font=('Helvetica','48','bold'), tag="route")

        self.canvas.create_text(280, 640, anchor=tk.NW, text="Click anywhere to show/hide values", fill='#FFFFFF', font=('Helvetica','18'), tag="route")

        if controllist["OP1:Fixed"][0].getValue():
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP1:Freq"][0].getValue() * 100 + controllist["OP1:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP1:Ratio"][0].getValue() * 100 + controllist["OP1:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP1:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP1_LOCX1 + 70, OP1_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP1:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")
        
        if controllist["OP2:Fixed"][0].getValue():
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP2:Freq"][0].getValue() * 100 + controllist["OP2:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP2:Ratio"][0].getValue() * 100 + controllist["OP2:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP2:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP2_LOCX1 + 70, OP2_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP2:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")

        if controllist["OP3:Fixed"][0].getValue():
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP3:Freq"][0].getValue() * 100 + controllist["OP3:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP3:Ratio"][0].getValue() * 100 + controllist["OP3:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP3:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP3_LOCX1 + 70, OP3_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP3:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")

        if controllist["OP4:Fixed"][0].getValue():
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 105, anchor=tk.NW, text="Freq: " + str(controllist["OP4:Freq"][0].getValue() * 100 + controllist["OP4:Freq"][0].fraction) + " Hz", fill='#000000', font=('Helvetica','18'), tag="route")
        else:
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 105, anchor=tk.NW, text="Ratio: x" + str((controllist["OP4:Ratio"][0].getValue() * 100 + controllist["OP4:Ratio"][0].fraction) / 100), fill='#000000', font=('Helvetica','18'), tag="route")
        if controllist["OP4:Detune"][0].getValue() != 0:
            self.canvas.create_text(OP4_LOCX1 + 70, OP4_LOCY1 + 130, anchor=tk.NW, text="Detune: " + str(controllist["OP4:Detune"][0].getValue()), fill='#000000', font=('Helvetica','18'), tag="route")


        # the OP1 to OP2 route (horiz, red)
        self.canvas.create_line(OP1_LOCX2, OP1_LOCY1 + 20, OP2_LOCX1, OP1_LOCY1 + 20, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP2:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX2 - 50, OP1_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP1 route (horiz, green)
        self.canvas.create_line(OP1_LOCX2, OP1_LOCY1 + 50, OP2_LOCX1, OP1_LOCY1 + 50, fill='#00FF00', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP2In"), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 5, OP1_LOCY1 + 50, anchor=tk.W, text=self.getDigits("OP1:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP4 route (horiz, bllue)
        self.canvas.create_line(OP3_LOCX2, OP3_LOCY2 - 20, OP4_LOCX1, OP3_LOCY2 - 20, fill='#2828FF', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX2 - 50, OP3_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 to OP3 route (horiz, yellow)
        self.canvas.create_line(OP3_LOCX2, OP3_LOCY2 - 50, OP4_LOCX1, OP3_LOCY2 - 50, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP3:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 5, OP3_LOCY2 - 50, anchor=tk.W, text=self.getDigits("OP3:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP1 to OP3 route (vert, red)
        self.canvas.create_line(OP1_LOCX1 + 20, OP1_LOCY2, OP1_LOCX1 + 20, OP3_LOCY1, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP3:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX1 + 5, OP1_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP3:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP1 route (vert, blue)
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY2, OP1_LOCX1 + 50, OP3_LOCY1, fill='#2828FF', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX1 + 30, OP3_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP1:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP4 route (vert, green)
        self.canvas.create_line(OP4_LOCX2 - 20, OP2_LOCY2, OP4_LOCX2 - 20, OP4_LOCY1, fill='#00FF00', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP2In"), tag="route")
        self.canvas.create_text(OP4_LOCX2 - 40, OP2_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 ot OP2 route (vert, yellow)
        self.canvas.create_line(OP4_LOCX2 - 50, OP2_LOCY2, OP4_LOCX2 - 50, OP4_LOCY1, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP2:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX2 - 70, OP4_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP1 to OP4 route (diag, red)
        self.canvas.create_line(OP1_LOCX2 - 8, OP1_LOCY2 - 30, OP4_LOCX1 + 30, OP4_LOCY1, fill='#FF1818', arrow=LAST, width=16, stipple=self.getStipple("OP4:OP1In"), tag="route")
        self.canvas.create_text(OP1_LOCX2 - 50, OP1_LOCY2 - 30, anchor=tk.W, text=self.getDigits("OP4:OP1In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP4 to OP1 route (diag, yellow)
        self.canvas.create_line(OP1_LOCX2 - 30, OP1_LOCY2, OP4_LOCX1 + 8, OP4_LOCY1 + 30, fill='#FFFF00', arrow=FIRST, width=16, stipple=self.getStipple("OP1:OP4In"), tag="route")
        self.canvas.create_text(OP4_LOCX1 + 8 , OP4_LOCY1 + 30, anchor=tk.W, text=self.getDigits("OP1:OP4In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP3 to OP2 route (diag, blue)
        self.canvas.create_line(OP3_LOCX2 - 8, OP3_LOCY1 + 30, OP2_LOCX1 + 30, OP2_LOCY2, fill='#2828FF', arrow=LAST, width=16, stipple=self.getStipple("OP2:OP3In"), tag="route")
        self.canvas.create_text(OP3_LOCX2 - 50 , OP3_LOCY1 + 30, anchor=tk.W, text=self.getDigits("OP2:OP3In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        # the OP2 to OP3 route (diag, green)
        self.canvas.create_line(OP3_LOCX2 - 30, OP3_LOCY1, OP2_LOCX1 + 8, OP2_LOCY2 - 30, fill='#00FF00', arrow=FIRST, width=16, stipple=self.getStipple("OP3:OP2In"), tag="route")
        self.canvas.create_text(OP2_LOCX1 + 8 , OP2_LOCY2 - 30, anchor=tk.W, text=self.getDigits("OP3:OP2In"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
      
        # the "OUTPUT" text label
        self.canvas.create_text(OP2_LOCX2 + 20, OP2_LOCY2 + 40, anchor=tk.NW, text="OUTPUT", fill='#FFFFFF', font=('Helvetica','30','bold'), tag="route")

        # the OP1 route to OUTPUT (red)
        stip = self.getStipple("OP1:Output")
        self.canvas.create_line(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1, OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 - 68, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 - 60, OP2_LOCX2 + 148, OP1_LOCY1 - 60, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 140, OP1_LOCY1 - 60, OP2_LOCX2 + 140, OP2_LOCY2 + 30, fill='#FF1818', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP1_LOCX1 + (OP_W / 2), OP1_LOCY1 + 20, anchor=tk.CENTER, text=self.getDigits("OP1:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP2 route to OUPUT (green)
        stip = self.getStipple("OP2:Output")
        self.canvas.create_line(OP2_LOCX2, OP2_LOCY1 + (OP_H / 2), OP2_LOCX2 + 58, OP2_LOCY1 + (OP_H / 2), fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 50, OP2_LOCY1 + (OP_H / 2), OP2_LOCX2 + 50, OP2_LOCY2 + 30, arrow=LAST, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP2_LOCX2 - 50, OP2_LOCY1 + (OP_H / 2), anchor=tk.W, text=self.getDigits("OP2:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP3 route to OUPUT (blue)
        stip = self.getStipple("OP3:Output")
        self.canvas.create_line(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2, OP1_LOCX1 + (OP_W / 2), OP3_LOCY2 + 68, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2 + 60, OP4_LOCX2 + 148, OP3_LOCY2 + 60, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 140, OP3_LOCY2 + 60, OP4_LOCX2 + 140, OP4_LOCY1 - 30, fill='#2828FF', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP3_LOCX1 + (OP_W / 2), OP3_LOCY2 - 20, anchor=tk.CENTER, text=self.getDigits("OP3:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP4 route to OUTPUT (yellow)
        stip = self.getStipple("OP4:Output")
        self.canvas.create_line(OP4_LOCX2, OP4_LOCY1 + (OP_H / 2), OP4_LOCX2 + 58, OP4_LOCY1 + (OP_H / 2), fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 50, OP4_LOCY1 + (OP_H / 2), OP4_LOCX2 + 50, OP4_LOCY1 - 30, arrow=LAST, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP4_LOCX2 - 50, OP4_LOCY1 + (OP_H / 2), anchor=tk.W, text=self.getDigits("OP4:Output"), fill='#000000', font=('Helvetica','18','bold'), tag="route")

        # the OP1 feedback loop (red)
        op1fbk = controllist["OP1:Feedback"][0].getValue()
        wave_file = self.getWave(op1fbk)
        stip = self.getStipple("OP1:Feedback")
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY1, OP1_LOCX1 + 50, OP1_LOCY1 - 38, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 + 50, OP1_LOCY1 - 30, OP1_LOCX1 - 38, OP1_LOCY1 - 30, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 - 30, OP1_LOCY1 - 30, OP1_LOCX1 - 30, OP1_LOCY1 + 30, fill='#FF1818', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP1_LOCX1 - 38, OP1_LOCY1 + 30, OP1_LOCX1, OP1_LOCY1 + 30, fill='#FF1818', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP1_LOCX1 + 30, OP1_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP1:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op1fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP1_LOCX1 + 30, OP1_LOCY1 + 40, anchor=tk.NW, image = wave_file, tag="route")

        # the OP2 feedback loop (green)
        op2fbk = controllist["OP2:Feedback"][0].getValue()
        wave_file = self.getWave(op2fbk)
        stip = self.getStipple("OP2:Feedback")
        self.canvas.create_line(OP2_LOCX2 - 50, OP2_LOCY1, OP2_LOCX2 - 50, OP2_LOCY1 - 38, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 - 50, OP2_LOCY1 - 30, OP2_LOCX2 + 38, OP2_LOCY1 - 30, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 30, OP2_LOCY1 - 30, OP2_LOCX2 + 30, OP2_LOCY1 + 30, fill='#00FF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP2_LOCX2 + 38, OP2_LOCY1 + 30, OP2_LOCX2, OP2_LOCY1 + 30, fill='#00FF00', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP2_LOCX2 - 70, OP2_LOCY1 + 20, anchor=tk.W, text=self.getDigits("OP2:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op2fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP2_LOCX2 - 70, OP2_LOCY1 + 40, anchor=tk.NW, image = wave_file, tag="route")

        # the OP3 feedback loop (blue)
        op3fbk = controllist["OP3:Feedback"][0].getValue()
        wave_file = self.getWave(op3fbk)
        stip = self.getStipple("OP3:Feedback")
        self.canvas.create_line(OP3_LOCX1 + 50, OP3_LOCY2, OP3_LOCX1 + 50, OP3_LOCY2 + 38, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 + 50, OP3_LOCY2 + 30, OP3_LOCX1 - 38, OP3_LOCY2 + 30, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 - 30, OP3_LOCY2 - 30, OP3_LOCX1 - 30, OP3_LOCY2 + 30, fill='#2828FF', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP3_LOCX1 - 38, OP3_LOCY2 - 30, OP3_LOCX1, OP3_LOCY2 - 30, fill='#2828FF', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP3_LOCX1 + 30, OP3_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP3:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op3fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP3_LOCX1 + 30, OP3_LOCY2 - 70, anchor=tk.NW, image = wave_file, tag="route")

        # the OP4 feedback loop (yellow)
        op4fbk = controllist["OP4:Feedback"][0].getValue()
        wave_file = self.getWave(op4fbk)
        stip = self.getStipple("OP4:Feedback")
        self.canvas.create_line(OP4_LOCX2 - 50, OP4_LOCY2, OP4_LOCX2 - 50, OP4_LOCY2 + 38, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 - 50, OP4_LOCY2 + 30, OP4_LOCX2 + 38, OP4_LOCY2 + 30, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 30, OP4_LOCY2 + 30, OP4_LOCX2 + 30, OP4_LOCY2 - 30, fill='#FFFF00', width=16, stipple=stip, tag="route")
        self.canvas.create_line(OP4_LOCX2 + 38, OP4_LOCY2 - 30, OP4_LOCX2, OP4_LOCY2 - 30, fill='#FFFF00', arrow=LAST, width=16, stipple=stip, tag="route")
        self.canvas.create_text(OP4_LOCX2 - 70, OP4_LOCY2 - 20, anchor=tk.W, text=self.getDigits("OP4:Feedback"), fill='#000000', font=('Helvetica','18','bold'), tag="route")
        if op4fbk != 0.0 and self.showNums:
            self.canvas.create_image(OP4_LOCX2 - 70, OP4_LOCY2 - 70, anchor=tk.NW, image = wave_file, tag="route")

class SetupWindow:
    def __init__(self):
        self.setupWin = Toplevel(window)
        self.setupWin.geometry("940x670")
        self.setupWin.title("Setup")
        self.setupWin.resizable(False, False)
        self.setupWin.protocol("WM_DELETE_WINDOW", self.disable_event)
        self.canvas = Canvas(self.setupWin, width = 940, height = 670, bg='#313131')
        self.canvas.place(x = 0, y = 0)
        self.listbox = Listbox(self.setupWin, width = 50)
        self.listbox.place(x = 20, y = 50)
        self.midiButton = Button(self.setupWin, text = "Open MIDI port")
        self.midiButton.place(x = 120, y = 230)
        self.midiButton.bind('<Button>', self.openMIDI)
        self.midiLabel = Label(self.setupWin, text="MIDI port: NOT SET", bg='#FFFFFF')
        self.midiLabel.place(x = 120, y = 20)
        self.dumpLabel = Label(self.setupWin, text = "Dump of received sysex (red = changed)", bg = '#FFFFFF')
        self.dumpLabel.place(x = 510, y = 20)
        self.showNums = True
        self.portsListed = False
        self.bytes = b''
        self.hide()

    def disable_event(self):
        pass

    def show(self):
        self.setupWin.deiconify()
        self.Showing = True
        self.draw()

    def hide(self):
        self.setupWin.withdraw()
        self.Showing = False

    def draw(self):
        if not self.Showing:
            return
        print("len of bytes = " + str(len(self.bytes)))
        if len(self.bytes) == 0:
            return
        if self.bytes[0x2A] == 4:
            offset = 0
            Yrange = 14
            byteLimit = len(self.bytes) - 1
        else:
            offset = 5
            Yrange = 15
            byteLimit = len(self.bytes) - 6
        self.canvas.delete("dump")
        for y in range(1, Yrange):
            Ypos = (y * 20) + 50
            addr = str(format(y * 16, '02X')) + " :"
            self.canvas.create_text(440, Ypos, anchor=tk.NW, text = addr, fill='#8080FF', tag="dump")
        for x in range(16):
            Xpos = x * 20 + 470
            addr = str(format(x, '02X'))
            self.canvas.create_text(Xpos, 50, anchor=tk.NW, text = addr, fill='#80FF80', tag="dump")
        for x in range(16, byteLimit):
            byt = self.bytes[x + offset]
            tx = str(format(byt, '02X'))
            Xoff = (x * 20) % 320
            Yoff = int(x / 16) * 20
            if len(self.bytes) != len(self.oldBytes):
                self.canvas.create_text(470 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
            else:
                if self.bytes[x + offset] == self.oldBytes[x + offset]:
                    self.canvas.create_text(470 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FFFFFF', tag="dump")
                else:
                    self.canvas.create_text(470 + Xoff, 50 + Yoff, anchor=tk.NW, text = tx, fill='#FF8080', tag="dump")

    def setPorts(self, inports):
        if len(inports) > 0:
            for port in inports:
                self.listbox.insert(END, port)
            self.listbox.selection_anchor(0)
            self.portsListed = True

    def openMIDI(self, event):
        if not self.portsListed:
            return
        global port
        global portOpen
        if portOpen:
            port.close()
        print("going to open: " + self.listbox.get(ANCHOR))
        port = mido.open_input(self.listbox.get(ANCHOR), callback=rxmsg)
        self.midiLabel.config(text = "MIDI port: " + self.listbox.get(ANCHOR))
        portOpen = True
        window.title("Quick Edit for Liven XFM")

    def setBytes(self, bytes):
        self.oldBytes = self.bytes
        self.bytes = bytes
        self.draw()

def print_dump(bytes):
    txt = ""
    print("10 :", end=" ")
    for x in range(16, len(bytes) - 1):
            byt = bytes[x]
            print(format(byt, '02x'), end = " ")
            if byt > 31 and byt < 128:
                txt = txt + chr(byt)
            else:
                txt = txt + '.'
            if x % 16 == 15:
                print(txt)
                print(format(x + 1, '02x'), ":", end=" ")
                txt = ""
    print()

def make_signed(byte):
    # all valuse have to pack into the 128 steps from 0x00 to 0x7F but some are
    # really "signed" values like -18..+18, -63..+63, -63..+64 so as soon as the
    # dump is received convert such values to signed which basically means (as this
    # is in 7 bits not 8 bits) that >64 should be -(128 - n)
    retval = int(byte)
    if byte > 64:
        retval = int (-1 * (128 - byte))
    return retval


def decode_bytes(bytes, patch):
    txt = ""
    # 4 character name or are there dots?
    txt += chr(bytes[0x2E])
    txt += chr(bytes[0x2F])
    txt += chr(bytes[0x30])
    txt += chr(bytes[0x32])
    #print("name len = ", bytes[0x2A])
    if bytes[0x2A] == 4:
        offset = 0
        inc = 1 # some (but not all!) values are 1 byte on compared to offset=5 (so really offset = 4)
    else:
        if bytes[0x2A] >= 5:
            txt += chr(bytes[0x33])
        if bytes[0x2A] >= 6:
            txt += chr(bytes[0x34])
        if bytes[0x2A] == 7:
            txt += chr(bytes[0x35])
        offset = 5
        inc = 0
    patch['Name'] = txt

    patch["OP1"]['Feedback'] = (make_signed(bytes[offset + 0xAE]) * 10) + make_signed(bytes[offset + 0x45])
    patch["OP1"]['OP2In'] = bytes[offset + 0xAF]
    patch["OP1"]['OP3In'] = bytes[offset + 0xB0]
    patch["OP1"]['OP4In'] = bytes[offset + 0xB1 + inc]
    patch["OP1"]['Output'] = bytes[offset + 0xC0]
    patch["OP1"]['PitchEnv'] = bytes[offset + 0xCE]
    patch["OP1"]['Fixed'] = bytes[offset + 0x49 + inc]
    if offset == 0:
        ratio = ((bytes[offset + 0x5D] * 256) + bytes[offset + 0x5C] )
        if bytes[offset + 0x59] & 0x10:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
    else:
        ratio = ((bytes[offset + 0x5D] * 256) + bytes[offset + 0x5B] )
        if bytes[offset + 0x54] & 0x01:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
    patch["OP1"]['Ratio'] = ratio
    freq = ((bytes[offset + 0x4C] * 256) + bytes[offset + 0x4B])
    if bytes[offset + 0x49] & 0x20:
        freq = freq + 128
    patch["OP1"]["Freq"] = freq
    patch["OP1"]['Detune'] = make_signed(bytes[offset + 0x5F])
    patch["OP1"]['Level'] = bytes[offset + 0x5E]
    patch["OP1"]['VelSens'] = bytes[offset + 0xC5]
    patch["OP1"]['Time'] = bytes[offset + 0xC9 + inc]
    patch["OP1"]['UpCurve'] = make_signed(bytes[offset + 0xD2 + inc])
    patch["OP1"]['DnCurve'] = make_signed(bytes[offset + 0xD3 + inc])
    patch["OP1"]['Scale'] = bytes[offset + 0x9F]
    patch["OP1"]['ALevel'] = bytes[offset + 0x72 + inc]
    patch["OP1"]['ATime'] = bytes[offset + 0x6E]
    patch["OP1"]['DLevel'] = bytes[offset + 0x73 + inc]
    patch["OP1"]['DTime'] = bytes[offset + 0x6F]
    patch["OP1"]['SLevel'] = bytes[offset + 0x75]
    patch["OP1"]['STime'] = bytes[offset + 0x70]
    patch["OP1"]['RLevel'] = bytes[offset + 0x76]
    patch["OP1"]['RTime'] = bytes[offset + 0x71 + inc]
    patch["OP1"]['LGain'] = make_signed(bytes[offset + 0x9B + inc])
    patch["OP1"]['RGain'] = make_signed(bytes[offset + 0x9D])
    patch["OP1"]['LCurve'] = bytes[offset + 0x9E] & 0x01
    patch["OP1"]['RCurve'] = 1 if bytes[offset + 0x9E] & 0x10 else 0

    patch["OP2"]['Feedback'] = (make_signed(bytes[offset + 0xB3 + inc]) * 10) + make_signed(bytes[offset + 0x46])
    patch["OP2"]['OP1In'] = bytes[offset + 0xB2 + inc]
    patch["OP2"]['OP3In'] = bytes[offset + 0xB5]
    patch["OP2"]['OP4In'] = bytes[offset + 0xB6]
    patch["OP2"]['Output'] = bytes[offset + 0xC2]
    patch["OP2"]['PitchEnv'] = bytes[offset + 0xCF]
    patch["OP2"]['Fixed'] = bytes[offset + 0x4E]
    if offset == 0:
        ratio = ((bytes[offset + 0x62] * 256) + bytes[offset + 0x60] )
        if bytes[offset + 0x59] & 0x10:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
        patch["OP2"]['Ratio'] = ratio
    else:
        ratio = ((bytes[offset + 0x5C] * 256) + bytes[offset + 0x60] )
        if bytes[offset + 0x5C] & 0x18:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
        patch["OP2"]['Ratio'] = ratio
    freq = ((bytes[offset + 0x50] * 256) + bytes[offset + 0x4F])
    if bytes[offset + 0x49] & 0x02:
        freq = freq + 128
    patch["OP2"]["Freq"] = freq
    patch["OP2"]['Detune'] = make_signed(bytes[offset + 0x63 + inc])
    patch["OP2"]['Level'] = bytes[offset + 0x62 + inc]
    patch["OP2"]['VelSens'] = bytes[offset + 0xC6]
    patch["OP2"]['Time'] = bytes[offset + 0xCA + inc]
    patch["OP2"]['UpCurve'] = make_signed(bytes[offset + 0xD5])
    patch["OP2"]['DnCurve'] = make_signed(bytes[offset + 0xD6])
    patch["OP2"]['Scale'] = bytes[offset + 0xA3 + inc]
    patch["OP2"]['ALevel'] = bytes[offset + 0x7B + inc]
    patch["OP2"]['ATime'] = bytes[offset + 0x77]
    patch["OP2"]['DLevel'] = bytes[offset + 0x7D]
    patch["OP2"]['DTime'] = bytes[offset + 0x78]
    patch["OP2"]['SLevel'] = bytes[offset + 0x7E]
    patch["OP2"]['STime'] = bytes[offset + 0x79 + inc]
    patch["OP2"]['RLevel'] = bytes[offset + 0x7F]
    patch["OP2"]['RTime'] = bytes[offset + 0x7A + inc]
    patch["OP2"]['LGain'] = make_signed(bytes[offset + 0xA0])
    patch["OP2"]['RGain'] = make_signed(bytes[offset + 0xA1 + inc])
    patch["OP2"]['LCurve'] = bytes[offset + 0xA3] & 0x01
    patch["OP2"]['RCurve'] = 1 if bytes[offset + 0xA2 + inc] & 0x10 else 0

    patch["OP3"]['Feedback'] = (make_signed(bytes[offset + 0xB9 + inc]) * 10) + make_signed(bytes[offset + 0x47])
    patch["OP3"]['OP1In'] = bytes[offset + 0xB7]
    patch["OP3"]['OP2In'] = bytes[offset + 0xB8]
    patch["OP3"]['OP4In'] = bytes[offset + 0xBA + inc]
    patch["OP3"]['Output'] = bytes[offset + 0xC3]
    patch["OP3"]['PitchEnv'] = bytes[offset + 0xD0]
    patch["OP3"]['Fixed'] = bytes[offset + 0x52 + inc]
    if offset == 0:
        ratio = ((bytes[offset + 0x66] * 256) + bytes[offset + 0x65] )
        if bytes[offset + 0x61] & 0x08:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
    else:
        ratio = ((bytes[offset + 0x66] * 256) + bytes[offset + 0x65] )
        if bytes[offset + 0x64] & 0x40:
            # bit 7 of low byte held separately...
            ratio = ratio + 128
    patch["OP3"]['Ratio'] = ratio
    freq = ((bytes[offset + 0x55] * 256) + bytes[offset + 0x54])
    if bytes[offset + 0x51] & 0x10:
        freq = freq + 128
    patch["OP3"]["Freq"] = freq
    patch["OP3"]['Detune'] = make_signed(bytes[offset + 0x68])
    patch["OP3"]['Level'] = bytes[offset + 0x67]
    patch["OP3"]['VelSens'] = bytes[offset + 0xC7]
    patch["OP3"]['Time'] = bytes[offset + 0xCB + inc]
    patch["OP3"]['UpCurve'] = make_signed(bytes[offset + 0xD7])
    patch["OP3"]['DnCurve'] = make_signed(bytes[offset + 0xD8])
    patch["OP3"]['Scale'] = bytes[offset + 0xA8]
    patch["OP3"]['ALevel'] = bytes[offset + 0x85]
    patch["OP3"]['ATime'] = bytes[offset + 0x80]
    patch["OP3"]['DLevel'] = bytes[offset + 0x86]
    patch["OP3"]['DTime'] = bytes[offset + 0x81 + inc]
    patch["OP3"]['SLevel'] = bytes[offset + 0x87]
    patch["OP3"]['STime'] = bytes[offset + 0x82 + inc]
    patch["OP3"]['RLevel'] = bytes[offset + 0x88]
    patch["OP3"]['RTime'] = bytes[offset + 0x83 + inc]
    patch["OP3"]['LGain'] = make_signed(bytes[offset + 0xA5])
    patch["OP3"]['RGain'] = make_signed(bytes[offset + 0xA6])
    patch["OP3"]['LCurve'] = bytes[offset + 0xA7] & 0x01
    patch["OP3"]['RCurve'] = 1 if bytes[offset + 0xA7] & 0x10 else 0

    patch["OP4"]['Feedback'] = (make_signed(bytes[offset + 0xBF]) * 10) + make_signed(bytes[offset + 0x48])
    patch["OP4"]['OP1In'] = bytes[offset + 0xBB + inc]
    patch["OP4"]['OP2In'] = bytes[offset + 0xBD]
    patch["OP4"]['OP3In'] = bytes[offset + 0xBE]
    patch["OP4"]['Output'] = bytes[offset + 0xC4]
    patch["OP4"]['PitchEnv'] = bytes[offset + 0xD2]
    patch["OP4"]['Fixed'] = bytes[offset + 0x57]
    ratio = ((bytes[offset + 0x6B] * 256) + bytes[offset + 0x6A] )
    if bytes[offset + 0x69] != 0:
        # bit 7 of low byte held separately...
        ratio = ratio + 128
    patch["OP4"]['Ratio'] = ratio
    freq = ((bytes[offset + 0x5A] * 256) + bytes[offset + 0x58])
    if bytes[offset + 0x51] & 0x01:
        freq = freq + 128
    patch["OP4"]["Freq"] = freq
    patch["OP4"]['Detune'] = make_signed(bytes[offset + 0x6D])
    patch["OP4"]['Level'] = bytes[offset + 0x6B + inc]
    patch["OP4"]['VelSens'] = bytes[offset + 0xC8]
    patch["OP4"]['Time'] = bytes[offset + 0xCD]
    patch["OP4"]['UpCurve'] = make_signed(bytes[offset + 0xD9 + inc])
    patch["OP4"]['DnCurve'] = make_signed(bytes[offset + 0xDA + inc])
    patch["OP4"]['Scale'] = bytes[offset + 0xAD]
    patch["OP4"]['ALevel'] = bytes[offset + 0x8E]
    patch["OP4"]['ATime'] = bytes[offset + 0x89 + inc]
    patch["OP4"]['DLevel'] = bytes[offset + 0x8F]
    patch["OP4"]['DTime'] = bytes[offset + 0x8A + inc]
    patch["OP4"]['SLevel'] = bytes[offset + 0x90]
    patch["OP4"]['STime'] = bytes[offset + 0x8B + inc]
    patch["OP4"]['RLevel'] = bytes[offset + 0x91 + inc]
    patch["OP4"]['RTime'] = bytes[offset + 0x8D]
    patch["OP4"]['LGain'] = make_signed(bytes[offset + 0xA9 + inc])
    patch["OP4"]['RGain'] = make_signed(bytes[offset + 0xAA + inc])
    patch["OP4"]['LCurve'] = bytes[offset + 0xAC] & 0x01
    patch["OP4"]['RCurve'] = 1 if bytes[offset + 0xAC] & 0x10 else 0

    patch["Pitch"]['ALevel'] = make_signed(bytes[offset + 0x97])
    patch["Pitch"]['ATime'] = bytes[offset + 0x92 + inc]
    patch["Pitch"]['DLevel'] = make_signed(bytes[offset + 0x98])
    patch["Pitch"]['DTime'] = bytes[offset + 0x93 + inc]
    patch["Pitch"]['SLevel'] = make_signed(bytes[offset + 0x99 + inc])
    patch["Pitch"]['STime'] = bytes[offset + 0x95]
    patch["Pitch"]['RLevel'] = make_signed(bytes[offset + 0x9A + inc])
    patch["Pitch"]['RTime'] = bytes[offset + 0x96]

    patch["Mixer"]['Level'] = make_signed(bytes[offset + 0xDB + inc])

def encode_bytes(patch, bytes):
    bytes[0x2E] = ord(patch['Name'][0])
    bytes[0x2F] = ord(patch['Name'][1])
    bytes[0x30] = ord(patch['Name'][2])
    bytes[0x32] = ord(patch['Name'][3])

    bytes[0x45] = patch["OP1"]['Feedback']                 # -63.0 .. +64.0 (+1.0)
    bytes[0xAF] = patch["OP1"]['OP2In']                    # 0 .. 127 (+1)
    bytes[0xB0] = patch["OP1"]['OP3In']
    bytes[0xB2] = patch["OP1"]['OP4In']
    bytes[0xC0] = patch["OP1"]['Output']                   # 0..127 (+1)
    bytes[0xCE] = patch["OP1"]['PitchEnv']                      # OFF / ON
    bytes[0x4A] = patch["OP1"]['Fixed']                    # OFF / ON
    bytes[0x5C] = (patch["OP1"]['Ratio']) & 0xFF           # 0.50 .. 32.00 (+.01) / 1 .. 9755 (+1)
    bytes[0x5D] = int((patch["OP1"]['Ratio']) / 256)
    bytes[0x5F] = patch["OP1"]['Detune']                   # -63 .. 63 (+1)
    bytes[0x5E] = patch["OP1"]['Level']                    # 0 .. 127 (+1)
    bytes[0xC5] = patch["OP1"]['VelSens']                  # 0 .. 127 (+1)
    bytes[0xCA] = patch["OP1"]['Time']                     # 0 .. 127 (+1)
    bytes[0xD3] = patch["OP1"]['UpCurve']                   # -18 .. +18 (+1)
    bytes[0xD4] = patch["OP1"]['DnCurve']                   # -18 .. +18 (+1)
    bytes[0x9F] = patch["OP1"]['Scale']                    # C1 .. C7
    bytes[0x73] = patch["OP1"]['ALevel']                   # 0 .. 127 (+1)
    bytes[0x6E] = patch["OP1"]['ATime']
    bytes[0x74] = patch["OP1"]['DLevel']
    bytes[0x6F] = patch["OP1"]['DTime']
    bytes[0x75] = patch["OP1"]['SLevel']
    bytes[0x70] = patch["OP1"]['STime']
    bytes[0x76] = patch["OP1"]['RLevel']
    bytes[0x72] = patch["OP1"]['RTime']
    bytes[0x9C] = patch["OP1"]['LGain']                    # -63 .. +63 (+1)
    bytes[0x9D] = patch["OP1"]['RGain']
    curves = (patch["OP1"]['LCurve']) | (patch["OP1"]['RCurve'])  # LINE / EXP
    bytes[0x9E] = curves

    bytes[0x46] = patch["OP2"]['Feedback']
    bytes[0xB3] = patch["OP2"]['OP1In']
    bytes[0xB5] = patch["OP2"]['OP3In']
    bytes[0xB6] = patch["OP2"]['OP4In']
    bytes[0xC2] = patch["OP2"]['Output']
    bytes[0xCF] = patch["OP2"]['PitchEnv']
    bytes[0x4E] = patch["OP2"]['Fixed']
    bytes[0x60] = (patch["OP2"]['Ratio']) & 0xFF
    bytes[0x61] = int((patch["OP2"]['Ratio']) / 256)
    bytes[0x64] = patch["OP2"]['Detune']
    bytes[0x63] = patch["OP2"]['Level']
    bytes[0xC6] = patch["OP2"]['VelSens']
    bytes[0xCB] = patch["OP2"]['Time']
    bytes[0xD5] = patch["OP2"]['UpCurve']
    bytes[0xD6] = patch["OP2"]['DnCurve']
    bytes[0xA4] = patch["OP2"]['Scale']
    bytes[0x7C] = patch["OP2"]['ALevel']
    bytes[0x77] = patch["OP2"]['ATime']
    bytes[0x7D] = patch["OP2"]['DLevel']
    bytes[0x78] = patch["OP2"]['DTime']
    bytes[0x7E] = patch["OP2"]['SLevel']
    bytes[0x7A] = patch["OP2"]['STime']
    bytes[0x7F] = patch["OP2"]['RLevel']
    bytes[0x7B] = patch["OP2"]['RTime']
    bytes[0xA0] = patch["OP2"]['LGain']
    bytes[0xA2] = patch["OP2"]['RGain']
    curves = (patch["OP2"]['LCurve']) | (patch["OP2"]['RCurve'])
    bytes[0xA3] = curves

    bytes[0x47] = patch["OP3"]['Feedback']
    bytes[0xB7] = patch["OP3"]['OP1In']
    bytes[0xB8] = patch["OP3"]['OP2In']
    bytes[0xBB] = patch["OP3"]['OP4In']
    bytes[0xC3] = patch["OP3"]['Output']
    bytes[0xD0] = patch["OP3"]['PitchEnv']
    bytes[0x53] = patch["OP3"]['Fixed']
    bytes[0x65] = (patch["OP3"]['Ratio']) & 0xFF
    bytes[0x66] = int((patch["OP3"]['Ratio']) / 256)
    bytes[0x68] = patch["OP3"]['Detune']
    bytes[0x67] = patch["OP3"]['Level']
    bytes[0xC7] = patch["OP3"]['VelSens']
    bytes[0xCC] = patch["OP3"]['Time']
    bytes[0xD7] = patch["OP3"]['UpCurve']
    bytes[0xD8] = patch["OP3"]['DnCurve']
    bytes[0xA8] = patch["OP3"]['Scale']
    bytes[0x85] = patch["OP3"]['ALevel']
    bytes[0x80] = patch["OP3"]['ATime']
    bytes[0x86] = patch["OP3"]['DLevel']
    bytes[0x82] = patch["OP3"]['DTime']
    bytes[0x87] = patch["OP3"]['SLevel']
    bytes[0x83] = patch["OP3"]['STime']
    bytes[0x88] = patch["OP3"]['RLevel']
    bytes[0x84] = patch["OP3"]['RTime']
    bytes[0xA5] = patch["OP3"]['LGain']
    bytes[0xA6] = patch["OP3"]['RGain']
    curves = (patch["OP3"]['LCurve']) | (patch["OP3"]['RCurve'])
    bytes[0xA7] = curves

    bytes[0x48] = patch["OP4"]['Feedback']
    bytes[0xBC] = patch["OP4"]['OP1In']
    bytes[0xBD] = patch["OP4"]['OP2In']
    bytes[0xBE] = patch["OP4"]['OP3In']
    bytes[0xC4] = patch["OP4"]['Output']
    bytes[0xD2] = patch["OP4"]['PitchEnv']
    bytes[0x57] = patch["OP4"]['Fixed']
    bytes[0x6A] = (patch["OP4"]['Ratio']) & 0xFF
    bytes[0x6B] = int((patch["OP4"]['Ratio']) / 256)
    bytes[0x6D] = patch["OP4"]['Detune']
    bytes[0x6C] = patch["OP4"]['Level']
    bytes[0xC8] = patch["OP4"]['VelSens']
    bytes[0xCD] = patch["OP4"]['Time']
    bytes[0xDA] = patch["OP4"]['UpCurve']
    bytes[0xDB] = patch["OP4"]['DnCurve']
    bytes[0xAD] = patch["OP4"]['Scale']
    bytes[0x8E] = patch["OP4"]['ALevel']
    bytes[0x8A] = patch["OP4"]['ATime']
    bytes[0x8F] = patch["OP4"]['DLevel']
    bytes[0x8B] = patch["OP4"]['DTime']
    bytes[0x90] = patch["OP4"]['SLevel']
    bytes[0x8C] = patch["OP4"]['STime']
    bytes[0x92] = patch["OP4"]['RLevel']
    bytes[0x8D] = patch["OP4"]['RTime']
    bytes[0xAA] = patch["OP4"]['LGain']
    bytes[0xAB] = patch["OP4"]['RGain']
    curves = (patch["OP4"]['LCurve']) | (patch["OP4"]['RCurve'])
    bytes[0xAC] = curves

    bytes[0x97] = patch["Pitch"]['ALevel']         # -48 .. +48 (+1)
    bytes[0x93] = patch["Pitch"]['ATime']          # 0 .. 127 (+1)
    bytes[0x98] = patch["Pitch"]['DLevel']
    bytes[0x94] = patch["Pitch"]['DTime']
    bytes[0x9A] = patch["Pitch"]['SLevel']
    bytes[0x95] = patch["Pitch"]['STime']
    bytes[0x9B] = patch["Pitch"]['RLevel']
    bytes[0x96] = patch["Pitch"]['RTime']

    bytes[0xDC] = patch["Mixer"]['Level']           # -63 .. +63 (+1)

def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    # sound dump comes in 3 messages - look for the middle one with sequence number 2 (from 1, 2, 3)
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
        bytes = msg.bytes()
        setupWin.setBytes(bytes)

        print_dump(bytes)

        decode_bytes(bytes, patch)
        saveJson(patch)

        # then load the patch (dict)
        loadCtrls(patch)
        routeWin.draw()

def loadCtrls(data):
    for i in data:
        print("=====", i, "=====")
        if (i != "Name"):
            for j in data[i]:
                key = f'{i}:{j}'
                print(f'{key} = ', data[i][j])
                valToSet = data[i][j]
                if j == "Freq" or j == "Ratio":                
                    controllist[key][0].setValue(int(valToSet / 100))
                    controllist[key][0].fraction = int(valToSet % 100)
                elif j == "Feedback":
                    controllist[key][0].setValue(int(valToSet / 10))
                    controllist[key][0].fraction = int(abs(valToSet) % 10)
                else:
                    controllist[key][0].setValue(valToSet)
                controllist[key][0].draw()
        else:
            charCount = 0
            n = 0
            while n < len(data[i]):
                withDot = False
                key = f'{i}:chr{charCount}'
                print(f'{n}:{charCount}: {key} =  {data[i][n]}')
                chrnum = ord(data[i][n])
                if n < (len(data[i]) - 1):
                    if data[i][n + 1] == '.':
                        withDot = True
                if chrnum >= ord('A'):
                    chrnum = chrnum - ord('A') + 11 # 11 not 10 because ' '
                else:
                    chrnum = chrnum - ord('0')
                if withDot == True:
                    chrnum = chrnum + 100 # mark that a dot needs to be drawn
                    n = n + 1
                controllist[key][0].index = chrnum
                controllist[key][0].draw()
                charCount = charCount + 1
                n = n + 1
        for j in ['OP1:', 'OP2:', 'OP3:', 'OP4:', 'Pitch:']:
            adsrs[j].draw()

def readCtrls():
    patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
    nameList = list()
    for x in controllist:
        sect= x.split(':')[0]
        item = x.split(':')[1]
        if sect == "Name":
            dot  = False
            namechr = controllist[x][0].getValue()
            if namechr > 100:
                dot = True
                namechr = namechr - 100
            if namechr < 10:
                namechr = namechr + ord('0')
            elif namechr == 10:
                namechr = ord(' ')
            else:
                namechr = namechr - 11 + ord('A')
            nameList.append(chr(namechr))
            if dot:
                nameList.append('.')
            if item == "chr3":
                patch["Name"] = ''.join(nameList)
        elif item == "Freq" or item == "Ratio":
            patch[sect][item] = (controllist[x][0].getValue() * 100) + controllist[x][0].fraction
        elif item == "Feedback":
            patch[sect][item] = (controllist[x][0].getValue() * 10) + controllist[x][0].fraction
        else:
            patch[sect][item] = controllist[x][0].getValue()
    return patch

def loadInitJson():
    with open("initpatch.json") as f:
        data = json.load(f)
        loadCtrls(data)

def saveJson(patch):
    jsonpatch = json.dumps(patch, indent=4)
    with open("savetest.json", 'w') as f:
        f.write(jsonpatch)

#============================= THE start ================================
portOpen = False

window = Tk()
window.geometry("1720x930")
window.title("Quick Edit for Liven XFM - no MIDI port open - use Setup!!")
window.iconbitmap("xicon.ico")
window.configure(bg='#313131')
window.resizable(False, False)

# There are only so many different types of control and each has an animated PNG
# The entries are filename and number of frames (so frame height is overall height / num frames)
anims = {
    "0to127" :  [ "ctrl_0_127.png", 128 ],
    "on_off" :  [ "ctrl_on_off.png", 2 ],
    "line_exp" :[ "ctrl_line_exp.png", 2 ],
    "_18to18" : [ "ctrl_-18_18.png", 37 ],
    "slideH" :  [ "ctrl_slide_H.png", 128],
    "slideV" :  [ "ctrl_slide_V.png", 128],
    "slideVbi" :[ "ctrl_slide_V-48_48.png", 97],
    "_63to63" : [ "ctrl_-63_63.png", 127 ],
    "C1toC7" :  [ "ctrl_C1_C7.png", 7 ],
    "chars" :   [ "lcd_chars.png", 38 ],
    "blk128" :  [ "ctrl_blank_128.png", 128 ],
    "blk33" :   [ "ctrl_blank_33.png", 33 ],
    "blk98" :   [ "ctrl_blank_98.png", 98 ],
    "op1_4" :   [ "op_logo.png", 4 ],
    "dig_d_99" :[ "digits_dot_0_99.png", 100 ],
    "dig_d_9" : [ "digits_dot_0_9.png", 10 ],
    "digits" :  [ "digits_0_127.png", 128 ],
    "digits0" : [ "digits_00_127.png", 128 ],
    "neg"    :  [ "digit_neg.png", 1],
    "litegrey" :[ "lightgrey.png", 1],
    "dot" :     [ "dot.png", 1]
}

# Given the above list open each PNG in turn and break them into N separate anim frames
ctrlimgs = {}
for anim in anims:
    fname = anims[anim][0]
    numFrame = anims[anim][1]
    img = Image.open(fname)
    width = img.size[0]
    # following is total height so if 7 frame anim and each frame is 32px high this is 224 e.g.
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

waveSineImage = ImageTk.PhotoImage(Image.open("sine.png").resize((32,32), Image.Resampling.LANCZOS))
waveSawImage = ImageTk.PhotoImage(Image.open("saw.png").resize((32,32), Image.Resampling.LANCZOS))
waveSquareImage = ImageTk.PhotoImage(Image.open("square.png").resize((32,32), Image.Resampling.LANCZOS))
waveNoiseImage = ImageTk.PhotoImage(Image.open("noise.png").resize((32,32), Image.Resampling.LANCZOS))

# Textured grey used as background for all 5 sub-windows
rawback = Image.open("dark-grey.jpg")
opback = rawback.resize((685, 460))
backimg = ImageTk.PhotoImage(opback)

# Background for pitch/master edit right - same image just resized
mstrback = rawback.resize((340, 928))
mstrimg = ImageTk.PhotoImage(mstrback)

# "Quick Edit for Sonicware Liven XFM logo"
rawlogo = Image.open("logo.png")
mainlogo = ImageTk.PhotoImage(rawlogo)

Backdrop("OP1", 0, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][0], 0, 8)
Backdrop("OP2", 688, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][1], 0, 8)
Backdrop("OP3", 0, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][2], 0, 8)
Backdrop("OP4", 688, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][3], 0, 8)
Backdrop("Master", 1375, 0, 340, 922, mstrimg, mainlogo, 15, 680)

adsrs = {}
# The five grey ADSR canvases
adsrs["OP1:"] = Adsr("OP1:", 210, 250)
adsrs["OP2:"] = Adsr("OP2:", 890, 250)
adsrs["OP3:"] = Adsr("OP3:", 210, 710)
adsrs["OP4:"] = Adsr("OP4:", 890, 710)
adsrs["Pitch:"] = Adsr("Pitch:", 1410, 270)

XOFF = 690
YOFF = 460
COL_RATIO = 500
COL_FEEDBACK = 590
COL_TIMESCALE = 10
COL_DETUNE = 100
TIME_SLIDE_Y = 400
LEVEL_SLIDE_Y = 70
SWITCH_X = 210
SWITCH_OFFX = 70
SWITCH_Y = 20

# following is list of all animated controls - a key name, a label, an anim to use and X/Y
controls = {
    "Name:chr0" :    [ "",          "chars",   1430, 10 ],
    "Name:chr1" :    [ "",          "chars",   1430 + 64 - 8, 10 ],
    "Name:chr2" :    [ "",          "chars",   1430 + ((64 - 8) * 2), 10 ],
    "Name:chr3":     [ "",          "chars",   1430 + ((64 - 8) * 3), 10 ],

    "OP1:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, 10, -63 ],
    "OP1:OP2In" :    [ "OP2 Input", "0to127",    COL_RATIO, 130 ],
    "OP1:OP3In" :    [ "OP3 Input", "0to127",    COL_FEEDBACK, 130 ],
    "OP1:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, 220 ],
    "OP1:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, 220 ],
    "OP1:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP1:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    # two controls - one location - what's displayed depends on Fixed On/Off
    "OP1:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, 25, -63 ],
    "OP1:Level" :    [ "Level",     "0to127",    COL_RATIO, 310 ],
    "OP1:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, 310 ],
    "OP1:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, 130 ],
    "OP1:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, 130, -18 ],
    "OP1:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, 220, -18 ],
    "OP1:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, 220 ],
    "OP1:ALevel" :   [ "A Level",   "slideV",    210, LEVEL_SLIDE_Y ],
    "OP1:ATime" :    [ "A Time",    "slideH",    10, TIME_SLIDE_Y ],
    "OP1:DLevel" :   [ "D Level",   "slideV",    280, LEVEL_SLIDE_Y ],
    "OP1:DTime" :    [ "D Time",    "slideH",    180, TIME_SLIDE_Y ],
    "OP1:SLevel" :   [ "S Level",   "slideV",    350, LEVEL_SLIDE_Y ],
    "OP1:STime" :    [ "S Time",    "slideH",    350, TIME_SLIDE_Y ],
    "OP1:RLevel" :   [ "R Level",   "slideV",    420, LEVEL_SLIDE_Y ],
    "OP1:RTime" :    [ "R Time",    "slideH",    520, TIME_SLIDE_Y ],
    "OP1:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, 310, -63 ],
    "OP1:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, 310, -63 ],
    "OP1:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, SWITCH_Y ],
    "OP1:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],

    "OP2:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, 10, -63 ],
    "OP2:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, 130 ],
    "OP2:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_FEEDBACK, 130 ],
    "OP2:OP4In" :    [ "OP4 Input", "0to127",    XOFF + COL_RATIO, 220 ],
    "OP2:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, 220 ],
    "OP2:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, 25, -63 ],
    "OP2:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, 310 ],
    "OP2:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, 310 ],
    "OP2:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, 130 ],
    "OP2:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, 130, -18 ],
    "OP2:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, 220, -18 ],
    "OP2:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, 220 ],
    "OP2:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, LEVEL_SLIDE_Y ],
    "OP2:ATime" :    [ "A Time",    "slideH",    XOFF + 10, TIME_SLIDE_Y ],
    "OP2:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, LEVEL_SLIDE_Y ],
    "OP2:DTime" :    [ "D Time",    "slideH",    XOFF + 180, TIME_SLIDE_Y ],
    "OP2:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, LEVEL_SLIDE_Y ],
    "OP2:STime" :    [ "S Time",    "slideH",    XOFF + 350, TIME_SLIDE_Y ],
    "OP2:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, LEVEL_SLIDE_Y ],
    "OP2:RTime" :    [ "R Time",    "slideH",    XOFF + 520, TIME_SLIDE_Y ],
    "OP2:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, 310, -63 ],
    "OP2:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, 310, -63 ],
    "OP2:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, SWITCH_Y ],
    "OP2:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],

    "OP3:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP3:OP1In" :    [ "OP1 Input", "0to127",    COL_RATIO, YOFF + 130 ],
    "OP3:OP2In" :    [ "OP2 Input", "0to127",    COL_FEEDBACK, YOFF + 130 ],
    "OP3:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, YOFF + 220 ],
    "OP3:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, YOFF + 220 ],
    "OP3:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, YOFF + 25, -63 ],
    "OP3:Level" :    [ "Level",     "0to127",    COL_RATIO, YOFF + 310 ],
    "OP3:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, YOFF + 310 ],
    "OP3:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, YOFF + 130 ],
    "OP3:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, YOFF + 130, -18 ],
    "OP3:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, YOFF + 220, -18 ],
    "OP3:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, YOFF + 220 ],
    "OP3:ALevel" :   [ "A Level",   "slideV",    210, YOFF + LEVEL_SLIDE_Y ],
    "OP3:ATime" :    [ "A Time",    "slideH",    10, YOFF + TIME_SLIDE_Y ],
    "OP3:DLevel" :   [ "D Level",   "slideV",    280, YOFF + LEVEL_SLIDE_Y ],
    "OP3:DTime" :    [ "D Time",    "slideH",    180, YOFF + TIME_SLIDE_Y ],
    "OP3:SLevel" :   [ "S Level",   "slideV",    350, YOFF + LEVEL_SLIDE_Y ],
    "OP3:STime" :    [ "S Time",    "slideH",    350, YOFF + TIME_SLIDE_Y ],
    "OP3:RLevel" :   [ "R Level",   "slideV",    420, YOFF + LEVEL_SLIDE_Y ],
    "OP3:RTime" :    [ "R Time",    "slideH",    520, YOFF + TIME_SLIDE_Y ],
    "OP3:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, YOFF + 310, -63 ],
    "OP3:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, YOFF + 310, -63 ],
    "OP3:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, YOFF + SWITCH_Y ],
    "OP3:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],

    "OP4:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP4:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, YOFF + 130 ],
    "OP4:OP2In" :    [ "OP2 Input", "0to127",    XOFF + COL_FEEDBACK, YOFF + 130 ],
    "OP4:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_RATIO, YOFF + 220 ],
    "OP4:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, YOFF + 220 ],
    "OP4:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, YOFF + 25, -63 ],
    "OP4:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, YOFF + 310 ],
    "OP4:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, YOFF + 310 ],
    "OP4:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, YOFF + 130 ],
    "OP4:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, YOFF + 130, -18 ],
    "OP4:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, YOFF + 220, -18 ],
    "OP4:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, YOFF + 220 ],
    "OP4:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, YOFF + LEVEL_SLIDE_Y ],
    "OP4:ATime" :    [ "A Time",    "slideH",    XOFF + 10, YOFF + TIME_SLIDE_Y ],
    "OP4:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, YOFF + LEVEL_SLIDE_Y ],
    "OP4:DTime" :    [ "D Time",    "slideH",    XOFF + 180, YOFF + TIME_SLIDE_Y ],
    "OP4:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, YOFF + LEVEL_SLIDE_Y ],
    "OP4:STime" :    [ "S Time",    "slideH",    XOFF + 350, YOFF + TIME_SLIDE_Y ],
    "OP4:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, YOFF + LEVEL_SLIDE_Y ],
    "OP4:RTime" :    [ "R Time",    "slideH",    XOFF + 520, YOFF + TIME_SLIDE_Y ],
    "OP4:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, YOFF + 310, -63 ],
    "OP4:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, YOFF + 310, -63 ],
    "OP4:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, YOFF + SWITCH_Y ],
    "OP4:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],

    "Pitch:ALevel" : [ "A Level",   "slideVbi",    1410, 90, -48 ],
    "Pitch:ATime" :  [ "A Time",    "slideH",    1410, 410 ],
    "Pitch:DLevel" : [ "D Level",   "slideVbi",    1480, 90, -48 ],
    "Pitch:DTime" :  [ "D Time",    "slideH",    1410, 460 ],
    "Pitch:SLevel" : [ "S Level",   "slideVbi",    1550, 90, -48 ],
    "Pitch:STime" :  [ "S Time",    "slideH",    1410, 510 ],
    "Pitch:RLevel" : [ "R Level",   "slideVbi",    1620, 90, -48 ],
    "Pitch:RTime" :  [ "R Time",    "slideH",    1410, 560 ],

    "Mixer:Level" :  [ "Mixer Level","_63to63",   1600, 500, -63 ],
}

# For all the above controls simply create their anm objects but don't draw until inits set
controllist = {}
for key in controls:
    entry = controls[key]
    if len(entry) == 4:
        thisanim = Anim(key, title = entry[0], ctrl = entry[1], xpos = entry[2], ypos = entry[3])
    else:
        thisanim = Anim(key, title = entry[0], ctrl = entry[1], xpos = entry[2], ypos = entry[3], offset = entry[4])
    controllist.update({key : [thisanim]})

# following is a JSON experiment to load a file (when a canvas is clicked) and load all the
# values into the controls
def loadJSON(event):
    loadInitJson()

def saveJSON(event):
    patch = readCtrls()
    saveJson(patch)

load = Canvas(width=32, height=32, highlightthickness=0)
load.place(x=1650, y=410)
load.create_rectangle(0,0, 31, 31, fill='#C00000')
load.create_text(0, 0, anchor=tk.NW, text="JSON\ninit", fill='#FFFFFF')
load.bind('<Button>', loadJSON)

save = Canvas(width=32, height=32, highlightthickness=0)
save.place(x=1600, y=410)
save.create_rectangle(0,0, 31, 31, fill='#00C000')
save.create_text(0, 0, anchor=tk.NW, text="JSON\nsave", fill='#FFFFFF')
save.bind('<Button>', saveJSON)

routeWin = RouteWindow()

def routeButtonClick(event):
    if not routeWin.Showing:
        routeWin.show()
        routeButton.itemconfig(route_label, text="Hide\nRoute")
    else:
        routeButton.itemconfig(route_label, text="Show\nRoute")
        routeWin.hide()

routeButton = Canvas(width=32, height=32, highlightthickness=0)
routeButton.place(x=1600, y=450)
routeButton.create_rectangle(0,0, 31, 31, fill='#0000C0')
route_label = routeButton.create_text(0, 0, anchor=tk.NW, text="Show\nRoute", fill='#FFFFFF')
routeButton.bind('<Button>', routeButtonClick)

setupWin = SetupWindow()

def setupButtonClick(event):
    if not setupWin.Showing:
        setupWin.show()
    else:
        setupWin.hide()

setupButton = Canvas(width=32, height=32, highlightthickness=0)
setupButton.place(x=1650, y=450)
setupButton.create_rectangle(0,0, 31, 31, fill='#C000C0')
setupButton.create_text(0, 0, anchor=tk.NW, text="Setup", fill='#FFFFFF')
setupButton.bind('<Button>', setupButtonClick)

# load initpatch.json (which will default to an "init" patch.
loadInitJson()

# Now init values are set run throught the list and draw all animated controls
for entry in controllist:
    controllist[entry][0].draw()

inports = mido.get_input_names()
setupWin.setPorts(inports)

if len(inports):
    print("MIDI ports:", inports)

window.mainloop()
