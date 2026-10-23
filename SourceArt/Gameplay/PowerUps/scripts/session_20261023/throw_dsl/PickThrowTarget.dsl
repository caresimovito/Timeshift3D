(fn PickThrowTarget ()
  ; quick throws (X / R): auto-aim at the nearest dinosaur within ~30 deg of facing and 25 m
  (Variables|Default|SetThrowTarget)
  (Variables|Default|SetThrowTargetScore 2500.0)
  (bind arr (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Enemies/BP_EnemyBase.BP_EnemyBase_C"))
  (for e arr
    (CallFunction|ConsiderThrowTarget self e))
  (bind tgt (Variables|Default|GetThrowTarget))
  (Utilities|IsValid tgt
    (:"Is Valid"
      (Transformation|SetActorRotation self (Math|Rotator|MakeRotator :Roll 0.0 :Pitch 0.0 :Yaw (.yaw (Math|Rotator|FindLookatRotation (Transformation|GetActorLocation self) (Transformation|GetActorLocation tgt)))) false))
    (:"Is Not Valid")))
