(fn BeginSnareHold ()
  ; a snared enemy is frozen (tick off), so it no longer separates itself from the hero: its invisible blocking cylinder
  ; could pop the hero up onto its top, leaving him standing in mid-air. While snared it ignores the hero (Pawn).
  ; A snared flyer (more than 80 cm above the ground under it) drops - wings tangled - instead of hanging in the air.
  (bind t (Variables|Default|GetSnared))
  (bind tl (Transformation|GetActorLocation t))
  (bind (hit ok) (Collision|LineTraceByChannel :Start tl :End (Math|Vector|MakeVector (.x tl) (.y tl) (- (.z tl) 5000.0)) :ActorsToIgnore (Utilities|Array|MakeArray t)))
  (bind (bb io tm ds hl) (Collision|BreakHitResult hit))
  (if (and ok (> (- (.z tl) (.z hl)) 80.0))
    (Variables|Default|SetSnareGround (.z hl))
    (Variables|Default|SetSnareFallV 0.0)
    (Variables|Default|SetSnareFalling true))
  ; the cast ends the flow, so it goes last
  (bind root (Utilities|Casting|CastToPrimitiveComponent :Object (Actor|GetComponentbyClass t "/Script/Engine.StaticMeshComponent"))
    (:then
      (Collision|SetCollisionResponsetoChannel :self root :Channel "ECC_Pawn" :NewResponse "ECR_Ignore"))
    (:CastFailed)))
