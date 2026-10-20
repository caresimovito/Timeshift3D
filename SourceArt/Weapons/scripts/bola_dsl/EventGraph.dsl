(event EventBeginPlay
  (Actor|SetLifeSpan self 6.0)
  (Collision|SetCollisionProfileName (Variables|Default|GetCollision) "BlockAllDynamic")
  (Physics|SetNotifyRigidBodyCollision (Variables|Default|GetCollision) true)
  (Collision|IgnoreActorWhenMoving (Variables|Default|GetCollision) (Actor|GetOwner self) true))

(event Collision|EventHit (MyComp Other OtherComp bSelfMoved HitLocation HitNormal NormalImpulse Hit)
  ; never the player: the bola spawns at his hand, inside his capsule, and his own movement used to "hit" it -
  ; it then snared, froze and damaged HIM every frame (seen 2026-10-20, the 'floating on the bola' report)
  (if (not (== Other (Game|GetPlayerCharacter 0)))
    (bind hc (Utilities|Casting|CastToBP_HealthComponent :Object (Actor|GetComponentbyClass Other "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C"))
      (:then
        (Variables|Default|SetSnared Other)
        (Class|BPHealthComponent|ApplyDamage hc (Variables|Default|GetDamage))
        (Components|Movement|StopMovementImmediately (Variables|Default|GetMovement))
        (Collision|SetCollisionEnabled (Variables|Default|GetCollision) "NoCollision")
        (Components|Activation|Deactivate (Variables|Default|GetSpin))
        (Transformation|AttachActorToActor self Other :LocationRule "KeepWorld" :RotationRule "KeepWorld" :ScaleRule "KeepWorld")
        (Actor|SetLifeSpan self 0.0)
        (Actor|Tick|SetActorTickEnabled Other false)
        (Development|PrintString "Snared!" true true "(R=1.000000,G=0.800000,B=0.300000,A=1.000000)" 1.5)
        (Utilities|Time|SetTimerbyFunctionName self "ReleaseSnare" 3.0)
        (CallFunction|SetSnareAnimRate self 0.25)
        (CallFunction|BeginSnareHold self))
      (:CastFailed
        (Actor|DestroyActor self)))))

(event AddEvent|EventTick (DeltaSeconds)
  (if (Variables|Default|GetSnareFalling)
    (CallFunction|StepSnareFall self DeltaSeconds)))
