(fn Senses (Enemy)
  ; HEARING (user 2026-10-21: "no dinosaurs come near me, they need to investigate"): a hunter / big herbivore that hears
  ; the player beyond its sight range walks over to where it heard him (its roam target), re-aimed every 0.5 s while it can
  ; still hear him; once he is in sight range the normal chase takes over, and if it loses him its roaming drifts it home.
  ; Hearing range = sight range x 2.5 x noise: crouched 0.4, standing 0.5, walking 1, sprinting 1.3. Timid (fleeing),
  ; flying and dying animals do not investigate, and nobody listens in the first 8 s of play.
  (bind now (Utilities|Time|GetGameTimeinSeconds))
  (if (and (> now (Variables|Default|GetNextHearTime)) (> now 8.0))
    (Variables|Default|SetNextHearTime (+ now 0.5))
    (if (not (or (or (or (Class|BPEnemyBase|GetDying Enemy) (Class|BPEnemyBase|GetIsFlying Enemy)) (Class|BPEnemyBase|ShouldFlee Enemy)) (== (Class|BPEnemyBase|GetAnimState Enemy) 2)))
      (bind pl (Game|GetPlayerCharacter 0))
      (bind d (Transformation|GetHorizontalDistanceTo :self Enemy :OtherActor pl))
      (bind det (Class|BPEnemyBase|GetDetectionRange Enemy))
      (bind spd (Math|Vector|VectorLengthXY (Transformation|GetVelocity pl)))
      (bind noise (select (Class|Character|GetIsCrouched pl) 0.4 (select (> spd 450.0) 1.3 (select (> spd 30.0) 1.0 0.5))))
      (if (and (> d det) (< d (* det (* 2.5 noise))))
        (bind pp (Transformation|GetActorLocation pl))
        (bind me (Transformation|GetActorLocation Enemy))
        (Class|BPEnemyBase|SetRoamTarget :self Enemy :RoamTarget (Math|Vector|MakeVector (+ (.x pp) (Math|Random|RandomFloatInRange -250.0 250.0)) (+ (.y pp) (Math|Random|RandomFloatInRange -250.0 250.0)) (.z me)))
        (Class|BPEnemyBase|SetRoamHolding :self Enemy :RoamHolding false)
        (Class|BPEnemyBase|SetNextRoamTime :self Enemy :NextRoamTime (+ now 10.0))
        (Class|BPEnemyBase|SetStuckCheckPos :self Enemy :StuckCheckPos me)
        (Class|BPEnemyBase|SetStuckCheckTime :self Enemy :StuckCheckTime (+ now 3.0))
        (Variables|Default|SetInvestigating true)
        (else
          (Variables|Default|SetInvestigating false))))))
