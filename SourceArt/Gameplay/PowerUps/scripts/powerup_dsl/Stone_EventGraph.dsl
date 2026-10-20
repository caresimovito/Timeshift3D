(event EventBeginPlay
  (Actor|SetLifeSpan self 5.0)
  (Collision|SetCollisionProfileName (Variables|Default|GetCollision) "BlockAllDynamic")
  (Physics|SetNotifyRigidBodyCollision (Variables|Default|GetCollision) true)
  (Collision|IgnoreActorWhenMoving (Variables|Default|GetCollision) (Actor|GetOwner self) true))

(event Collision|EventHit (MyComp Other OtherComp bSelfMoved HitLocation HitNormal NormalImpulse Hit)
  ; Damage is set by the thrower (22, x2 under Fury); never hurts the player who threw it
  (bind hc (Utilities|Casting|CastToBP_HealthComponent :Object (Actor|GetComponentbyClass Other "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C"))
    (:then
      (if (not (== Other (Game|GetPlayerCharacter 0)))
        (Class|BPHealthComponent|ApplyDamage hc (Variables|Default|GetDamage))
        (Niagara|SpawnSystematLocation :SystemTemplate "/Game/Variant_Combat/VFX/NS_Damage.NS_Damage" :Location HitLocation :Scale (Math|Vector|MakeVector 1.2 1.2 1.2))
        (Game|Feedback|ClientStartCameraShake (Game|GetPlayerController 0) "/Game/Variant_Combat/Blueprints/BP_CameraShake_Hit_Enemy.BP_CameraShake_Hit_Enemy_C"))
      (Actor|DestroyActor self))
    (:CastFailed
      (Actor|DestroyActor self))))
