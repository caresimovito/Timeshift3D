(fn HandleMorphInput ()
  ; M = use a morph charge (polled with the other throw keys); while charged but not morphed, a "MORPH READY" line stays up
  (bind mk (Game|Player|IsInputKeyDown (Game|GetPlayerController 0) "M"))
  (if (and (and mk (not (Variables|Default|GetMorphKeyPressed))) (and (> (Variables|Default|GetMorphCharges) 0) (not (Variables|Default|GetMorphed))))
    (CallFunction|StartMorph self))
  (Variables|Default|SetMorphKeyPressed mk)
  ; DEV KEY - REMOVE BEFORE RELEASE: U morphs without needing Morph Amber, and U again changes straight back
  ; (added 2026-10-20 for testing)
  (bind uk (Game|Player|IsInputKeyDown (Game|GetPlayerController 0) "U"))
  (if (and uk (not (Variables|Default|GetDevMorphPressed)))
    (if (Variables|Default|GetMorphed)
      (CallFunction|EndMorph self)
      (else
        (Variables|Default|SetMorphCharges (+ (Variables|Default|GetMorphCharges) 1))
        (CallFunction|StartMorph self))))
  (Variables|Default|SetDevMorphPressed uk)
  (if (and (> (Variables|Default|GetMorphCharges) 0) (not (Variables|Default|GetMorphed)))
    (Development|PrintString :InString (Utilities|String|Append "MORPH READY - press M   x" (Utilities|String|ToString(Integer) (Variables|Default|GetMorphCharges))) :bPrintToScreen true :bPrintToLog false :TextColor "(R=1.000000,G=0.650000,B=0.100000,A=1.000000)" :Duration 0.3 :Key "Morph")))
