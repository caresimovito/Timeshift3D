(fn HandlePlayerExit (OtherActor)
  (bind pc (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object OtherActor)
    (:then
      (Variables|Default|SetPlayerInside false)
      (if (not (Variables|Default|GetIsPeriodicBurst))
        (Class|BPThirdPersonCharacter|SetHazardSpeed :self pc :Mult 1.0)
        (Utilities|Time|ClearTimerbyFunctionName self "ApplyContinuousDamage")))
    (:CastFailed)))
