(fn SetTrappedAnimRate (Rate)
  (bind sk (Utilities|Casting|CastToSkeletalMeshComponent :Object (Actor|GetComponentbyClass (Variables|Default|GetTrapped) "/Script/Engine.SkeletalMeshComponent"))
    (:then
      (Components|Animation|SetPlayRate sk Rate))
    (:CastFailed)))
