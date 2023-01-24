# XFM
## Sysex viewer/editor for Liven XFM

So this is intended to be a patch editor for XFM. As users will know the on-board editing in XFM, with the overlay, is quite a convoluted process because your only view of what is going on is through that four character 14-segment display so you can't "picture" the ADSR wave shapes or anything like that and you can only see the set value of **one** control at a time.

The plan with this Python utility is to be able to see everything at once, as "visually" as possible. The aim is also that the interface to XFM itself be as seemless as possible. It's true that you will have to manually trigger a patch to be sent from XFM to the PC/editor but once in the editor, as changes are made they should be automatically sent back.

BUT STOP RIGHT THERE - so here is the current "problem" with this editor and the reason it's not "released" yet. When XFM sends a patch it sends three sysex messages. One is just a preamble, then there is the main body of the patch in the middle message, then finally the third message is some kind of CRC/hash to validate the data. This is fine if all you were doing is sending patches to a PC to be stored "as is" without changing them. You could then send the three messages back when you wanted to restore that patch. But if, while the patch is on the PC, you EDIT it then when you come to send it back the XFM will say "the payload does not match the CRC". What it actually says is "D.ERR" on the 4 characters. So, for an editor to work, it either needs to recalculate the hash/checksum after changes or it needs an XFM that does not insist on a checksum. I've spoken to Sonicware about this. They couldn't give me the re-calculation algo but they have promised that XFM firmware will be updated to make it easier to upload changed patches. Until then this program is really just a *viewer* to see how patches saved out of XFM are constructed.

So on to the development...

### Graphics

The first thing I did was a simple Python program, adsr.py, (I like the simplicity of Tkinter for graphics) to run some experiments in drawing 8 point ADSR envelopes...

![](readme_pics/pretty.png)

This was just playing about to understand how to visually represent 8 parameter envelopes as used by XFM.

### MIDI in Python

I also did experiments to read Sysex from XFM (rx_syx.py). I spent some time researching how you could interface to MIDI from inside a Python program. The library I ended up with is "MIDO" but this is really just a high level interface that then relies on a lower level, back end to connect to "ports" and in this case that is RT_MIDI. With mido you can just mido.get_input_names() to find the MIDI ports available and mido.open() one and register callback=function and then that function is called with a message each time something arrives on the port. I wrote some code to then hex/ASCII dump the 230+ bytes of the main patch message

![](readme_pics/sysex_dump.png)

At the start I had no idea what any of the bytes of this data controlled. It's not documented anywhere and Sonicware were too busy working on things like LoFi12 and SmplTrek to take time out to produce a document. So a lot (an awful lot!!) of the work in this project was capturing 100's if not 1000's of Sysex dumps like this picture. Each time I would make some small control adjustment and see what bit/bytes changed. The complexity of the layout of the data is simply incredible. I sort of assumed it would be a C struct and one localized element might change for a control adjustment but for some things the bytes are split all over the place. This is especially true for controls that don't have a simple 7bit (MIDI sized!) value holding 0..127. For things like Frequency/Ratio/Feedback you will not believe how complex the storage of the values is !! But to get a flavour...
```
    if offset == 0:
        freq = ((bytes[offset + 0x4D] * 65536) + (bytes[offset + 0x4C] * 256) + bytes[offset + 0x4B])
        if bytes[offset + 0x49] & 0x20:
            freq = freq + 128
        if bytes[offset + 0x49] & 0x10:
            freq = freq + 32768
    else:
        freq = ((bytes[offset + 0x4D] * 65536) + (bytes[offset + 0x4B] * 256) + bytes[offset + 0x4A])
        if bytes[offset + 0x44] & 0x02:
            freq = freq + 128
        if bytes[offset + 0x44] & 0x01:
            freq = freq + 32768
    print("op1 freq = ", freq)
```

### Graphics / Animations

I love playing with knobs!

I also wanted to prototype the "look" of the program before I had any way to draw animated knobs in Python. So I reverted to my old friend Ctrlr which is a GUI program for making MIDI control panels. I was just interested in laying out controls more than anything. Now with Ctrlr it has a default "look and feel" as seen in this control panel I actually used for my own design Teensy4 based synth:

![](readme_pics/synthctrlr.png)

But I wanted to use my own knob design. Reading around I found that some users of Ctrlr used a dedicated knob design program called Knobman because Ctrlr can have an animation file attached to a control that is then used to draw each step of the control:

