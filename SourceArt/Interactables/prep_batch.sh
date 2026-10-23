#!/bin/bash
# Blender prep for the 8 Meshy pickups, one after another (memory - Unreal keeps running out), previews -> scratchpad
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
S="C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables"
P="C:/Users/vitoc/AppData/Local/Temp/claude/C--repos/2e5987e6-fff4-4bb7-b101-81dc3e01b334/scratchpad"
for spec in "SauropodEgg 0.55" "Fury 0.40" "Adrenaline 0.45" "Hide 0.45" "Regen 0.40" "Armour 0.50" "MorphAmber 0.30" "Stones 0.35"; do
  set -- $spec
  "$B" -b --factory-startup -noaudio -P C:/agentpy/pickup_prep.py -- "$S/$1/$1_meshy_raw.glb" "$S/$1/SM_$1.glb" "$P/prev_$1.png" "SM_$1" $2 8000 2>&1 | grep -a "HERBP\] faces\|Error" | sed "s/^/[$1] /"
done
echo "[PREP] done"
