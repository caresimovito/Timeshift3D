(fn EnsureMorphBody ()
  ; the dinosaur body: a skeletal mesh on the capsule, created on first use, hidden when not morphed
  (Utilities|IsValid (Variables|Default|GetMorphBody)
    (:"Is Valid")
    (:"Is Not Valid"
      (bind mb (Utilities|Casting|CastToSkeletalMeshComponent :Object (Game|AddComponentbyClass self "/Script/Engine.SkeletalMeshComponent"))
        (:then
          (Variables|Default|SetMorphBody mb)
          ; purely visual: its physics bodies must never collide (they shoved the hero metres into the air)
          (Collision|SetCollisionEnabled mb "NoCollision")
          (Rendering|SetVisibility mb false))
        (:CastFailed)))))
