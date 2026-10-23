(fn HideFXOn ()
  ; INVISIBILITY LOOK (Gemini concept 2026-10-23): his body turns to glass that bends the jungle behind it (M_Invisible:
  ; translucent, refraction 1.12, cyan fresnel rim), faint cyan glowing lines over it (MI_HideGlow overlay) and cyan wisps
  ; drifting off his bones (NS_HideWisps). The hero mesh has one material slot; its material is kept for HideFXOff
  ; (StartHide only calls this while visible, so slot 0 still holds his real material here).
  (bind mesh (Variables|Character|GetMesh))
  (Variables|Default|SetHideSavedMat (Rendering|Material|GetMaterial :self mesh :ElementIndex 0))
  (Rendering|Material|SetMaterial :self mesh :ElementIndex 0 :Material "/Game/Timeshift/VFX/Hide/M_Invisible.M_Invisible")
  (Rendering|Material|SetOverlayMaterial :self mesh :NewOverlayMaterial "/Game/Timeshift/VFX/Hide/MI_HideGlow.MI_HideGlow")
  (Variables|Default|SetHideFX (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Hide/NS_HideWisps.NS_HideWisps" :AttachToComponent mesh :AttachPointName "root" :LocationType "SnapToTarget" :bAutoDestroy false)))
