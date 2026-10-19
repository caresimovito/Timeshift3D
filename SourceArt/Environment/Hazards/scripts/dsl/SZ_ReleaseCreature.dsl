(fn ReleaseCreature ()
  (bind t (Variables|Default|GetTrapped))
  (Utilities|IsValid t
    (:"Is Valid"
      (Actor|Tick|SetActorTickEnabled t true)
      (CallFunction|SetTrappedAnimRate self 1.0)
      (Variables|Default|SetTrapped))
    (:"Is Not Valid")))
