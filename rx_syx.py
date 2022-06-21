import keyboard
import mido
import json

inports = mido.get_input_names()
print(inports)

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

def decode_bytes(bytes, patch):
    txt = ""
    txt += chr(bytes[0x2E])
    txt += chr(bytes[0x2F])
    txt += chr(bytes[0x30])
    txt += chr(bytes[0x32])
    patch['name'] = txt

    patch["OP1"]['feedback'] = bytes[0x45]
    patch["OP1"]['OP2 input'] = bytes[0xAF]
    patch["OP1"]['OP3 input'] = bytes[0xB0]
    patch["OP1"]['OP4 input'] = bytes[0xB2]
    patch["OP1"]['Output to Mixer'] = bytes[0xC0]
    patch["OP1"]['Pitch EQ'] = bytes[0xCE]
    patch["OP1"]['Fixed'] = bytes[0x4A]
    ratio = ((bytes[0x5D] * 256) + bytes[0x5C] )
    patch["OP1"]['Ratio/Fixed'] = ratio
    patch["OP1"]['Detune'] = bytes[0x5F]
    patch["OP1"]['Level'] = bytes[0x5E]
    patch["OP1"]['Velocity Sensitivity'] = bytes[0xC5]
    patch["OP1"]['Timescale'] = bytes[0xCA]
    patch["OP1"]['Up Curve'] = bytes[0xD3]
    patch["OP1"]['Down Curve'] = bytes[0xD4]
    patch["OP1"]['ScalePos'] = bytes[0x9F]
    patch["OP1"]['A level'] = bytes[0x73]
    patch["OP1"]['A time'] = bytes[0x6E]
    patch["OP1"]['D level'] = bytes[0x74]
    patch["OP1"]['D time'] = bytes[0x6F]
    patch["OP1"]['S level'] = bytes[0x75]
    patch["OP1"]['S time'] = bytes[0x70]
    patch["OP1"]['R level'] = bytes[0x76]
    patch["OP1"]['R time'] = bytes[0x72]
    patch["OP1"]['L gain'] = bytes[0x9C]
    patch["OP1"]['R gain'] = bytes[0x9D]
    patch["OP1"]['L curve'] = bytes[0x9E] & 0x01
    patch["OP1"]['R curve'] = bytes[0x9E] & 0x10

    patch["OP2"]['feedback'] = bytes[0x46]
    patch["OP2"]['OP1 input'] = bytes[0xB3]
    patch["OP2"]['OP3 input'] = bytes[0xB5]
    patch["OP2"]['OP4 input'] = bytes[0xB6]
    patch["OP2"]['Output to Mixer'] = bytes[0xC2]
    patch["OP2"]['Pitch EQ'] = bytes[0xCF]
    patch["OP2"]['Fixed'] = bytes[0x4E]
    ratio = ((bytes[0x61] * 256) + bytes[0x60] )
    patch["OP2"]['Ratio/Fixed'] = ratio
    patch["OP2"]['Detune'] = bytes[0x64]
    patch["OP2"]['Level'] = bytes[0x63]
    patch["OP2"]['Velocity Sensitivity'] = bytes[0xC6]
    patch["OP2"]['Timescale'] = bytes[0xCB]
    patch["OP2"]['Up Curve'] = bytes[0xD5]
    patch["OP2"]['Down Curve'] = bytes[0xD6]
    patch["OP2"]['ScalePos'] = bytes[0xA4]
    patch["OP2"]['A level'] = bytes[0x7C]
    patch["OP2"]['A time'] = bytes[0x77]
    patch["OP2"]['D level'] = bytes[0x7D]
    patch["OP2"]['D time'] = bytes[0x78]
    patch["OP2"]['S level'] = bytes[0x7E]
    patch["OP2"]['S time'] = bytes[0x7A]
    patch["OP2"]['R level'] = bytes[0x7F]
    patch["OP2"]['R time'] = bytes[0x7B]
    patch["OP2"]['L gain'] = bytes[0xA0]
    patch["OP2"]['R gain'] = bytes[0xA2]
    patch["OP2"]['L curve'] = bytes[0xA3] & 0x01
    patch["OP2"]['R curve'] = bytes[0xA3] & 0x10

    patch["OP3"]['feedback'] = bytes[0x47]
    patch["OP3"]['OP1 input'] = bytes[0xB7]
    patch["OP3"]['OP2 input'] = bytes[0xB8]
    patch["OP3"]['OP4 input'] = bytes[0xBB]
    patch["OP3"]['Output to Mixer'] = bytes[0xC3]
    patch["OP3"]['Pitch EQ'] = bytes[0xD0]
    patch["OP3"]['Fixed'] = bytes[0x53]
    ratio = ((bytes[0x66] * 256) + bytes[0x65] )
    patch["OP3"]['Ratio/Fixed'] = ratio
    patch["OP3"]['Detune'] = bytes[0x68]
    patch["OP3"]['Level'] = bytes[0x67]
    patch["OP3"]['Velocity Sensitivity'] = bytes[0xC7]
    patch["OP3"]['Timescale'] = bytes[0xCC]
    patch["OP3"]['Up Curve'] = bytes[0xD7]
    patch["OP3"]['Down Curve'] = bytes[0xD8]
    patch["OP3"]['ScalePos'] = bytes[0xA8]
    patch["OP3"]['A level'] = bytes[0x85]
    patch["OP3"]['A time'] = bytes[0x80]
    patch["OP3"]['D level'] = bytes[0x86]
    patch["OP3"]['D time'] = bytes[0x82]
    patch["OP3"]['S level'] = bytes[0x87]
    patch["OP3"]['S time'] = bytes[0x83]
    patch["OP3"]['R level'] = bytes[0x88]
    patch["OP3"]['R time'] = bytes[0x84]
    patch["OP3"]['L gain'] = bytes[0xA5]
    patch["OP3"]['R gain'] = bytes[0xA6]
    patch["OP3"]['L curve'] = bytes[0xA7] & 0x01
    patch["OP3"]['R curve'] = bytes[0xA7] & 0x10

    patch["OP4"]['feedback'] = bytes[0x48]
    patch["OP4"]['OP1 input'] = bytes[0xBC]
    patch["OP4"]['OP2 input'] = bytes[0xBD]
    patch["OP4"]['OP3 input'] = bytes[0xBE]
    patch["OP4"]['Output to Mixer'] = bytes[0xC4]
    patch["OP4"]['Pitch EQ'] = bytes[0xD2]
    patch["OP4"]['Fixed'] = bytes[0x57]
    ratio = ((bytes[0x6B] * 256) + bytes[0x6A] )
    patch["OP4"]['Ratio/Fixed'] = ratio
    patch["OP4"]['Detune'] = bytes[0x6D]
    patch["OP4"]['Level'] = bytes[0x6C]
    patch["OP4"]['Velocity Sensitivity'] = bytes[0xC8]
    patch["OP4"]['Timescale'] = bytes[0xCD]
    patch["OP4"]['Up Curve'] = bytes[0xDA]
    patch["OP4"]['Down Curve'] = bytes[0xDB]
    patch["OP4"]['ScalePos'] = bytes[0xAD]
    patch["OP4"]['A level'] = bytes[0x8E]
    patch["OP4"]['A time'] = bytes[0x8A]
    patch["OP4"]['D level'] = bytes[0x8F]
    patch["OP4"]['D time'] = bytes[0x8B]
    patch["OP4"]['S level'] = bytes[0x90]
    patch["OP4"]['S time'] = bytes[0x8C]
    patch["OP4"]['R level'] = bytes[0x92]
    patch["OP4"]['R time'] = bytes[0x8D]
    patch["OP4"]['L gain'] = bytes[0xAA]
    patch["OP4"]['R gain'] = bytes[0xAB]
    patch["OP4"]['L curve'] = bytes[0xAC] & 0x01
    patch["OP4"]['R curve'] = bytes[0xAC] & 0x10

    patch["Pitch"]['A level'] = bytes[0x97]
    patch["Pitch"]['A time'] = bytes[0x93]
    patch["Pitch"]['D level'] = bytes[0x98]
    patch["Pitch"]['D time'] = bytes[0x94]
    patch["Pitch"]['S level'] = bytes[0x9A]
    patch["Pitch"]['S time'] = bytes[0x95]
    patch["Pitch"]['R level'] = bytes[0x9B]
    patch["Pitch"]['R time'] = bytes[0x96]

    patch["Mixer"]['Level'] = bytes[0xDC]