[Knobman](https://www.g200kg.com/jp/software/knobman.html)

There's Windows specific versions, Java versions and even an online based editor - I ended up using all 3 because each had specific things only they could do (like my "LCD like" font could only be used in Windows!). As well as the tools there is a gallery of knob designs from other people:

[Knobman Gallery](https://www.g200kg.com/en/webknobman/gallery.php)

It's slow to load but worth the wait as there's tons of knob designs there to choose from (or you can draw from scratch if you want). I ended up with a bit of both. Now I actually like the look of a knob like:

![](readme_pics/original_knob.png)

It had a "3D" look but I didn't like the red/white scale or the red pointer. I also noticed when I was editing on the XFM with the editing overlay in place that because the holes for the knobs were a bit bigger then the knobs themselves a "blue halo" would show through so I used knobman to create my own knob design that has subtle "ticks" in white to show scale but then a blue halo that grows as the knob is turned.

Another requirement I had (apart from the blue halo) was a way to instantly read the value of every control. So I searched and searched and found a Truetype LCD font that was very like the characters in the XFM display. So I overlaid this on the rotary controls so they would show the value of the reading. In the end the editing looked like:

![](readme_pics/knobman_editor.png)

Knobman basically takes all the design elements of the knob (some of which vary from frame to frame - like the angle of the white mark, the blue halo and the LCD printed value) and then it creates either animated GIFs or animated PNG files with every frame in it. I already knew about animated GIF but didn't know about animated PNG. In the latter it basically draws each frame either side-by-side or on top of one another. The nice thing about that is that if you want to do your own animator it's just a case in a file that is w x N*h to cut out the rectangle from (0, h * N1) to (w, h * N2) and drawing that. As many of the controls have a 0..127 range they are effectively 128 small rectangles on top of one another. The code directory is full of such PNG animations like:

![](example_anim.png)

(that is just -18 to +18 so 37 steps but many are 128 small pictures!)

So anyway, having created PNG animations it was possible to initially prototype the look of the layout (complete with operational / animated knobs) in Ctrlr so it looked like:

![](readme_pics/ctrlr_layout.png)

(the one thing I could not fake "inside" controller were my dynamic ADSR curves so in this they are just static images as "placeholders").

Having seen how this would look in Ctrlr I then set about presenting an almost identical look and feel from actual Python code which basically involved writing an animation engine to be able to display one of many (often 128) small images in one location pulled out of an animated PNG file and to then add mouse support so that mouse events would be reported back into the "control" and allow its value to be adjusted. The UI of the program would then involve laying out about 100+ such controls and having code to load values into the controls when a MIDI Sysex patch arrives or to read the values back out if they were to be sent out by MIDI.

As I wanted to be able to save/restore edited patches to disk I actually hold the values of every control in an associated array (dictionary) and once you have it in that it's trivial to save/load to JSON.

### The final Python program

So all the foregoing were just prototyping experiments (it's a good way to approach software design in fact). So I had python code that proved I could draw dynamically changeable ADSR curves. I had code that could do MIDI interactions with XFM. I spent 10's and 10's of hours doing reverse engineering on the patch format (oh and something I bet no one else knows - if you change a patch name to include a "." (1..4 of them) then the patch dump gets 5 bytes longer and the location of about half the things in it change (sadly not everything!). So I actually had to do the reverse engineer of everything TWICE - once for 4 character names and one for 4 character + dot names!). I had designed all the animated graphics and I wrote a Python program using nothing but Tkinter to be able to draw any given animation frame. I then added "mouse awareness" to that so that the animations were "hot" and you could adjust them by dragging the mouse over them.

So finally it came time to put all these experiments together in one big program and I ended up with this...

![](knobman.png)

Having watched one of Chris ("Lody") Dodsworth's excellent Sonicware videos I was inspired by a sketch he drew trying to explain XFM signal routing...

![](readme_pics/route_inspiration.png)

to implement a feature so that when "Route" is pressed on the main editor this secondary window will be toggled on. It shows the signal routing between each operator (density of line indicates strength of signal). Signal shape is shown - when feedback is close to 0 it is "sine", when large positive (but not 63..64) it is sawtooth, when positive 63..64 it is noise, when large negative it is square...

![](readme_pics/route.png)

### Running / Using the code

So it's a Python program which means that to be able to run it you need to have Python installed. It does not work with the now dead Python 2.7. It has to be some flavour of 3.x (a later one!)

Because I tried to stick with lib code that comes with Python (like Tkinter for the GUI graphics) there's not much else you need to install to run it. The main thing is going to be the libs for MIDI support. So you probably need:

    pip install mido
    pip install python-rtmidi

The latter is the lower level support (RTmidi) that allows Mido to open and interact with the MIDI ports on the machine.

If it's not installed already you will also need

    pip install pillow

While writing these words I also found that I used a feature in PIL (Pillow - part of Python's image handling) that is only available in a fairly recent Pillow (> v9.x) and that such a late version of PIL is only compatible with later versions of Python (3.9, 3.10, 3.11) so if you have an earlier 3.6 (say) you may need to upgrade and if "pip list" shows your Pillow is an older version before V9 you may need to do a pip upgrade of that wheel too.

To execute the program

    python xfm.py

These words aren't finished - I want to say something about how to operate this but that will be in a later update...
