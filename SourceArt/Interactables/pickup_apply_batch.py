# Editor Python: the 8 Meshy pickups (2026-10-23) through pickup_apply.py, one after another
S = "C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables/"
JOBS = [  # folder, BP, tint, glow, scale, light rgb, lux
    ("SauropodEgg", "BP_Pickup_EggLarge", (1.0, 0.8, 0.35), 0.8, 1.2, (255, 200, 90), 6000.0),
    ("Fury", "BP_Pickup_Fury", (1.0, 0.3, 0.2), 1.2, 1.3, (255, 70, 40), 6000.0),
    ("Adrenaline", "BP_Pickup_Adrenaline", (1.0, 0.9, 0.3), 1.2, 1.6, (255, 230, 80), 6000.0),
    ("Hide", "BP_Pickup_Hide", (0.7, 0.4, 1.0), 1.2, 1.3, (170, 90, 255), 6000.0),
    ("Regen", "BP_Pickup_Regen", (0.4, 1.0, 0.9), 1.0, 1.3, (90, 255, 220), 6000.0),
    ("Armour", "BP_Pickup_Armour", (0.6, 0.8, 1.0), 0.6, 1.2, (160, 200, 255), 5000.0),
    ("MorphAmber", "BP_Pickup_Morph", (1.0, 0.6, 0.15), 1.5, 1.6, (255, 150, 40), 6000.0),
    ("Stones", "BP_Pickup_Stones", (1.0, 1.0, 1.0), 0.15, 1.3, (255, 255, 255), 0.0),
]
_src = open(r"C:/agentpy/pickup_apply.py").read()
for folder, bpn, tint, glow, scale, light, lux in JOBS:
    g = dict(GLB=S + "%s/SM_%s.glb" % (folder, folder), DEST="/Game/Timeshift/Interactables/%s" % folder,
             BP="/Game/Timeshift/Interactables/%s" % bpn, TINT=tint, GLOW=glow, SCALE=scale, LIGHT=light, LUX=lux)
    exec(_src, g)
import unreal
unreal.log_warning("[PBATCH] done")
