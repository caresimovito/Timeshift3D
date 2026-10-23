(fn RestoreEnemy (Target)
  ; undo DimEnemy: the parked sight range comes back
  (bind e (Utilities|Casting|CastToBP_EnemyBase :Object Target)
    (:then
      (if (and (<= (Class|BPEnemyBase|GetDetectionRange e) 0.0) (> (Class|BPEnemyBase|GetDetectionRangeBackup e) 0.0))
        (Class|BPEnemyBase|SetDetectionRange :self e :DetectionRange (Class|BPEnemyBase|GetDetectionRangeBackup e))))
    (:CastFailed)))
