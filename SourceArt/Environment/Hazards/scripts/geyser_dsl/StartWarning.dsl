(fn StartWarning ()
  ; tell: hiss + gurgle and a thickening steam plume for WarnTime seconds
  (Variables|Default|SetPhase 1)
  (Components|Activation|Activate (Variables|Default|GetWarn) true)
  (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Hazards/Audio/S_GeyserHiss.S_GeyserHiss" :Location (Transformation|GetActorLocation self) :VolumeMultiplier 1.0 :PitchMultiplier (Math|Random|RandomFloatinRange 0.9 1.1))
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "StartBurst" :Time (Variables|Default|GetWarnTime) :bLooping false))
