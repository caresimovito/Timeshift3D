(fn HandleRangedAttack ()
  (CallFunction|EnsurePouches self)
  (CallFunction|UpdateWading self)
  (CallFunction|UpdateSinking self)
  (if (< (Variables|Default|GetStoneAmmo) 0)
    (Variables|Default|SetStoneAmmo 0))
  ; throw a stone: F (user 2026-10-22: "need to remap key for throwing stones") - X still works too
  (bind pc (Game|GetPlayerController 0))
  (bind xk (or (Game|Player|IsInputKeyDown pc "F") (Game|Player|IsInputKeyDown pc "X")))
  (if (and xk (not (Variables|Default|GetThrowKeyPressed)))
    (if (and (<= (Variables|Default|GetStoneAmmo) 0) (not (Variables|Default|GetMorphed)))
      ; no stones: say so instead of silently doing nothing
      (Development|PrintString :InString "No stones - pick some up (grey stone piles)" :bPrintToScreen true :bPrintToLog false :TextColor "(R=1.000000,G=0.800000,B=0.400000,A=1.000000)" :Duration 1.5 :Key "NoStones")
      (else
        (CallFunction|QuickThrow self))))
  (Variables|Default|SetThrowKeyPressed xk)
  ; aiming (right mouse held) + LEFT CLICK throws, read straight from the mouse (user 2026-10-23: left click still did not
  ; throw through the attack input). PerformAttack's own aimed branch is then blocked by bIsRangedAttacking - no double throw
  (bind lmb (Game|Player|IsInputKeyDown pc "LeftMouseButton"))
  (if (and (and lmb (not (Variables|Default|GetAimClickPressed))) (Variables|Default|GetIsAiming))
    (if (<= (Variables|Default|GetStoneAmmo) 0)
      (Development|PrintString :InString "No stones - pick some up (grey stone piles)" :bPrintToScreen true :bPrintToLog false :TextColor "(R=1.000000,G=0.800000,B=0.400000,A=1.000000)" :Duration 1.5 :Key "NoStones")
      (else
        (CallFunction|QuickThrow self))))
  (Variables|Default|SetAimClickPressed lmb)
  (CallFunction|HandleDevPanels self))
