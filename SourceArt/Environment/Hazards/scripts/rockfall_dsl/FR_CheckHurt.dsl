(fn CheckHurt ()
  ; a moving boulder that reaches the hero hits him once: a shove away from the rock + damage
  (bind pc (Game|GetPlayerCharacter 0))
  (if (and (not (Variables|Default|GetHurt)) (> (Math|Vector|VectorLength (Variables|Default|GetVel)) 250.0))
    (if (< (Math|Vector|Distance(Vector) (Transformation|GetActorLocation self) (Transformation|GetActorLocation pc)) (+ (* 110.0 (Variables|Default|GetScale)) 55.0))
      (Variables|Default|SetHurt true)
      (bind away (Math|Vector|Normalize (Math|Vector|MakeVector (- (.x (Transformation|GetActorLocation pc)) (.x (Transformation|GetActorLocation self))) (- (.y (Transformation|GetActorLocation pc)) (.y (Transformation|GetActorLocation self))) 0.0)))
      (Character|LaunchCharacter pc (Math|Vector|MakeVector (* (.x away) 400.0) (* (.y away) 400.0) 220.0) true true)
      (Development|PrintString "Hit by a falling rock!" true true "(R=1.000000,G=0.700000,B=0.400000,A=1.000000)" 1.2)
      ; the cast ends the flow, so it goes last
      (bind hc (Utilities|Casting|CastToBP_HealthComponent :Object (Actor|GetComponentbyClass pc "/Game/Timeshift/Components/BP_HealthComponent.BP_HealthComponent_C"))
        (:then
          (Class|BPHealthComponent|ApplyDamage hc (Variables|Default|GetDamage)))
        (:CastFailed)))))
