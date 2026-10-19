(event AddEvent|EventBeginPlay ()
  ; stagger vents so they don't all fire together
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "StartWarning" :Time (Math|Random|RandomFloatinRange 1.0 (Variables|Default|GetIdleMax)) :bLooping false))

(event Collision|EventActorBeginOverlap (OtherActor)
  ; walking into the column mid-burst also scalds
  (CallFunction|HitActor self OtherActor))
