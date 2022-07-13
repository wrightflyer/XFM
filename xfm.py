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
            #print("so settint it now")
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
        self.make_inbounds()
        self.canvas.delete(self.keyname)
        self.canvas.delete("digits")
        self.canvas.create_image(0, 11, anchor=tk.NW, image = self.getFrame(), tag=self.keyname)
        op = self.keyname.split(':')[0]
        ctrl = self.keyname.split(':')[1]
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
    txt += chr(bytes[0x2E])
    txt += chr(bytes[0x2F])
    txt += chr(bytes[0x30])
    txt += chr(bytes[0x32])
    patch['Name'] = txt

    patch["OP1"]['Feedback'] = make_signed(bytes[0x45])
    patch["OP1"]['OP2In'] = bytes[0xAF]
    patch["OP1"]['OP3In'] = bytes[0xB0]
    patch["OP1"]['OP4In'] = bytes[0xB2]
    patch["OP1"]['Output'] = bytes[0xC0]
    patch["OP1"]['PitchEnv'] = bytes[0xCE]
    patch["OP1"]['Fixed'] = bytes[0x4A]
    ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
    if bytes[0x59] & 0x10:
        # bit 7 of low byte held separately...
        ratio = ratio + 128
    patch["OP1"]['Ratio'] = ratio
    patch["OP1"]['Detune'] = make_signed(bytes[0x5F])
    patch["OP1"]['Level'] = bytes[0x5E]
    patch["OP1"]['VelSens'] = bytes[0xC5]
    patch["OP1"]['Time'] = bytes[0xCA]
    patch["OP1"]['UpCurve'] = make_signed(bytes[0xD3])
    patch["OP1"]['DnCurve'] = make_signed(bytes[0xD4])
    patch["OP1"]['Scale'] = bytes[0x9F]
    patch["OP1"]['ALevel'] = bytes[0x73]
    patch["OP1"]['ATime'] = bytes[0x6E]
    patch["OP1"]['DLevel'] = bytes[0x74]
    patch["OP1"]['DTime'] = bytes[0x6F]
    patch["OP1"]['SLevel'] = bytes[0x75]
    patch["OP1"]['STime'] = bytes[0x70]
    patch["OP1"]['RLevel'] = bytes[0x76]
    patch["OP1"]['RTime'] = bytes[0x72]
    patch["OP1"]['LGain'] = make_signed(bytes[0x9C])
    patch["OP1"]['RGain'] = make_signed(bytes[0x9D])
    patch["OP1"]['LCurve'] = bytes[0x9E] & 0x01
    patch["OP1"]['RCurve'] = bytes[0x9E] & 0x10

    patch["OP2"]['Feedback'] = make_signed(bytes[0x46])
    patch["OP2"]['OP1In'] = bytes[0xB3]
    patch["OP2"]['OP3In'] = bytes[0xB5]
    patch["OP2"]['OP4In'] = bytes[0xB6]
    patch["OP2"]['Output'] = bytes[0xC2]
    patch["OP2"]['PitchEnv'] = bytes[0xCF]
    patch["OP2"]['Fixed'] = bytes[0x4E]
    ratio = ((bytes[0x61] * 256) + bytes[0x60] )
    if bytes[0x59] & 0x01:
        # bit 7 of low byte held separately...
        ratio = ratio + 128
    patch["OP2"]['Ratio'] = ratio
    patch["OP2"]['Detune'] = make_signed(bytes[0x64])
    patch["OP2"]['Level'] = bytes[0x63]
    patch["OP2"]['VelSens'] = bytes[0xC6]
    patch["OP2"]['Time'] = bytes[0xCB]
    patch["OP2"]['UpCurve'] = make_signed(bytes[0xD5])
    patch["OP2"]['DnCurve'] = make_signed(bytes[0xD6])
    patch["OP2"]['Scale'] = bytes[0xA4]
    patch["OP2"]['ALevel'] = bytes[0x7C]
    patch["OP2"]['ATime'] = bytes[0x77]
    patch["OP2"]['DLevel'] = bytes[0x7D]
    patch["OP2"]['DTime'] = bytes[0x78]
    patch["OP2"]['SLevel'] = bytes[0x7E]
    patch["OP2"]['STime'] = bytes[0x7A]
    patch["OP2"]['RLevel'] = bytes[0x7F]
    patch["OP2"]['RTime'] = bytes[0x7B]
    patch["OP2"]['LGain'] = make_signed(bytes[0xA0])
    patch["OP2"]['RGain'] = make_signed(bytes[0xA2])
    patch["OP2"]['LCurve'] = bytes[0xA3] & 0x01
    patch["OP2"]['RCurve'] = bytes[0xA3] & 0x10

    patch["OP3"]['Feedback'] = make_signed(bytes[0x47])
    patch["OP3"]['OP1In'] = bytes[0xB7]
    patch["OP3"]['OP2In'] = bytes[0xB8]
    patch["OP3"]['OP4In'] = bytes[0xBB]
    patch["OP3"]['Output'] = bytes[0xC3]
    patch["OP3"]['PitchEnv'] = bytes[0xD0]
    patch["OP3"]['Fixed'] = bytes[0x53]
    ratio = ((bytes[0x66] * 256) + bytes[0x65] )
    if bytes[0x61] != 0:
        # bit 7 of low byte held separately...
        ratio = ratio + 128
    patch["OP3"]['Ratio'] = ratio
    patch["OP3"]['Detune'] = make_signed(bytes[0x68])
    patch["OP3"]['Level'] = bytes[0x67]
    patch["OP3"]['VelSens'] = bytes[0xC7]
    patch["OP3"]['Time'] = bytes[0xCC]
    patch["OP3"]['UpCurve'] = make_signed(bytes[0xD7])
    patch["OP3"]['DnCurve'] = make_signed(bytes[0xD8])
    patch["OP3"]['Scale'] = bytes[0xA8]
    patch["OP3"]['ALevel'] = bytes[0x85]
    patch["OP3"]['ATime'] = bytes[0x80]
    patch["OP3"]['DLevel'] = bytes[0x86]
    patch["OP3"]['DTime'] = bytes[0x82]
    patch["OP3"]['SLevel'] = bytes[0x87]
    patch["OP3"]['STime'] = bytes[0x83]
    patch["OP3"]['RLevel'] = bytes[0x88]
    patch["OP3"]['RTime'] = bytes[0x84]
    patch["OP3"]['LGain'] = make_signed(bytes[0xA5])
    patch["OP3"]['RGain'] = make_signed(bytes[0xA6])
    patch["OP3"]['LCurve'] = bytes[0xA7] & 0x01
    patch["OP3"]['RCurve'] = bytes[0xA7] & 0x10

    patch["OP4"]['Feedback'] = make_signed(bytes[0x48])
    patch["OP4"]['OP1In'] = bytes[0xBC]
    patch["OP4"]['OP2In'] = bytes[0xBD]
    patch["OP4"]['OP3In'] = bytes[0xBE]
    patch["OP4"]['Output'] = bytes[0xC4]
    patch["OP4"]['PitchEnv'] = bytes[0xD2]
    patch["OP4"]['Fixed'] = bytes[0x57]
    ratio = ((bytes[0x6B] * 256) + bytes[0x6A] )
    if bytes[0x69] != 0:
        # bit 7 of low byte held separately...
        ratio = ratio + 128
    patch["OP4"]['Ratio'] = ratio
    patch["OP4"]['Detune'] = make_signed(bytes[0x6D])
    patch["OP4"]['Level'] = bytes[0x6C]
    patch["OP4"]['VelSens'] = bytes[0xC8]
    patch["OP4"]['Time'] = bytes[0xCD]
    patch["OP4"]['UpCurve'] = make_signed(bytes[0xDA])
    patch["OP4"]['DnCurve'] = make_signed(bytes[0xDB])
    patch["OP4"]['Scale'] = bytes[0xAD]
    patch["OP4"]['ALevel'] = bytes[0x8E]
    patch["OP4"]['ATime'] = bytes[0x8A]
    patch["OP4"]['DLevel'] = bytes[0x8F]
    patch["OP4"]['DTime'] = bytes[0x8B]
    patch["OP4"]['SLevel'] = bytes[0x90]
    patch["OP4"]['STime'] = bytes[0x8C]
    patch["OP4"]['RLevel'] = bytes[0x92]
    patch["OP4"]['RTime'] = bytes[0x8D]
    patch["OP4"]['LGain'] = make_signed(bytes[0xAA])
    patch["OP4"]['RGain'] = make_signed(bytes[0xAB])
    patch["OP4"]['LCurve'] = bytes[0xAC] & 0x01
    patch["OP4"]['RCurve'] = bytes[0xAC] & 0x10

    patch["Pitch"]['ALevel'] = make_signed(bytes[0x97])
    patch["Pitch"]['ATime'] = bytes[0x93]
    patch["Pitch"]['DLevel'] = make_signed(bytes[0x98])
    patch["Pitch"]['DTime'] = bytes[0x94]
    patch["Pitch"]['SLevel'] = make_signed(bytes[0x9A])
    patch["Pitch"]['STime'] = bytes[0x95]
    patch["Pitch"]['RLevel'] = make_signed(bytes[0x9B])
    patch["Pitch"]['RTime'] = bytes[0x96]

    patch["Mixer"]['Level'] = make_signed(bytes[0xDC])

