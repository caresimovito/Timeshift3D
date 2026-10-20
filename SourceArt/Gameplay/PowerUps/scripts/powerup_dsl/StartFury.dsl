(fn StartFury (Duration)
  ; Fury pickup: double damage (melee via AlignWeaponsToGrip, kick, stones, bolas) for Duration s, red glow on the hero,
  ; on-screen countdown. Picking up another while active just extends it.
  (Variables|Default|SetFuryActive true)
  (Variables|Default|SetFuryEnd (+ (Utilities|Time|GetGameTimeinSeconds) Duration))
  (CallFunction|EnsureBuffLights self)
  (Rendering|SetVisibility (Variables|Default|GetFuryLight) true)
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "FuryTick" :Time 0.25 :bLooping true)
  (Development|PrintString :InString "FURY - double damage!" :bPrintToScreen true :bPrintToLog true :TextColor "(R=1.000000,G=0.250000,B=0.150000,A=1.000000)" :Duration 2.5))
