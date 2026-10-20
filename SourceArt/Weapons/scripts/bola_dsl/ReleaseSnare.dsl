(fn ReleaseSnare ()
  (Variables|Default|SetSnareFalling false)
  (bind t (Variables|Default|GetSnared))
  (Utilities|IsValid t
    (:"Is Valid"
      (Actor|Tick|SetActorTickEnabled t true)
      (CallFunction|SetSnareAnimRate self 1.0)
      ; give the enemy its blocking cylinder back (its root SM_Cylinder is its only StaticMeshComponent; BeginSnareHold set it to ignore the hero)
      (bind root (Utilities|Casting|CastToPrimitiveComponent :Object (Actor|GetComponentbyClass t "/Script/Engine.StaticMeshComponent"))
        (:then
          (Collision|SetCollisionResponsetoChannel :self root :Channel "ECC_Pawn" :NewResponse "ECR_Block")
          (Actor|DestroyActor self))
        (:CastFailed
          (Actor|DestroyActor self))))
    (:"Is Not Valid"
      (Actor|DestroyActor self))))
