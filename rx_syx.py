import keyboard
import mido

inports = mido.get_input_names()
print(inports)

#sysex data=(0,72,4,0,0,3,96,2,4,70,77,84,67
def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        bytes = msg.bytes()
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
        txt = ""
        txt += bytes[0x2E]
        txt += bytes[0x2F]
        txt += bytes[0x30]
        txt += bytes[0x32]
        print("Patch name:", txt)
        print("Operator 1")
        print("Feedback =", bytes[0x45])
        print("OP2 -> OP1=", bytes[0xAF])
        print("OP3 -> OP1=", bytes[0xB0])
        print("OP4 -> OP1=", bytes[0xB2])
        print("Output to Mixer=", bytes[0xC0])
        peq = True if bytes[0xCE] == 1 else False
        fixed = True if bytes[0x4A] == 1 else False
        print("Fixed=", fixed)
        ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
        if fixed:
            print("Fixed Frequency =", ratio, "Hz")
        else:
            print("Ratio=", ratio / 100)
        print("Detune=", bytes[0x5F])
        print("Level=", bytes[0x5E])
        print("Velocity Sensitivity=", bytes[0xC5])
        print("Timescale=", bytes[0xCA])
        print("Up Curve=", bytes[0xD3])
        print("Down Curve=", bytes[0xD4])
        print("ScalePos (C4=3)=", bytes[0x9F])
        print("A level =", bytes[0x73])
        print("A time =", bytes[0x6E])
        print("D level =", bytes[0x74])
        print("D time =", bytes[0x6F])
        print("S level =", bytes[0x75])
        print("S time =", bytes[0x70])
        print("R level =", bytes[0x76])
        print("R time =", bytes[0x72])
        print("L gain =", bytes[0x9C])
        print("R gain =", bytes[0x9D])
        if bytes[0x9E] & 0x01:
            print("Left Exp")
        else:
            print("Left Line")
        if bytes[0x9E] & 0x10:
            print("Right Exp")
        else:
            print("Right Line")


if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

