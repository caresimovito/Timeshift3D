(fn GrabStone ()
  (bind hs (Variables|Default|GetHeldStoneComponent))
  (Utilities|IsValid hs
    (:"Is Valid"
      (CallFunction|AttachHeldStone self))
    (:"Is Not Valid"
      (bind c (Game|AddComponentbyClass self "/Script/Engine.StaticMeshComponent"))
      (Variables|Default|SetHeldStoneComponent c)
      (Components|StaticMesh|SetStaticMesh c "/Game/Timeshift/Environment/Meshes/RiverBoulder/SM_RiverBoulder_01.SM_RiverBoulder_01")
      (Collision|SetCollisionEnabled c "NoCollision")
      (CallFunction|AttachHeldStone self))))
