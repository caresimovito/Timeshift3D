(fn DimEnemy (Target)
  ; INVISIBLE (user 2026-10-23: Hide becomes invisibility, until its timer ends - attacking does not break it): the enemy's
  ; sight goes to 0 (its hearing follows - BP_AttackVariety.Senses scales from it), the real range parked in
  ; DetectionRangeBackup (the convention ApplyDifficulty already follows). Was: range x 0.45.
  (bind e (Utilities|Casting|CastToBP_EnemyBase :Object Target)
    (:then
      (if (> (Class|BPEnemyBase|GetDetectionRange e) 0.0)
        (Class|BPEnemyBase|SetDetectionRangeBackup :self e :DetectionRangeBackup (Class|BPEnemyBase|GetDetectionRange e))
        (Class|BPEnemyBase|SetDetectionRange :self e :DetectionRange 0.0)))
    (:CastFailed)))
