(fn BurstTick ()
  (bind arr (Collision|GetOverlappingActors self))
  (for a arr
    (CallFunction|HitActor self a)))
