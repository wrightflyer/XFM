import keyboard
import mido
import json

inports = mido.get_input_names()
print(inports)

#sysex data=(0,72,4,0,0,3,96,2,4,70,77,84,67
def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = {}
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
        patch['Op1']['name'] = txt
        patch['Op1']['feedback'] = bytes[0x45]
        patch['Op1']['OP2 input'] = bytes[0xAF]
        patch['Op1']['OP3 input'] = bytes[0xB0]
        patch['Op1']['OP4 input'] = bytes[0xB2]
        patch['Op1']['Output to Mixer'] = bytes[0xC0]
        peq = True if bytes[0xCE] == 1 else False
        fixed = True if bytes[0x4A] == 1 else False
        patch['Op1']['Fixed='] = fixed
        ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
        patch['Op1']['Ratio/Fixed'] = ratio
        patch['Op1']['Detune'] = bytes[0x5F]
        patch['Op1']['Level'] = bytes[0x5E]
        patch['Op1']['Velocity Sensitivity'] = bytes[0xC5]
        patch['Op1']['Timescale'] = bytes[0xCA]
        patch['Op1']['Up Curve'] = bytes[0xD3]
        patch['Op1']['Down Curve'] = bytes[0xD4]
        patch['Op1']['ScalePos (C4=3)'] = bytes[0x9F]
        patch['Op1']['A level '] = bytes[0x73]
        patch['Op1']['A time '] = bytes[0x6E]
        patch['Op1']['D level '] = bytes[0x74]
        patch['Op1']['D time '] = bytes[0x6F]
        patch['Op1']['S level '] = bytes[0x75]
        patch['Op1']['S time '] = bytes[0x70]
        patch['Op1']['R level '] = bytes[0x76]
        patch['Op1']['R time '] = bytes[0x72]
        patch['Op1']['L gain '] = bytes[0x9C]
        patch['Op1']['R gain '] = bytes[0x9D]
        patch['Op1']['L curve'] = "Line" if bytes[0x9E] & 0x01 else "Exp"
        patch['Op1']['R curve'] = "Line" if bytes[0x9E] & 0x10 else "Exp"
        print("Operator 1")
        print(json.dumps(patch, indent=4))

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

