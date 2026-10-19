(fn Impact (Speed)
  ; thud (louder for harder hits, deeper for bigger rocks) + a puff of dust where it struck
  (Variables|Default|SetSnd (Math|Random|RandomIntegerinRange 0 2))
  (Variables|Default|SetSndVol (Math|Float|Clamp(Float) (/ Speed 900.0) 0.25 1.3))
  (if (== (Variables|Default|GetSnd) 0)
    (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Hazards/Audio/S_RockImpact_01.S_RockImpact_01" :Location (Transformation|GetActorLocation self) :VolumeMultiplier (Variables|Default|GetSndVol) :PitchMultiplier (- 1.2 (Variables|Default|GetScale)))
    (else
      (if (== (Variables|Default|GetSnd) 1)
        (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Hazards/Audio/S_RockImpact_02.S_RockImpact_02" :Location (Transformation|GetActorLocation self) :VolumeMultiplier (Variables|Default|GetSndVol) :PitchMultiplier (- 1.2 (Variables|Default|GetScale)))
        (else
          (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Hazards/Audio/S_RockImpact_03.S_RockImpact_03" :Location (Transformation|GetActorLocation self) :VolumeMultiplier (Variables|Default|GetSndVol) :PitchMultiplier (- 1.2 (Variables|Default|GetScale)))))))
  (Niagara|SpawnSystematLocation :SystemTemplate "/Game/Timeshift/Hazards/VFX/NS_RockDust.NS_RockDust" :Location (Transformation|GetActorLocation self) :Scale (Math|Vector|MakeVector (* 1.8 (Variables|Default|GetScale)) (* 1.8 (Variables|Default|GetScale)) (* 1.8 (Variables|Default|GetScale)))))
