# Editor Python: author the second batch of attack moves (Stomp / Gore / Frenzy / Slash / Sidestep) per species.
# DRY=True first to read the self-check log lines, then DRY=False to write.
NEW_MOVES = {"Raptor": ["Frenzy", "Slash", "Sidestep"], "Dilophosaurus": ["Frenzy", "Slash", "Sidestep"],
             "Compy": ["Frenzy", "Slash", "Sidestep"], "Caudipteryx": ["Frenzy", "Slash", "Sidestep"],
             "Spinosaurus": ["Frenzy", "Slash"], "RiverAmbusher": ["Frenzy", "Stomp"], "Kulindadromeus": ["Sidestep"],
             "Triceratops": ["Gore", "Stomp"], "Ankylosaurus": ["Gore", "Stomp"], "Parasaurolophus": ["Gore", "Stomp"],
             "Stegosaurus": ["Stomp"], "Psittacosaurus": ["Gore", "Sidestep"], "Archaeoceratops": ["Gore", "Sidestep"]}
_dry = globals().get("DRY", True)
_only = globals().get("ONLY")
_src = open(r"C:/agentpy/dino_attack_anims.py").read()
for _sp, _mv in NEW_MOVES.items():
    if _only and _sp not in _only:
        continue
    exec(_src, {"SPECIES": [_sp], "MOVES": _mv, "DRY": _dry, "__name__": "dino_attack_anims"})
