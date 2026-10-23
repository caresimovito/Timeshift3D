(fn RegenFXOn ()
  ; REGEN LOOK (user 2026-10-23: "just use the same as fury but with a green glow"): MI_RegenGlow overlay = M_FuryGlow
  ; (fresnel rim + faint inner glow, gentle pulse) in green. The green RegenLight is handled by StartRegen / RegenTick.
  ; Parked attempts: v1 surface bands (RegenFXOn_v1_overlay.dsl.bak), v2 limb coils (RegenFXOn_v2_coils_parked.dsl).
  (Rendering|Material|SetOverlayMaterial :self (Variables|Character|GetMesh) :NewOverlayMaterial "/Game/Timeshift/VFX/Regen/MI_RegenGlow.MI_RegenGlow"))
