(fn PlayWeaponSwing ()
  ; whoosh for the weapon in hand; as a dinosaur (morph) a growl instead - higher for the small ones, deeper for the big
  (if (Variables|Default|GetMorphed)
    (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_Creature_Growl_01.S_Creature_Growl_01" :Location (Transformation|GetActorLocation self) :VolumeMultiplier 1.0 :PitchMultiplier (select (< (Variables|Default|GetMorphHP) 150.0) 1.3 0.85))
    (else
      (Audio|PlaySoundatLocation :Sound (select (and (== (Variables|Default|GetCurrentWeaponIndex) 1) (Variables|Default|GetHasBoneClub)) (Variables|Default|GetWpnSndClub) (select (and (== (Variables|Default|GetCurrentWeaponIndex) 2) (Variables|Default|GetHasTorch)) (Variables|Default|GetWpnSndTorch) (Variables|Default|GetWpnSndSpear))) :Location (Transformation|GetActorLocation self) :VolumeMultiplier 0.85))))