def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    # sound dump comes in 3 messages - look for the middle one with sequence number 2 (from 1, 2, 3)
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = { "Name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
        bytes = msg.bytes()

        print_dump(bytes)

        decode_bytes(bytes, patch)
        jsonpatch = json.dumps(patch, indent=4)

        print(jsonpatch)
        with open("activepatch.json", 'w') as f:
            f.write(json.dumps(patch, indent=4))

        loadJson()

def loadJson():
    with open("activepatch.json") as f:
        data = json.load(f)

        for i in data:
            print("=====", i, "=====")
            if (i != "Name"):
                for j in data[i]:
                    key = f'{i}:{j}'
                    print(f'{key} = ', data[i][j])
                    controllist[key][0].setValue(data[i][j])
                    controllist[key][0].draw()
            else:
                for n in range(4):
                    key = f'{i}:chr{n}'
                    print(f'{key} = ', data[i][n])
                    chrnum= ord(data[i][n])
                    if chrnum >= ord('A'):
                        chrnum = chrnum - ord('A') + 10
                    else:
                        chrnum = chrnum - ord('0')
                    controllist[key][0].setValue(chrnum)
                    controllist[key][0].draw()
            for j in ['OP1:', 'OP2:', 'OP3:', 'OP4:', 'Pitch:']:
                adsrs[j].draw()

#============================= THE start ================================
window = Tk()
window.geometry("1720x930")
window.title("Quick Edit for Liven XFM")
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
    "chars" :   [ "lcd_chars.png", 36 ],
    "blk128" :  [ "ctrl_blank_128.png", 128 ],
    "blk33" :   [ "ctrl_blank_33.png", 33 ],
    "blk98" :   [ "ctrl_blank_98.png", 98 ],
    "op1_4" :   [ "op_logo.png", 4 ],
    "dig_d_99" :[ "digits_dot_0_99.png", 100 ],
    "dig_d_9" : [ "digits_dot_0_9.png", 10 ],
    "digits" :  [ "digits_0_127.png", 128 ],
    "digits0" : [ "digits_00_127.png", 128 ],
    "neg"    :  [ "digit_neg.png", 1],
    "litegrey" :[ "lightgrey.png", 1]
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

# Textured grey used as background for all 5 sub-windows
rawback = Image.open("xfm/resources/dark-grey-texture-abstract-hd-wallpaper-1920x1200-1223.jpg")
opback = rawback.resize((685, 460))
backimg = ImageTk.PhotoImage(opback)

# Background for pitch/master edit right - same image just resized
mstrback = rawback.resize((340, 882))
mstrimg = ImageTk.PhotoImage(mstrback)

# "Quick Edit for Sonicware Liven XFM logo"
rawlogo = Image.open("logo.png")
mainlogo = ImageTk.PhotoImage(rawlogo)

Backdrop("OP1", 0, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][0], 0, 8)
Backdrop("OP2", 688, 0, 684, 460, backimg, ctrlimgs["op1_4"]["frames"][1], 0, 8)
Backdrop("OP3", 0, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][2], 0, 8)
Backdrop("OP4", 688, 462, 684, 462, backimg, ctrlimgs["op1_4"]["frames"][3], 0, 8)
Backdrop("Master", 1375, 0, 340, 922, mstrimg, mainlogo, 30, 630)

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
    # Knobs
    "OP1:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, 10, -63 ],
    "OP1:OP3In" :    [ "OP3 Input", "0to127",    COL_FEEDBACK, 130 ],
    "OP1:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, 220 ],
    "OP1:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, 310 ],
    # two controls - one location - what's displayed depends on Fixed On/Off
    "OP1:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, 10 ],#not 0to127 !
    "OP1:OP2In" :    [ "OP2 Input", "0to127",    COL_RATIO, 130 ],
    "OP1:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, 220 ],
    "OP1:Level" :    [ "Level",     "0to127",    COL_RATIO, 310 ],
    "OP1:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, 25, -63 ],
    "OP1:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, 130, -18 ],
    "OP1:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, 220, -18 ],
    "OP1:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, 310, -63 ],
    "OP1:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, 130 ],
    "OP1:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, 220 ],
    "OP1:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, 310, -63 ],
    # Switches
    "OP1:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, SWITCH_Y ],
    "OP1:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],
    "OP1:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP1:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    # Sliders
    "OP1:ALevel" :   [ "A Level",   "slideV",    210, LEVEL_SLIDE_Y ],
    "OP1:DLevel" :   [ "D Level",   "slideV",    280, LEVEL_SLIDE_Y ],
    "OP1:SLevel" :   [ "S Level",   "slideV",    350, LEVEL_SLIDE_Y ],
    "OP1:RLevel" :   [ "R Level",   "slideV",    420, LEVEL_SLIDE_Y ],
    "OP1:ATime" :    [ "A Time",    "slideH",    10, TIME_SLIDE_Y ],
    "OP1:DTime" :    [ "D Time",    "slideH",    180, TIME_SLIDE_Y ],
    "OP1:STime" :    [ "S Time",    "slideH",    350, TIME_SLIDE_Y ],
    "OP1:RTime" :    [ "R Time",    "slideH",    520, TIME_SLIDE_Y ],

    # Knobs
    "OP2:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, 10, -63 ],
    "OP2:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_FEEDBACK, 130 ],
    "OP2:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, 220 ],
    "OP2:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, 310 ],
    "OP2:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, 10 ],
    "OP2:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, 130 ],
    "OP2:OP4In" :    [ "OP4 Input", "0to127",    XOFF + COL_RATIO, 220 ],
    "OP2:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, 310 ],
    "OP2:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, 25, -63 ],
    "OP2:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, 130, -18 ],
    "OP2:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, 220, -18 ],
    "OP2:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, 310, -63 ],
    "OP2:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, 130 ],
    "OP2:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, 220 ],
    "OP2:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, 310, -63 ],
    # Switches
    "OP2:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, SWITCH_Y ],
    "OP2:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), SWITCH_Y ],
    "OP2:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), SWITCH_Y ],
    # Sliders
    "OP2:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, LEVEL_SLIDE_Y ],
    "OP2:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, LEVEL_SLIDE_Y ],
    "OP2:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, LEVEL_SLIDE_Y ],
    "OP2:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, LEVEL_SLIDE_Y ],
    "OP2:ATime" :    [ "A Time",    "slideH",    XOFF + 10, TIME_SLIDE_Y ],
    "OP2:DTime" :    [ "D Time",    "slideH",    XOFF + 180, TIME_SLIDE_Y ],
    "OP2:STime" :    [ "S Time",    "slideH",    XOFF + 350, TIME_SLIDE_Y ],
    "OP2:RTime" :    [ "R Time",    "slideH",    XOFF + 520, TIME_SLIDE_Y ],

    # Knobs
    "OP3:Feedback" : [ "Feedback",  "blk128",    COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP3:OP2In" :    [ "OP2 Input", "0to127",    COL_FEEDBACK, YOFF + 130 ],
    "OP3:Output" :   [ "Output",    "0to127",    COL_FEEDBACK, YOFF + 220 ],
    "OP3:VelSens" :  [ "Velo Sens", "0to127",    COL_FEEDBACK, YOFF + 310 ],
    "OP3:Ratio" :    [ "Ratio",     "blk33",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:Freq" :     [ "Frequency", "blk98",     COL_RATIO - 12, YOFF + 10 ],
    "OP3:OP1In" :    [ "OP1 Input", "0to127",    COL_RATIO, YOFF + 130 ],
    "OP3:OP4In" :    [ "OP4 Input", "0to127",    COL_RATIO, YOFF + 220 ],
    "OP3:Level" :    [ "Level",     "0to127",    COL_RATIO, YOFF + 310 ],
    "OP3:Detune" :   [ "Detune",    "_63to63",   COL_DETUNE, YOFF + 25, -63 ],
    "OP3:UpCurve" :  [ "Up Curve",  "_18to18",   COL_DETUNE, YOFF + 130, -18 ],
    "OP3:DnCurve" :  [ "Down Curve","_18to18",   COL_DETUNE, YOFF + 220, -18 ],
    "OP3:RGain" :    [ "R Gain",    "_63to63",   COL_DETUNE, YOFF + 310, -63 ],
    "OP3:Time" :     [ "TimeScale", "0to127",    COL_TIMESCALE, YOFF + 130 ],
    "OP3:Scale" :    [ "Scale Pos", "C1toC7",    COL_TIMESCALE, YOFF + 220 ],
    "OP3:LGain" :    [ "L Gain",    "_63to63",   COL_TIMESCALE, YOFF + 310, -63 ],
    # Switches
    "OP3:LCurve" :   [ "L Curve",   "line_exp",  SWITCH_X, YOFF + SWITCH_Y ],
    "OP3:RCurve" :   [ "R Curve",   "line_exp",  SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:PitchEnv" : [ "Pitch Env",  "on_off",   SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP3:Fixed" :    [ "Fixed",     "on_off",    SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    # Sliders
    "OP3:ALevel" :   [ "A Level",   "slideV",    210, YOFF + LEVEL_SLIDE_Y ],
    "OP3:DLevel" :   [ "D Level",   "slideV",    280, YOFF + LEVEL_SLIDE_Y ],
    "OP3:SLevel" :   [ "S Level",   "slideV",    350, YOFF + LEVEL_SLIDE_Y ],
    "OP3:RLevel" :   [ "R Level",   "slideV",    420, YOFF + LEVEL_SLIDE_Y ],
    "OP3:ATime" :    [ "A Time",    "slideH",    10, YOFF + TIME_SLIDE_Y ],
    "OP3:DTime" :    [ "D Time",    "slideH",    180, YOFF + TIME_SLIDE_Y ],
    "OP3:STime" :    [ "S Time",    "slideH",    350, YOFF + TIME_SLIDE_Y ],
    "OP3:RTime" :    [ "R Time",    "slideH",    520, YOFF + TIME_SLIDE_Y ],

    # Knobs
    "OP4:Feedback" : [ "Feedback",  "blk128",    XOFF + COL_FEEDBACK - 12, YOFF + 10, -63 ],
    "OP4:OP2In" :    [ "OP2 Input", "0to127",    XOFF + COL_FEEDBACK, YOFF + 130 ],
    "OP4:Output" :   [ "Output",    "0to127",    XOFF + COL_FEEDBACK, YOFF + 220 ],
    "OP4:VelSens" :  [ "Velo Sens", "0to127",    XOFF + COL_FEEDBACK, YOFF + 310 ],
    "OP4:Ratio" :    [ "Ratio",     "blk33",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:Freq" :     [ "Frequency", "blk98",     XOFF + COL_RATIO - 12, YOFF + 10 ],
    "OP4:OP1In" :    [ "OP1 Input", "0to127",    XOFF + COL_RATIO, YOFF + 130 ],
    "OP4:OP3In" :    [ "OP3 Input", "0to127",    XOFF + COL_RATIO, YOFF + 220 ],
    "OP4:Level" :    [ "Level",     "0to127",    XOFF + COL_RATIO, YOFF + 310 ],
    "OP4:Detune" :   [ "Detune",    "_63to63",   XOFF + COL_DETUNE, YOFF + 25, -63 ],
    "OP4:UpCurve" :  [ "Up Curve",  "_18to18",   XOFF + COL_DETUNE, YOFF + 130, -18 ],
    "OP4:DnCurve" :  [ "Down Curve","_18to18",   XOFF + COL_DETUNE, YOFF + 220, -18 ],
    "OP4:RGain" :    [ "R Gain",    "_63to63",   XOFF + COL_DETUNE, YOFF + 310, -63 ],
    "OP4:Time" :     [ "TimeScale", "0to127",    XOFF + COL_TIMESCALE, YOFF + 130 ],
    "OP4:Scale" :    [ "Scale Pos", "C1toC7",    XOFF + COL_TIMESCALE, YOFF + 220 ],
    "OP4:LGain" :    [ "L Gain",    "_63to63",   XOFF + COL_TIMESCALE, YOFF + 310, -63 ],
    # Switches
    "OP4:LCurve" :   [ "L Curve",   "line_exp",  XOFF + SWITCH_X, YOFF + SWITCH_Y ],
    "OP4:RCurve" :   [ "R Curve",   "line_exp",  XOFF + SWITCH_X + (1 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:PitchEnv" : [ "Pitch Env",  "on_off",   XOFF + SWITCH_X + (2 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    "OP4:Fixed" :    [ "Fixed",     "on_off",    XOFF + SWITCH_X + (3 * SWITCH_OFFX), YOFF + SWITCH_Y ],
    # Sliders
    "OP4:ALevel" :   [ "A Level",   "slideV",    XOFF + 210, YOFF + LEVEL_SLIDE_Y ],
    "OP4:DLevel" :   [ "D Level",   "slideV",    XOFF + 280, YOFF + LEVEL_SLIDE_Y ],
    "OP4:SLevel" :   [ "S Level",   "slideV",    XOFF + 350, YOFF + LEVEL_SLIDE_Y ],
    "OP4:RLevel" :   [ "R Level",   "slideV",    XOFF + 420, YOFF + LEVEL_SLIDE_Y ],
    "OP4:ATime" :    [ "A Time",    "slideH",    XOFF + 10, YOFF + TIME_SLIDE_Y ],
    "OP4:DTime" :    [ "D Time",    "slideH",    XOFF + 180, YOFF + TIME_SLIDE_Y ],
    "OP4:STime" :    [ "S Time",    "slideH",    XOFF + 350, YOFF + TIME_SLIDE_Y ],
    "OP4:RTime" :    [ "R Time",    "slideH",    XOFF + 520, YOFF + TIME_SLIDE_Y ],


    "Name:chr0" :    [ "",          "chars",   1430, 10 ],
    "Name:chr1" :    [ "",          "chars",   1430 + 64 - 11, 10 ],
    "Name:chr2" :    [ "",          "chars",   1430 + ((64 - 11) * 2), 10 ],
    "Name:chr3":     [ "",          "chars",   1430 + ((64 - 11) * 3), 10 ],
    "Pitch:ATime" :  [ "A Time",    "slideH",    1410, 410 ],
    "Pitch:DTime" :  [ "D Time",    "slideH",    1410, 460 ],
    "Pitch:STime" :  [ "S Time",    "slideH",    1410, 510 ],
    "Pitch:RTime" :  [ "R Time",    "slideH",    1410, 560 ],
    "Pitch:ALevel" : [ "A Level",   "slideVbi",    1410, 90, -48 ],
    "Pitch:DLevel" : [ "D Level",   "slideVbi",    1480, 90, -48 ],
    "Pitch:SLevel" : [ "S Level",   "slideVbi",    1550, 90, -48 ],
    "Pitch:RLevel" : [ "R Level",   "slideVbi",    1620, 90, -48 ],
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
    with open("mypatch.json") as f:
        data = json.load(f)

        for i in data:
            print("=====", i, "=====")
            if (i != "Name"):
                for j in data[i]:
                    key = f'{i}:{j}'
                    print(f'{key} = ', data[i][j])
                    controllist[key][0].setValue(data[i][j])
                    controllist[key][0].draw()
            else:
                for n in range(4):
                    key = f'{i}:chr{n}'
                    print(f'{key} = ', data[i][n])
                    controllist[key][0].setValue(ord(data[i][n]))
                    controllist[key][0].draw()
            for j in ['OP1:', 'OP2:', 'OP3:', 'OP4:', 'Pitch:']:
                adsrs[j].draw()

load = Canvas(width=32, height=32, highlightthickness=0)
load.place(x=1650, y=450)
load.create_rectangle(0,0, 31, 31, fill='#C00000')
load.create_text(0, 0, anchor=tk.NW, text="JSON\ntest", fill='#FFFFFF')
load.bind('<Button>', loadJSON)


# set all the non-0 init values into controls as if an "init" patch
controllist["OP1:ALevel"][0].setValue(127)
controllist["OP1:DLevel"][0].setValue(127)
controllist["OP1:SLevel"][0].setValue(127)
controllist["OP2:ALevel"][0].setValue(127)
controllist["OP2:DLevel"][0].setValue(127)
controllist["OP2:SLevel"][0].setValue(127)
controllist["OP3:ALevel"][0].setValue(127)
controllist["OP3:DLevel"][0].setValue(127)
controllist["OP3:SLevel"][0].setValue(127)
controllist["OP4:ALevel"][0].setValue(127)
controllist["OP4:DLevel"][0].setValue(127)
controllist["OP4:SLevel"][0].setValue(127)
adsrs["OP1:"].init()
adsrs["OP2:"].init()
adsrs["OP3:"].init()
adsrs["OP4:"].init()
controllist["Pitch:ALevel"][0].setValue(0)
controllist["Pitch:DLevel"][0].setValue(0)
controllist["Pitch:SLevel"][0].setValue(0)
controllist["Pitch:RLevel"][0].setValue(0)
adsrs["Pitch:"].draw()
controllist["OP1:Output"][0].setValue(127)
controllist["OP1:Level"][0].setValue(0)
controllist["OP2:Level"][0].setValue(0)
controllist["OP3:Level"][0].setValue(0)
controllist["OP4:Level"][0].setValue(0)
controllist["OP1:Feedback"][0].setValue(0)
controllist["OP2:Feedback"][0].setValue(0)
controllist["OP3:Feedback"][0].setValue(0)
controllist["OP4:Feedback"][0].setValue(0)
controllist["OP1:Ratio"][0].setValue(1)
controllist["OP2:Ratio"][0].setValue(1)
controllist["OP3:Ratio"][0].setValue(1)
controllist["OP4:Ratio"][0].setValue(1)
controllist["Mixer:Level"][0].setValue(63)
controllist["OP1:Detune"][0].setValue(0)
controllist["OP2:Detune"][0].setValue(0)
controllist["OP3:Detune"][0].setValue(0)
controllist["OP4:Detune"][0].setValue(0)
controllist["OP1:UpCurve"][0].setValue(0)
controllist["OP2:UpCurve"][0].setValue(0)
controllist["OP3:UpCurve"][0].setValue(0)
controllist["OP4:UpCurve"][0].setValue(0)
controllist["OP1:DnCurve"][0].setValue(0)
controllist["OP2:DnCurve"][0].setValue(0)
controllist["OP3:DnCurve"][0].setValue(0)
controllist["OP4:DnCurve"][0].setValue(0)
controllist["OP1:Scale"][0].setValue(3)
controllist["OP2:Scale"][0].setValue(3)
controllist["OP3:Scale"][0].setValue(3)
controllist["OP4:Scale"][0].setValue(3)
controllist["Name:chr0"][0].setValue(18)  #'I'
controllist["Name:chr1"][0].setValue(23)  #'N'
controllist["Name:chr2"][0].setValue(18)  #'I'
controllist["Name:chr3"][0].setValue(29)  #'T'
controllist["OP1:LGain"][0].setValue(0)
controllist["OP2:LGain"][0].setValue(0)
controllist["OP3:LGain"][0].setValue(0)
controllist["OP4:LGain"][0].setValue(0)
controllist["OP1:RGain"][0].setValue(0)
controllist["OP2:RGain"][0].setValue(0)
controllist["OP3:RGain"][0].setValue(0)
controllist["OP4:RGain"][0].setValue(0)

# Now init values are set run throught the list and draw all animated controls
for entry in controllist:
    controllist[entry][0].draw()

inports = mido.get_input_names()
if len(inports):
    print("MIDI ports:", inports)

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

window.mainloop()
