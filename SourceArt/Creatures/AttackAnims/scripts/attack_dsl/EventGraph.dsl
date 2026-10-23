(event AddEvent|EventBeginPlay
  ; tick after the owner has moved this frame, so Guard sees (and can undo) the move
  (Components|Tick|AddTickPrerequisiteActor :self self :PrerequisiteActor (Components|GetOwner self)))

(event AddEvent|EventTick (DeltaSeconds)
  (bind eb (Utilities|Casting|CastToBP_EnemyBase :Object (Components|GetOwner self))
    (:then
      (Variables|Default|SetIsHero false)
      (Variables|Default|SetOwnerEnemy eb)
      (CallFunction|Guard self eb)
      (CallFunction|ApplyDifficulty self eb)
      (CallFunction|Watch self eb)
      (CallFunction|Senses self eb)
      (CallFunction|MoveFx self (== (Class|BPEnemyBase|GetAnimState eb) 2)))
    (:CastFailed
      (CallFunction|HeroFx self))))
