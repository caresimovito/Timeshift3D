(fn SetDifficulty (D)
  ; 0 easy / 1 medium / 2 hard: the hero's AttackVariety holds it (every enemy reads it from there), the settings save keeps it
  (bind hero (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (Class|BPAttackVariety|SetDifficulty :self (Class|BPThirdPersonCharacter|GetAttackVariety hero) :Difficulty D)
      (CallFunction|SaveDifficulty self D)
      (CallFunction|RefreshStatus self))
    (:CastFailed)))
