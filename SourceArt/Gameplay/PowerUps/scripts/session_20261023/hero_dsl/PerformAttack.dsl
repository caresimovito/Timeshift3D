(fn PerformAttack ()
  ; aiming (right mouse held) with stones: left click throws. It goes through QuickThrow (as F / X do), which clears a
  ; leftover bola flag and aims at the crosshair - calling ThrowStone directly counted BOLAS after a bola throw, so with no
  ; bolas left the aimed left click did nothing (user 2026-10-23: "left click is not working to throw stones")
  (if (and (Variables|Default|GetIsAiming) (> (Variables|Default|GetStoneAmmo) 0))
    (CallFunction|QuickThrow self)
    (else
      (bind cm (Variables|Character|GetCharacterMovement))
      (Components|Movement|StopMovementImmediately cm)
      (Class|CharacterMovementComponent|SetMaxWalkSpeed 0.0 cm)
      (CallFunction|PlayWeaponAttackAnim self)
      (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "ApplyAttackDamage" :Time 0.22))))
