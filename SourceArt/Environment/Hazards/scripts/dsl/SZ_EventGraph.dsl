(event Collision|EventActorBeginOverlap (OtherActor)
  (bind pc (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object OtherActor)
    (:then
      (Class|BPThirdPersonCharacter|EnterSinkZone :self pc :SpeedMult (Variables|Default|GetSpeedMult) :Rate (Variables|Default|GetSinkRate) :Depth (Variables|Default|GetSinkDepth) :Damage (Variables|Default|GetSinkDamage)))
    (:CastFailed
      (CallFunction|TrapCreature self OtherActor))))

(event Collision|EventActorEndOverlap (OtherActor)
  (bind pc (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object OtherActor)
    (:then
      (Class|BPThirdPersonCharacter|ExitSinkZone :self pc))
    (:CastFailed)))
