(event AddEvent|EventTick (DeltaSeconds)
  (if (== (Variables|Default|GetPhase) 0)
    (CallFunction|StepFlight self DeltaSeconds)))
