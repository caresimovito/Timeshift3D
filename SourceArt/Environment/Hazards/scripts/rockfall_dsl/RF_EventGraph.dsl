(event Collision|EventActorBeginOverlap (OtherActor)
  (bind pc (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object OtherActor)
    (:then
      (if (not (Variables|Default|GetBusy))
        (CallFunction|StartFall self)))
    (:CastFailed)))