def encode_bytes(patch, bytes):
    bytes[0x2E] = ord(patch['name'][0])
    bytes[0x2F] = ord(patch['name'][1])
    bytes[0x30] = ord(patch['name'][2])
    bytes[0x32] = ord(patch['name'][3])

    bytes[0x45] = patch["OP1"]['feedback']
    bytes[0xAF] = patch["OP1"]['OP2 input']
    bytes[0xB0] = patch["OP1"]['OP3 input']
    bytes[0xB2] = patch["OP1"]['OP4 input']
    bytes[0xC0] = patch["OP1"]['Output to Mixer']
    bytes[0xCE] = patch["OP1"]['Pitch EQ']
    bytes[0x4A] = patch["OP1"]['Fixed']
    bytes[0x5C] = (patch["OP1"]['Ratio/Fixed']) & 0xFF
    bytes[0x5D] = int((patch["OP1"]['Ratio/Fixed']) / 256)
    bytes[0x5F] = patch["OP1"]['Detune']
    bytes[0x5E] = patch["OP1"]['Level']
    bytes[0xC5] = patch["OP1"]['Velocity Sensitivity']
    bytes[0xCA] = patch["OP1"]['Timescale']
    bytes[0xD3] = patch["OP1"]['Up Curve']
    bytes[0xD4] = patch["OP1"]['Down Curve']
    bytes[0x9F] = patch["OP1"]['ScalePos']
    bytes[0x73] = patch["OP1"]['A level']
    bytes[0x6E] = patch["OP1"]['A time']
    bytes[0x74] = patch["OP1"]['D level']
    bytes[0x6F] = patch["OP1"]['D time']
    bytes[0x75] = patch["OP1"]['S level']
    bytes[0x70] = patch["OP1"]['S time']
    bytes[0x76] = patch["OP1"]['R level']
    bytes[0x72] = patch["OP1"]['R time']
    bytes[0x9C] = patch["OP1"]['L gain']
    bytes[0x9D] = patch["OP1"]['R gain']
    curves = (patch["OP1"]['L curve']) | (patch["OP1"]['R curve'])
    bytes[0x9E] = curves

    bytes[0x46] = patch["OP2"]['feedback']
    bytes[0xB3] = patch["OP2"]['OP1 input']
    bytes[0xB5] = patch["OP2"]['OP3 input']
    bytes[0xB6] = patch["OP2"]['OP4 input']
    bytes[0xC2] = patch["OP2"]['Output to Mixer']
    bytes[0xCF] = patch["OP2"]['Pitch EQ']
    bytes[0x4E] = patch["OP2"]['Fixed']
    bytes[0x60] = (patch["OP2"]['Ratio/Fixed']) & 0xFF
    bytes[0x61] = int((patch["OP2"]['Ratio/Fixed']) / 256)
    bytes[0x64] = patch["OP2"]['Detune']
    bytes[0x63] = patch["OP2"]['Level']
    bytes[0xC6] = patch["OP2"]['Velocity Sensitivity']
    bytes[0xCB] = patch["OP2"]['Timescale']
    bytes[0xD5] = patch["OP2"]['Up Curve']
    bytes[0xD6] = patch["OP2"]['Down Curve']
    bytes[0xA4] = patch["OP2"]['ScalePos']
    bytes[0x7C] = patch["OP2"]['A level']
    bytes[0x77] = patch["OP2"]['A time']
    bytes[0x7D] = patch["OP2"]['D level']
    bytes[0x78] = patch["OP2"]['D time']
    bytes[0x7E] = patch["OP2"]['S level']
    bytes[0x7A] = patch["OP2"]['S time']
    bytes[0x7F] = patch["OP2"]['R level']
    bytes[0x7B] = patch["OP2"]['R time']
    bytes[0xA0] = patch["OP2"]['L gain']
    bytes[0xA2] = patch["OP2"]['R gain']
    curves = (patch["OP2"]['L curve']) | (patch["OP2"]['R curve'])
    bytes[0xA3] = curves

    bytes[0x47] = patch["OP3"]['feedback']
    bytes[0xB7] = patch["OP3"]['OP1 input']
    bytes[0xB8] = patch["OP3"]['OP2 input']
    bytes[0xBB] = patch["OP3"]['OP4 input']
    bytes[0xC3] = patch["OP3"]['Output to Mixer']
    bytes[0xD0] = patch["OP3"]['Pitch EQ']
    bytes[0x53] = patch["OP3"]['Fixed']
    bytes[0x65] = (patch["OP3"]['Ratio/Fixed']) & 0xFF
    bytes[0x66] = int((patch["OP3"]['Ratio/Fixed']) / 256)
    bytes[0x68] = patch["OP3"]['Detune']
    bytes[0x67] = patch["OP3"]['Level']
    bytes[0xC7] = patch["OP3"]['Velocity Sensitivity']
    bytes[0xCC] = patch["OP3"]['Timescale']
    bytes[0xD7] = patch["OP3"]['Up Curve']
    bytes[0xD8] = patch["OP3"]['Down Curve']
    bytes[0xA8] = patch["OP3"]['ScalePos']
    bytes[0x85] = patch["OP3"]['A level']
    bytes[0x80] = patch["OP3"]['A time']
    bytes[0x86] = patch["OP3"]['D level']
    bytes[0x82] = patch["OP3"]['D time']
    bytes[0x87] = patch["OP3"]['S level']
    bytes[0x83] = patch["OP3"]['S time']
    bytes[0x88] = patch["OP3"]['R level']
    bytes[0x84] = patch["OP3"]['R time']
    bytes[0xA5] = patch["OP3"]['L gain']
    bytes[0xA6] = patch["OP3"]['R gain']
    curves = (patch["OP3"]['L curve']) | (patch["OP3"]['R curve'])
    bytes[0xA7] = curves

    bytes[0x48] = patch["OP4"]['feedback']
    bytes[0xBC] = patch["OP4"]['OP1 input']
    bytes[0xBD] = patch["OP4"]['OP2 input']
    bytes[0xBE] = patch["OP4"]['OP3 input']
    bytes[0xC4] = patch["OP4"]['Output to Mixer']
    bytes[0xD2] = patch["OP4"]['Pitch EQ']
    bytes[0x57] = patch["OP4"]['Fixed']
    bytes[0x6A] = (patch["OP4"]['Ratio/Fixed']) & 0xFF
    bytes[0x6B] = int((patch["OP4"]['Ratio/Fixed']) / 256)
    bytes[0x6D] = patch["OP4"]['Detune']
    bytes[0x6C] = patch["OP4"]['Level']
    bytes[0xC8] = patch["OP4"]['Velocity Sensitivity']
    bytes[0xCD] = patch["OP4"]['Timescale']
    bytes[0xDA] = patch["OP4"]['Up Curve']
    bytes[0xDB] = patch["OP4"]['Down Curve']
    bytes[0xAD] = patch["OP4"]['ScalePos']
    bytes[0x8E] = patch["OP4"]['A level']
    bytes[0x8A] = patch["OP4"]['A time']
    bytes[0x8F] = patch["OP4"]['D level']
    bytes[0x8B] = patch["OP4"]['D time']
    bytes[0x90] = patch["OP4"]['S level']
    bytes[0x8C] = patch["OP4"]['S time']
    bytes[0x92] = patch["OP4"]['R level']
    bytes[0x8D] = patch["OP4"]['R time']
    bytes[0xAA] = patch["OP4"]['L gain']
    bytes[0xAB] = patch["OP4"]['R gain']
    curves = (patch["OP4"]['L curve']) | (patch["OP4"]['R curve'])
    bytes[0xAC] = curves

    bytes[0x97] = patch["Pitch"]['A level']
    bytes[0x93] = patch["Pitch"]['A time']
    bytes[0x98] = patch["Pitch"]['D level']
    bytes[0x94] = patch["Pitch"]['D time']
    bytes[0x9A] = patch["Pitch"]['S level']
    bytes[0x95] = patch["Pitch"]['S time']
    bytes[0x9B] = patch["Pitch"]['R level']
    bytes[0x96] = patch["Pitch"]['R time']

    bytes[0xDC] = patch["Mixer"]['Level']

def rxmsg(msg):
    #print("type=", msg.type, "byte5=", msg.bytes()[8])
    # sound dump comes in 3 messages - look for the middle one with sequence number 2 (from 1, 2, 3)
    if msg.type == 'sysex' and msg.bytes()[8] == 2:
        patch = { "name" : "LOAD", "Pitch" : {}, "OP1" : {}, "OP2" : {}, "OP3" : {}, "OP4" : {}, "Mixer" : {}}
        bytes = msg.bytes()

        print_dump(bytes)

        decode_bytes(bytes, patch)

        print(json.dumps(patch, indent=4))
        
        newbytes = [0 for _ in range(0xE0)]
        encode_bytes(patch, newbytes)
        print_dump(newbytes)

if (len(inports) > 1):
    port = mido.open_input(inports[1], callback=rxmsg)

while True:
    if keyboard.is_pressed("q"):
        break
    pass

port.close()

