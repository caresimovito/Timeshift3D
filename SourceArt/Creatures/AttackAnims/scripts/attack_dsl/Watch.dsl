(fn Watch (Enemy)
  (bind st (Class|BPEnemyBase|GetAnimState Enemy))
  (bind sp (Class|BPEnemyBase|GetSpecies Enemy))
  ; the player comes within its detection range -> roar once (re-armed when he is well clear again). bHasBeenProvoked
  ; was tried first, but it only flips when the PLAYER hits a passive animal - hunters attack without it
  (Variables|Default|SetPlayerDist (Math|Vector|Distance(Vector) (Transformation|GetActorLocation Enemy) (Transformation|GetActorLocation (Game|GetPlayerCharacter 0))))
  (if (and (< (Variables|Default|GetPlayerDist) (Class|BPEnemyBase|GetDetectionRange Enemy)) (not (Variables|Default|GetWasProvoked)))
    (Variables|Default|SetWasProvoked true)
    (Variables|Default|SetMoveLen (CallFunction|PlayMove self (Class|BPEnemyBase|GetBody Enemy) sp 9))
    (if (> (Variables|Default|GetMoveLen) 0.0)
      (Class|BPEnemyBase|SetAttackEndTime :self Enemy :AttackEndTime (+ (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveLen)))))
  (if (> (Variables|Default|GetPlayerDist) (* 1.6 (Class|BPEnemyBase|GetDetectionRange Enemy)))
    (Variables|Default|SetWasProvoked false))
  ; attack just started -> maybe swap in one of the species' moves (0 keeps the original bite)
  (if (and (== st 2) (!= (Variables|Default|GetLastState) 2))
    (Variables|Default|SetPick (Math|Random|RandomIntegerinRange 0 (CallFunction|MoveCount self sp)))
    (if (> (Variables|Default|GetPick) 0)
      (Variables|Default|SetMoveLen (CallFunction|PlayMove self (Class|BPEnemyBase|GetBody Enemy) sp (Variables|Default|GetPick)))
      (if (> (Variables|Default|GetMoveLen) 0.0)
        (Class|BPEnemyBase|SetAttackEndTime :self Enemy :AttackEndTime (+ (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveLen)))
        ; its next attack waits for the move to finish: UpdateBodyAnim never holds an attack, so a cooldown shorter than the
        ; move (Raptor 0.8 s vs Frenzy 1.0 s) would bite over it and cut its last hits off
        (Utilities|Time|SetTimerbyFunctionName :Object Enemy :FunctionName "ResetAttackCooldown" :Time (Math|Float|Max(Float) (Class|BPEnemyBase|GetAttackCooldown Enemy) (+ (Variables|Default|GetMoveLen) 0.2)) :bLooping false))))
  (Variables|Default|SetLastState st))
