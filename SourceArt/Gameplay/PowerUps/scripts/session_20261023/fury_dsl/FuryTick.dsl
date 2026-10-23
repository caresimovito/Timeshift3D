(fn FuryTick ()
  (Variables|Default|SetBuffLeft (- (Variables|Default|GetFuryEnd) (Utilities|Time|GetGameTimeinSeconds)))
  (bind on (> (Variables|Default|GetBuffLeft) 0.0))
  ; screen effect: in over 0.5 s, out over 0.7 s (applied to FuryPP at the end)
  (Variables|Default|SetFuryBlend (Math|Float|Clamp(Float) (+ (Variables|Default|GetFuryBlend) (select on 0.2 -0.15)) 0.0 1.0))
  (if on
    ; the light flickers like a fire
    (Rendering|Components|Light|SetIntensity :self (Variables|Default|GetFuryLight) :NewIntensity (* 8000.0 (Math|Random|RandomFloatinRange 0.7 1.3)))
    (Development|PrintString :InString (Utilities|String|Append "FURY  x2 damage   " (Utilities|String|ToString(Integer) (Math|Float|Ceil (Variables|Default|GetBuffLeft)))) :bPrintToScreen true :bPrintToLog false :TextColor "(R=1.000000,G=0.250000,B=0.150000,A=1.000000)" :Duration 0.2 :Key "Fury")
    (else
      (if (Variables|Default|GetFuryActive)
        (Variables|Default|SetFuryActive false)
        (Rendering|SetVisibility :self (Variables|Default|GetFuryLight) :bNewVisibility false)
        (CallFunction|FuryFXOff self)
        (Development|PrintString :InString "Fury fades" :bPrintToScreen true :bPrintToLog false :TextColor "(R=0.700000,G=0.400000,B=0.300000,A=1.000000)" :Duration 1.5 :Key "Fury"))
      (if (<= (Variables|Default|GetFuryBlend) 0.0)
        (Utilities|Time|ClearTimerbyFunctionName :Object self :FunctionName "FuryTick"))))
  (Utilities|IsValid (Variables|Default|GetFuryPP)
    (:"Is Valid"
      (Class|PostProcessVolume|SetBlendWeight :self (Variables|Default|GetFuryPP) :BlendWeight (Variables|Default|GetFuryBlend)))))
