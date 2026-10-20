(fn SetSnareAnimRate (Rate)
  (bind t (Variables|Default|GetSnared))
  (bind sk (Utilities|Casting|CastToSkeletalMeshComponent :Object (Actor|GetComponentbyClass t "/Script/Engine.SkeletalMeshComponent"))
    (:then
      (Components|Animation|SetPlayRate sk Rate))
    (:CastFailed)))
