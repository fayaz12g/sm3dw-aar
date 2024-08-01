import os
import math
from functions import *

def create_patch_files(patch_folder, ratio_value, scaling_factor, visual_fixes):
    visual_fixesa = visual_fixes[0]
    visual_fixesb = visual_fixes[1]
    scaling_factor = float(scaling_factor)
    ratio_value = float(ratio_value)
    ratio_value += (abs(ratio_value - (16/9)) / 2)
    print(f"The scaling factor is {scaling_factor}.")
    hex_value = make_hex(ratio_value, 0)
    hex_value2 = make_hex(ratio_value, 3)
    rounded_ratio = calculate_rounded_ratio(ratio_value)
    special_hex1, special_hex2 = make_specials(ratio_value)
    version_variables = ["1.0.0", "1.1.0"]
    for version_variable in version_variables:
        file_name = f"main-{version_variable}.pchtxt"
        file_path = os.path.join(patch_folder, file_name)

        if version_variable == "1.0.0":
            nsobidid = "9F7EFC2FB9653E5CDE03030478F23EDA7D18EF44"
            replacement_value = "008FADE0"
            replacement2_value = "009692D0"
            visual_fix = visual_fixesa
            fixes = f'''{replacement_value} {hex_value}
{replacement2_value} {hex_value2}
0091CFC8 A9AA8AD2
0091CFCC A902A8F2
008B6C1C A8AA8A52
008B6C20 A802A872'''

        elif version_variable == "1.1.0":
            nsobidid = "891687F016A18F1773D4A88EBF8A973C8E33ECC1"
            visual_fix = visual_fixesb
            fixes = f'''00901638 {asm_to_hex(f'movz w28, #0x{special_hex2}')}
0090163c {asm_to_hex(f'movz w28, #0x{special_hex1}, lsl #16')}
00901640 8003271E
009701B0 {asm_to_hex(f'fmov s3, #{rounded_ratio}')}
009237C8 {asm_to_hex(f'movz x9, #0x{special_hex2}')}
009237CC {asm_to_hex(f'movk x9, #0x{special_hex1}, lsl #16')}
008BD0FC {asm_to_hex(f'movz w8, #0x{special_hex2}')}
008BD100 {asm_to_hex(f'movk w8, #0x{special_hex1}, lsl #16')}'''


        patch_content = f'''@nsobid-{nsobidid}

@flag print_values
@flag offset_shift 0x100

@enabled
{fixes}
@disabled

{visual_fix}

// Generated using SMO-AAR by Fayaz (github.com/fayaz12g/sm3dw-aar)'''
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        with open(file_path, 'w') as patch_file:
            patch_file.write(patch_content)
        print(f"Patch file created: {file_path}")

# New System for 110
# movz w28, #0xe38e
# movk w28, #0x4018, lsl #16
# fmov s0, w28
# fmov s3, #2.37500000
# movz x9, #0xe38e
# movk x9, #0x4018, lsl #16
# movz w8, #0xe38e
# movk w8, #0x4018, lsl #16
