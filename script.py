import os
import struct
from functions import *

def patch_blarc(aspect_ratio, HUD_pos, unpacked_folder):
    unpacked_folder = str(unpacked_folder)
    aspect_ratio = float(aspect_ratio)
    print(f"Aspect ratio is {aspect_ratio}")
    HUD_pos = str(HUD_pos)

    layout_map = {
                    'SingleModeSceneLayout': ['CounterCoin', 'CounterGoalItem', 'CounterScenarioShine', 'ChallengeTimer', 'Menu', "ItemStock", "ShardCounter"],
                    'CourseSelectSceneLayout': ['Menu', 'World', 'Counters', 'CounterGreenStarTotal'],
                    'StageSceneLayout': ['CounterCoin', 'CounterPlayer', 'CounterGreenStar', 'ItemStock', 'CounterTime', 'CounterScore', 'NetworkQuality', "CounterStamp"],
                    'WindowProcessing': ['Capture04', 'All2', 'PicMario32_ds', 'PicMario32', 'TxtGuide'],
                    'RCS_Loading': ['Loading'],   
                    'RCS_NetworkLoading': ['Loading'], 
                    'RCS_SceneSkip': ['Menu'],   
                }

    def patch_ui_layouts(direction):
        if direction == "x":
            offset = 0x40
        if direction == 'y':
            offset = 0x48

        for filename, panes in layout_map.items():
            modified_name = filename + "_name"
            paths = file_paths.get(modified_name, [])
            
            new_paths = {}
            
            default_path = os.path.join(unpacked_folder, "romfs", "LayoutData", filename, "layout", "blyt", f"{filename}.bflyt")
            new_paths[default_path] = filename
            
            for full_path_of_file in new_paths:
                with open(full_path_of_file, 'rb') as f:
                    content = f.read().hex()
                
                start_rootpane = content.index(b'RootPane'.hex())
                
                for pane in panes:
                    pane_hex = pane.encode('utf-8').hex()
                    start_pane = content.index(pane_hex, start_rootpane)
                    idx = start_pane + offset 
                    
                    current_value_hex = content[idx:idx+8]
                    current_value = hex2float(current_value_hex)
                    
                    new_value = (current_value * s1**-1)
                    new_value_hex = float2hex(new_value)
                    
                    content = content[:idx] + new_value_hex + content[idx+8:]
                
                with open(full_path_of_file, 'wb') as f:
                    f.write(bytes.fromhex(content))

    def patch_blyt(filename, pane, operation, value):
        if operation == "scale_x" or operation == "scale_y":
            if value < 1:
                command = "Squishing"
            if value > 1:
                command = "Stretching"
            if value == 1:
                command = "Ignoring"
        if operation == "shift_x" or operation == "shift_y":
            command = "Shifting"

        print(f"{command} {pane} of {filename}")
        offset_dict = {'shift_x': 0x40, 'shift_y': 0x48, 'scale_x': 0x70, 'scale_y': 0x78} 
        modified_name = filename + "_name"
        if operation == "shift_x" or  operation == "shift_y":
            full_path_of_file = os.path.join(unpacked_folder, 'romfs', 'LayoutData', filename, 'layout', 'blyt', f'{filename}.bflyt')
        else:
            full_path_of_file = file_paths.get(modified_name)
        with open(full_path_of_file, 'rb') as f:
            content = f.read().hex()
        start_rootpane = content.index(b'RootPane'.hex())
        pane_hex = str(pane).encode('utf-8').hex()
        start_pane = content.index(pane_hex, start_rootpane)
        idx = start_pane + offset_dict[operation]
        content_new = content[:idx] + float2hex(value) + content[idx+8:]
        with open(full_path_of_file, 'wb') as f:
            f.write(bytes.fromhex(content_new))


    def patch_anim(folder, filename, offset, value):
        full_path = os.path.join(unpacked_folder, 'romfs', 'LayoutData', folder, 'layout', 'anim', f'{filename}.bflan') # update this to work with layout.lyarc structure
        with open(full_path, 'rb') as f:
            content = f.read().hex()
        idx = offset
        content_new = content[:idx] + float2hex(value) + content[idx+8:]
        with open(full_path, 'wb') as f:
            f.write(bytes.fromhex(content_new))  

    file_paths = {}

    blyt_folder = os.path.abspath(os.path.join(unpacked_folder))
    file_names_stripped = []
    
    do_not_scale_rootpane = ['WipeFadeBlack', 'WipeFadeWhite', 'WipeMystery', 'WipeMiss', "WipeNetwork", "WipeCurtainStart", "WipeCurtainResult", 'WipeCurtainRanking', 'WipeCurtainRankingParts', 'WipeCasino', 'WipeFairy', 'WipeKnoko', "WipeMissSingleMode", 'WipeNetwork', 'WipeCurtainDemo']
   
    rootpane_by_y = ['WipeCircle']

    for root, dirs, files in os.walk(blyt_folder):
        for file_name in files:
            if file_name.endswith(".bflyt"):
                file_names_stripped.append(file_name.strip(".bflyt"))
                stripped_name = file_name.strip(".bflyt")
                full_path = os.path.join(root, file_name)
                modified_name = stripped_name + "_name"
                file_paths[modified_name] = full_path

    
    if aspect_ratio >= 16/9:
        # (((((aspect_ratio * 9) - 16) / 2) + 16) / 9)  / aspect_ratio
        s1 = (16 / 9)  / aspect_ratio
        print(f"Scaling factor is set to {s1}")
        s2 = 1-s1
        s3 = s2/s1
        s4 = (16/10) / aspect_ratio
        
        for name in file_names_stripped:
            if name in do_not_scale_rootpane:
                    print(f"Skipping RootPane scaling of {name}")
            if name not in do_not_scale_rootpane:
                patch_blyt(name, 'RootPane', 'scale_x', s1)
            if name in rootpane_by_y:
                patch_blyt(name, 'RootPane', 'scale_y', 1/s1)
                patch_blyt(name, 'RootPane', 'scale_x', 1)

        patch_blyt('TitleLogo', 'ParControlGuideBar', 'scale_x', 1/s1)
   

        if HUD_pos == 'corner':
            print("Shifitng elements for corner HUD")
            patch_ui_layouts("x")

            
    else:
        s1 = aspect_ratio / (16/9)
        s2 = 1-s1
        s3 = s2/s1
        
        for name in file_names_stripped:
            if name in do_not_scale_rootpane:
                print(f"Skipping root pane scaling of {name}")
            if name not in do_not_scale_rootpane:
                patch_blyt(name, 'RootPane', 'scale_y', s1)
             
        patch_blyt('TitleLogo', 'ParControlGuideBar', 'scale_y', 1/s1)

        if HUD_pos == 'corner':
            print("Shifitng elements for corner HUD")
            patch_blyt('TitleLogo', 'Buttons', 'shift_y', -240/s1)
            patch_blyt('TitleLogo', 'ParButtonLuigiBros', 'shift_y', -300/s1)
            patch_blyt('SingleModeSceneLayout', 'CounterCoin', 'shift_y', -230/s1)
            patch_blyt('SingleModeSceneLayout', 'ShardCounter', 'shift_y', -376/s1)
            patch_blyt('SingleModeSceneLayout', 'CounterGoalItem', 'shift_y', 257/s1)
            patch_blyt('SingleModeSceneLayout', 'CounterScenarioShine', 'shift_y', 214/s1)
            patch_blyt('SingleModeSceneLayout', 'ChallengeTimer', 'shift_y', 416/s1)
            patch_blyt('SingleModeSceneLayout', 'Menu', 'shift_y', 271/s1)
            patch_blyt('SingleModeSceneLayout', 'ItemStock', 'shift_y', 6/s1)