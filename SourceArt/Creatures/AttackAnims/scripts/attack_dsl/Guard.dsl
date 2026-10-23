(fn Guard (Enemy)
  ; MOVEMENT GUARD (user 2026-10-21: "dinosaurs walking through trees"): enemies move by SetActorLocation without a
  ; sweep, so roaming / chasing / fleeing all slid through trunks and rocks. Each tick, sweep a sphere at body height
  ; along the step just taken; if it hit a tree / rock / wall (not the landscape, not another dinosaur or the player),
  ; put the enemy back on its last good spot and slide it along the obstacle so it works its way round.
  (bind cur (Transformation|GetActorLocation Enemy))
  (if (not (Variables|Default|GetGuardInit))
    (Variables|Default|SetGuardInit true)
    (Variables|Default|SetIgnoreList (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Enemies/BP_EnemyBase.BP_EnemyBase_C"))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetIgnoreList) :NewItem (Game|GetPlayerCharacter 0))
    (Variables|Default|SetLastGood cur)
    ; FEET FIX (user 2026-10-21: "dino is in the ground"): some Blender skeletons (Psittacosaurus, Caudipteryx) keep their
    ; armature bone below the mesh origin and the engine holds it there whatever the clips say, so the body sank 40-60 cm.
    ; Measure where that first bone really is and lift the body by the gap (0 for species that stand right).
    (bind body (Class|BPEnemyBase|GetBody Enemy))
    (bind sink (- (.z (Transformation|GetWorldLocation body)) (.z (Transformation|GetSocketLocation body (Components|SkinnedMesh|GetBoneName body 0)))))
    (if (> sink 3.0)
      (Transformation|AddWorldOffset body (Math|Vector|MakeVector 0.0 0.0 sink) false false))
    (else
      (bind last (Variables|Default|GetLastGood))
      (bind dx (- (.x cur) (.x last)))
      (bind dy (- (.y cur) (.y last)))
      (bind dl (Math|Vector|VectorLengthXY (Math|Vector|MakeVector dx dy 0.0)))
      ; only real steps: not standing still, not a teleport / big knockback, not flyers
      (if (and (and (> dl 1.0) (< dl 400.0)) (not (Class|BPEnemyBase|GetIsFlying Enemy)))
        (bind r (Math|Float|Clamp(Float) (* 0.5 (Class|BPEnemyBase|GetBodyRadius Enemy)) 15.0 60.0))
        (bind h (+ r 35.0))
        (bind (hit ok) (Collision|SphereTraceByChannel :Start (Math|Vector|MakeVector (.x last) (.y last) (+ (.z cur) h)) :End (Math|Vector|MakeVector (.x cur) (.y cur) (+ (.z cur) h)) :Radius r :ActorsToIgnore (Variables|Default|GetIgnoreList)))
        (bind (hb hio ht hd hl hip hn hin hpm hha hhc) (Collision|BreakHitResult hit))
        (if (and (and ok (not hio)) (not (Utilities|String|Contains (Utilities|GetDisplayName hhc) "Landscape")))
          ; slide = step minus its part going into the obstacle (impact normal, flattened), plus 1 cm clearance
          (bind nx (.x hin))
          (bind ny (.y hin))
          (bind nn (Math|Float|Max(Float) (+ (* nx nx) (* ny ny)) 0.0001))
          (bind into (Math|Float|Min(Float) (/ (+ (* dx nx) (* dy ny)) nn) 0.0))
          (bind inv (/ 1.0 (Math|Float|Sqrt nn)))
          (Transformation|SetActorLocation Enemy (Math|Vector|MakeVector (+ (+ (.x last) (- dx (* nx into))) (* nx inv)) (+ (+ (.y last) (- dy (* ny into))) (* ny inv)) (.z cur)) false false)))
      (Variables|Default|SetLastGood (Transformation|GetActorLocation Enemy)))))
