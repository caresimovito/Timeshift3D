(event AddEvent|EventTick (DeltaSeconds)
  (bind eb (Utilities|Casting|CastToBP_EnemyBase :Object (Components|GetOwner self))
    (:then
      (CallFunction|Watch self eb))
    (:CastFailed)))
