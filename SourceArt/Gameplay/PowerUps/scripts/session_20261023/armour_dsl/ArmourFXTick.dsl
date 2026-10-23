(fn ArmourFXTick ()
  ; ARMOUR LOOK (user 2026-10-23 picked Grok concept 4: a polished bronze-statue sheen): while he has armour his slot-0
  ; material becomes M_ArmourBronze (his own colour / normal textures cast in bronze); back to his saved material when
  ; the armour runs out. Runs every tick from ApplyWeaponSelection (cheap: two compares unless the state changes).
  ; Leaves the material alone while invisible (HideFXOn / HideFXOff own slot 0 then) or morphed (dino mesh; the morph's
  ; health lives in the armour).
  (if (not (or (Variables|Default|GetHiding) (Variables|Default|GetMorphed)))
    (bind mesh (Variables|Character|GetMesh))
    (bind want (> (Class|BPHealthComponent|GetArmour (Variables|Default|GetHealthComponent)) 0.0))
    (if (and want (not (Variables|Default|GetArmourFXOn)))
      (Variables|Default|SetArmourSavedMat (Rendering|Material|GetMaterial :self mesh :ElementIndex 0))
      (Rendering|Material|SetMaterial :self mesh :ElementIndex 0 :Material "/Game/Timeshift/VFX/Armour/M_ArmourBronze.M_ArmourBronze")
      (Variables|Default|SetArmourFXOn true))
    (if (and (not want) (Variables|Default|GetArmourFXOn))
      (Rendering|Material|SetMaterial :self mesh :ElementIndex 0 :Material (Variables|Default|GetArmourSavedMat))
      (Variables|Default|SetArmourFXOn false))))
