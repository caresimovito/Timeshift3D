(fn ApplyDifficulty (Enemy)
  ; DIFFICULTY (user 2026-10-21): the hero's AttackVariety holds the level (0 easy, 1 medium, 2 hard - saved in the settings
  ; save). Each enemy captures its species stats once, then re-applies multipliers whenever the level changes:
  ;   damage 0.6 / 1 / 1.4, health 0.75 / 1 / 1.3, sight + hearing 0.8 / 1 / 1.25, attack cooldown 1.3 / 1 / 0.8.
  ; Health keeps its current fraction. A hidden player (Hide power-up) has detection zeroed with the real value in
  ; DetectionRangeBackup, so the scaled range goes there while it is in use.
  (bind now (Utilities|Time|GetGameTimeinSeconds))
  (if (> now (Variables|Default|GetNextDiffCheck))
    (Variables|Default|SetNextDiffCheck (+ now 1.0))
    (bind hc (Class|BPEnemyBase|GetHealthComponent Enemy))
    (if (not (Variables|Default|GetBaseCaptured))
      (Variables|Default|SetBaseCaptured true)
      ; the captured species stats ARE the medium level (don't trust the component's default here: templates inside
      ; BP_EnemyBase / the hero kept 0 when the variable was added)
      (Variables|Default|SetAppliedDifficulty 1)
      (Variables|Default|SetBaseDamage (Class|BPEnemyBase|GetAttackDamage Enemy))
      (Variables|Default|SetBaseDetection (select (> (Class|BPEnemyBase|GetDetectionRange Enemy) 0.0) (Class|BPEnemyBase|GetDetectionRange Enemy) (Class|BPEnemyBase|GetDetectionRangeBackup Enemy)))
      (Variables|Default|SetBaseCooldown (Class|BPEnemyBase|GetAttackCooldown Enemy))
      (Variables|Default|SetBaseMaxHealth (Class|BPHealthComponent|GetMaxHealth hc)))
    (bind hero (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Game|GetPlayerCharacter 0))
      (:then
        (Variables|Default|SetDifficulty (CallFunction|GetLevel (Class|BPThirdPersonCharacter|GetAttackVariety hero)))
        (if (and (!= (Variables|Default|GetDifficulty) (Variables|Default|GetAppliedDifficulty)) (not (Class|BPHealthComponent|GetIsDead hc)))
          (Variables|Default|SetAppliedDifficulty (Variables|Default|GetDifficulty))
          (bind d (Variables|Default|GetDifficulty))
          (Class|BPEnemyBase|SetAttackDamage :self Enemy :AttackDamage (* (Variables|Default|GetBaseDamage) (select (== d 0) 0.6 (select (== d 2) 1.4 1.0))))
          (Class|BPEnemyBase|SetAttackCooldown :self Enemy :AttackCooldown (* (Variables|Default|GetBaseCooldown) (select (== d 0) 1.3 (select (== d 2) 0.8 1.0))))
          (if (> (Class|BPEnemyBase|GetDetectionRange Enemy) 0.0)
            (Class|BPEnemyBase|SetDetectionRange :self Enemy :DetectionRange (* (Variables|Default|GetBaseDetection) (select (== d 0) 0.8 (select (== d 2) 1.25 1.0))))
            (else
              (Class|BPEnemyBase|SetDetectionRangeBackup :self Enemy :DetectionRangeBackup (* (Variables|Default|GetBaseDetection) (select (== d 0) 0.8 (select (== d 2) 1.25 1.0))))))
          ; current health first (it reads the OLD max), then the new max
          (Class|BPHealthComponent|SetCurrentHealth :self hc :CurrentHealth (* (Class|BPHealthComponent|GetCurrentHealth hc) (/ (* (Variables|Default|GetBaseMaxHealth) (select (== d 0) 0.75 (select (== d 2) 1.3 1.0))) (Class|BPHealthComponent|GetMaxHealth hc))))
          (Class|BPHealthComponent|SetMaxHealth :self hc :MaxHealth (* (Variables|Default|GetBaseMaxHealth) (select (== d 0) 0.75 (select (== d 2) 1.3 1.0))))))
      (:CastFailed))))
