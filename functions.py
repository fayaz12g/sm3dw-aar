import struct
import keystone
from keystone import *
import binascii
import math
import os

def make_hex(x, r):
    p = math.floor(math.log(x, 2))
    a = round(16*(p-2) + x / 2**(p-4))
    if a<0: a += 128
    a = 2*a + 1
    h = hex(a).lstrip('0x').rjust(2,'0').upper()
    hex_value = f'0{r}' + h[1] + '02' + h[0] + '1E' 
    print(hex_value)
    return hex_value

def asm_to_hex(asm_code):
    ks = Ks(KS_ARCH_ARM64, KS_MODE_LITTLE_ENDIAN)
    encoding, count = ks.asm(asm_code)
    return ''.join('{:02x}'.format(x) for x in encoding)

def make_specials(num):
    num = round(num, 15)
    packed = struct.pack('!f', num)
    full_hex = ''.join('{:02x}'.format(b) for b in packed)
    hex_1 = full_hex[:4]
    hex_2 = full_hex[4:]
    return hex_1, hex_2

def calculate_rounded_ratio(ratio_value):
    if ratio_value <= 2:
        rounded_ratio = round(ratio_value * 16) / 16
    elif ratio_value > 2 and ratio_value <= 4:
        rounded_ratio = round(ratio_value * 8) / 8
    else:
        rounded_ratio = round(ratio_value * 4) / 4
    return rounded_ratio