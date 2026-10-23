(fn DifficultyName ()
  (bind hero (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Game|GetPlayerCharacter 0))
    (:then
      (bind d (Class|BPAttackVariety|GetDifficulty (Class|BPThirdPersonCharacter|GetAttackVariety hero)))
      (return (select (== d 0) "EASY" (select (== d 2) "HARD" "MEDIUM"))))
    (:CastFailed
      (return "MEDIUM"))))
