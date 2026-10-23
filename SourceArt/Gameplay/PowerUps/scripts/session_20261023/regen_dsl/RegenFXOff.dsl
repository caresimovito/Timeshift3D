(fn RegenFXOff ()
  ; undo RegenFXOn; the body overlay goes back to Adrenaline's electric skin or Fury's glow if one is still on
  (Rendering|Material|SetOverlayMaterial :self (Variables|Character|GetMesh) :NewOverlayMaterial "None")
  (if (Variables|Default|GetFuryActive)
    (CallFunction|FuryFXOn self))
  (if (Variables|Default|GetAdrenaline)
    (Rendering|Material|SetOverlayMaterial :self (Variables|Character|GetMesh) :NewOverlayMaterial "/Game/Timeshift/VFX/Adrenaline/MI_ElectricSkin.MI_ElectricSkin")))
