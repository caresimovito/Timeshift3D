# Generates the hero's morph graphs (Saved/morph_dsl). Species pool = 8 fun-to-play ground dinosaurs; stats are tuned for
# the PLAYER (his normal: 100 HP, 500 speed), not copied from the enemy versions. Psittacosaurus was dropped
# 2026-10-20: its animation clips collapse every bone onto the pelvis (broken export) - invisible as a morph. HP lives in the health component's
# ARMOUR (which already absorbs damage first and has a HUD bar), so the hero's own health is untouched while morphed.
#            name             hp   dmg  speed range cool  capR capHH
SPECIES = [("Raptor",        120, 25, 720, 190, 0.8,  55,  80),
           ("Dilophosaurus", 140, 28, 560, 230, 1.0,  65, 150),
           ("Parasaurolophus", 230, 30, 520, 300, 1.2, 95, 200),
           ("Spinosaurus",   270, 45, 520, 340, 1.4, 100, 190),
           ("Triceratops",   300, 50, 430, 290, 1.5, 110, 175),
           ("Stegosaurus",   320, 45, 370, 320, 1.6, 105, 200),
           ("Ankylosaurus",  360, 40, 340, 270, 1.5, 110, 120),
           # the little ones (added 2026-10-20 at the user's request): fast and fragile
           ("Compy",          60,  8, 750, 110, 0.4,  30,  40),
           ("Kulindadromeus", 70, 10, 700, 120, 0.5,  32,  42)]
D = r"C:/repos/Unreal Projects/Timeshift3D/Saved/morph_dsl/"
# camera: extra distance behind (along the boom) ~ body half-length, and lift ~ body height
CAMBACK = {"Raptor": 120, "Dilophosaurus": 280, "Psittacosaurus": 40, "Parasaurolophus": 520, "Spinosaurus": 460,
           "Triceratops": 400, "Stegosaurus": 460, "Ankylosaurus": 340,
           "Compy": 0, "Kulindadromeus": 0}


def path(sp, what):
    if what == "mesh":
        return "/Game/Timeshift/Enemies/%s/SK_%s.SK_%s" % (sp, sp, sp)
    n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, what)
    return "/Game/Timeshift/Enemies/%s/%s.%s" % (sp, n, n)


# ---- PickMorphSpecies(Index): nested if/elif chain filling the Morph* vars
body = ""
for i, (sp, hp, dmg, spd, rng, cd, r, hh) in enumerate(SPECIES):
    sets = "\n".join("    " + l for l in [
        '(Variables|Default|SetMorphName "%s")' % sp,
        '(Variables|Default|SetMorphHP %.1f)' % hp, '(Variables|Default|SetMorphDmg %.1f)' % dmg,
        '(Variables|Default|SetMorphSpeed %.1f)' % spd, '(Variables|Default|SetMorphRange %.1f)' % rng,
        '(Variables|Default|SetMorphCooldown %.2f)' % cd, '(Variables|Default|SetMorphRadius %.1f)' % min(r, 65),
        '(Variables|Default|SetMorphHalf %.1f)' % hh,
        '(Variables|Default|SetMorphCamBack %.1f)' % CAMBACK[sp], '(Variables|Default|SetMorphCamUp %.1f)' % (hh * 0.45),
        '(Variables|Default|SetMorphMeshAsset "%s")' % path(sp, "mesh"),
        '(Variables|Default|SetMorphIdle "%s")' % path(sp, "Idle"), '(Variables|Default|SetMorphWalk "%s")' % path(sp, "Walk"),
        '(Variables|Default|SetMorphRun "%s")' % path(sp, "Run"), '(Variables|Default|SetMorphAttack "%s")' % path(sp, "Attack")])
    body += ("  (if (== Index %d)\n%s)\n" % (i, sets))
open(D + "PickMorphSpecies.dsl", "w").write(
    "(fn PickMorphSpecies (Index)\n  ; morph pool: " + ", ".join(s[0] for s in SPECIES) + "\n" + body.rstrip() + ")\n")
print("species", len(SPECIES))
