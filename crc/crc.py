#/* Untitled1 (26/01/2023 20:15:33)
#   StartOffset(h): 00000000, EndOffset(h): 000000D6, Length(h): 000000D7 */

import zlib

def crc32(crc, p, len):
  crc = 0xffffffff & ~crc
  for i in range(len):
    crc = crc ^ p[i]
    for j in range(8):
      crc = (crc >> 1) ^ (0xedb88320 & -(crc & 1))
  return 0xffffffff & ~crc


input_list = [
	0x04, 0x46, 0x4D, 0x54, 0x43, 0x3C, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x02, 0x00, 0x00, 0x00, 0x00, 0x46, 0x4D, 0x4E, 0x4D, 0x14,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x04, 0x00, 0x00,
	0x00, 0x57, 0x47, 0x47, 0x02, 0x4C, 0x54, 0x50, 0x44, 0x54, 0x18, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x32, 0x11, 0x00, 0x00, 0x32, 0x11,
	0x00, 0x00, 0x00, 0x32, 0x11, 0x00, 0x01, 0x3A, 0x02, 0x00, 0x00, 0x64,
	0x00, 0x3F, 0x7F, 0x4B, 0x00, 0x00, 0x3F, 0x01, 0x32, 0x00, 0x3F, 0x00,
	0x00, 0x64, 0x00, 0x3F, 0x00, 0x29, 0x00, 0x41, 0x00, 0x30, 0x7F, 0x7F,
	0x5A, 0x00, 0x2A, 0x00, 0x00, 0x4B, 0x00, 0x7F, 0x7F, 0x37, 0x00, 0x2C,
	0x00, 0x7A, 0x51, 0x30, 0x7F, 0x7F, 0x37, 0x00, 0x00, 0x4D, 0x34, 0x4D,
	0x30, 0x7F, 0x59, 0x28, 0x00, 0x00, 0x21, 0x00, 0x5F, 0x00, 0x00, 0x00,
	0x40, 0x6E, 0x00, 0x00, 0x00, 0x00, 0x03, 0x00, 0x04, 0x00, 0x00, 0x05,
	0x00, 0x60, 0x00, 0x05, 0x40, 0x50, 0x3F, 0x00, 0x03, 0x1E, 0x00, 0x4A,
	0x00, 0x42, 0x00, 0x37, 0x3C, 0x3F, 0x00, 0x00, 0x00, 0x37, 0x32, 0x00,
	0x00, 0x00, 0x00, 0x7F, 0x00, 0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0x00, 0x00,
	0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00
]

def crc32_2(msg):
    crc = 0x00000000
    for b in msg:
        crc ^= b
        for _ in range(8):
            crc = (crc >> 1) ^ 0xedb88320 if crc & 1 else crc >> 1
    return crc ^ 0xffffffff

def reverse_Bits(n, no_of_bits):
    result = 0
    for i in range(no_of_bits):
        result <<= 1
        result |= n & 1
        n >>= 1
    return result

def create_table():
    a = []
    for i in range(256):
        k = i << 24;
        for _ in range(8):
            k = (k << 1) ^ 0x4c11db7 if k & 0x80000000 else k << 1
        a.append(k & 0xffffffff)
    return a

def crc32_tbl(bytestream):
    crc_table = create_table()
    crc = 0
    for byte in bytestream:
        lookup_index = ((crc >> 24) ^ byte) & 0xff
        crc = ((crc & 0xffffff) << 8) ^ crc_table[lookup_index]
    return crc

input_bytes = bytes(input_list)

print("aiming for 0x2174604F or maybe 0x4F607421 (from packet 3!)")
print()

print("zlib", hex(zlib.crc32(input_bytes)), "inverted", hex(0xFFFFFFFF ^ zlib.crc32(input_bytes)))

crc = crc32(0, input_list, 215)
print("crc = ", hex(crc), "inverted", hex(0xFFFFFFFF ^ crc), end="")
print("  reversed", hex(reverse_Bits(crc, 32)), "inverted", hex(0xFFFFFFFF ^ reverse_Bits(crc, 32)))

crc = crc32_2(input_bytes)
print("rev function = ", hex(crc), "inverted", hex(0xFFFFFFFF ^ crc), end="")
print("  reversed", hex(reverse_Bits(crc, 32)), "rev/inverted", hex(0xFFFFFFFF ^ reverse_Bits(crc, 32)))

crc = crc32_tbl(input_bytes)
print("table function = ", hex(crc), "inverted", hex(0xFFFFFFFF ^ crc), end="")
print("  reversed", hex(reverse_Bits(crc, 32)), "rev/inverted", hex(0xFFFFFFFF ^ reverse_Bits(crc, 32)))