(fn Rearm ()
  ; cooldown over: go again straight away if the hero is still on the path under the cliff
  (Variables|Default|SetBusy false)
  (if (Collision|IsOverlappingActor self (Game|GetPlayerCharacter 0))
    (CallFunction|StartFall self)))
