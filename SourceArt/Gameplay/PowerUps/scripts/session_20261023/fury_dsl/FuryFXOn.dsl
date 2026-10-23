(fn FuryFXOn ()
  ; FURY = the FIERY GLOW look (user 2026-10-23 compared both in game: "the glow one looks better remove the other one").
  ; No particles: hot orange rim + faint ember warmth on the body (M_FuryGlow overlay, additive fresnel, no noise),
  ; red-hot weapon in hand (MI_FuryGlowSpear overlay on the spear and club), the flickering orange light (FuryTick).
  ; The flames versions are parked: v7 small flames FuryFXOn_v7_flames_parked.dsl, v6 FuryFXOn_v6.dsl.bak,
  ; v5 FuryFXOn_v5_parked.dsl (assets NS_FuryAura / NS_FurySpearFire / M_FuryFlame are unused now).
  ; FuryTick fades FuryPP; FuryFXOff clears the overlays. ApplyWeaponSelection re-runs this on a weapon switch.
  (bind mesh (Variables|Character|GetMesh))
  (Variables|Default|SetFuryFXWeapon (Variables|Default|GetCurrentWeaponIndex))
  (Rendering|Components|Light|SetLightColor :self (Variables|Default|GetFuryLight) :NewLightColor "(R=1.000000,G=0.350000,B=0.080000,A=1.000000)")
  (Rendering|Material|SetOverlayMaterial :self mesh :NewOverlayMaterial "/Game/Timeshift/VFX/Fury/M_FuryGlow.M_FuryGlow")
  (Rendering|Material|SetOverlayMaterial :self (Variables|Default|GetSpearMeshComponent) :NewOverlayMaterial "/Game/Timeshift/VFX/Fury/MI_FuryGlowSpear.MI_FuryGlowSpear")
  (Rendering|Material|SetOverlayMaterial :self (Variables|Default|GetClubMeshComponent) :NewOverlayMaterial "/Game/Timeshift/VFX/Fury/MI_FuryGlowSpear.MI_FuryGlowSpear")
  (bind pps (Actor|GetAllActorsWithTag :Tag "FuryPP"))
  (if (> (Utilities|Array|Length pps) 0)
    (Variables|Default|SetFuryPP (Utilities|Casting|CastToPostProcessVolume :Object (Utilities|Array|Get(acopy) pps 0)))))
