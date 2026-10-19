(fn TrapCreature (A)
  ; tar only: a dinosaur that wades in gets stuck (logic paused, anim slowed) for 4 s and takes damage
  (if (Variables|Default|GetIsTar)
    (bind hc (Utilities|Casting|CastToBP_HealthComponent :Object (Actor|GetComponentbyClass A "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C"))
      (:then
        (Variables|Default|SetTrapped A)
        (Class|BPHealthComponent|ApplyDamage hc 10.0)
        (Actor|Tick|SetActorTickEnabled A false)
        (CallFunction|SetTrappedAnimRate self 0.3)
        (Utilities|Time|SetTimerbyFunctionName self "ReleaseCreature" 4.0))
      (:CastFailed))))
