from tkinter import *
from PIL import Image, ImageTk

win = Tk()

img = Image.open("stipple256.png").convert('1')

for n in range(256):
    tup = (0, 32 * n, 32, 32 * (n + 1))
    frame = img.crop(tup)
    outname = "stip"
    outname = outname + str(n) + ".xbm"
    frame.save(outname, "XBM")
