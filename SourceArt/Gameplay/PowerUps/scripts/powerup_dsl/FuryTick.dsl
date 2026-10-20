(fn FuryTick ()
  (Variables|Default|SetBuffLeft (- (Variables|Default|GetFuryEnd) (Utilities|Time|GetGameTimeinSeconds)))
  (if (<= (Variables|Default|GetBuffLeft) 0.0)
    (Variables|Default|SetFuryActive false)
    (Rendering|SetVisibility (Variables|Default|GetFuryLight) false)
    (Utilities|Time|ClearTimerbyFunctionName :Object self :FunctionName "FuryTick")
    (Development|PrintString :InString "Fury fades" :bPrintToScreen true :bPrintToLog false :TextColor "(R=0.700000,G=0.400000,B=0.300000,A=1.000000)" :Duration 1.5 :Key "Fury")
    (else
      (Development|PrintString :InString (Utilities|String|Append "FURY  x2 damage   " (Utilities|String|ToString(Integer) (Math|Float|Ceil (Variables|Default|GetBuffLeft)))) :bPrintToScreen true :bPrintToLog false :TextColor "(R=1.000000,G=0.250000,B=0.150000,A=1.000000)" :Duration 0.3 :Key "Fury"))))
