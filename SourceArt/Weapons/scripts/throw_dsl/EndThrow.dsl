(fn EndThrow ()
  (Variables|Default|SetIsRangedAttacking false)
  (Variables|Default|SetThrowingBola false)
  (Variables|Default|SetThrowTarget)
  (bind hs (Variables|Default|GetHeldStoneComponent))
  (Utilities|IsValid hs
    (:"Is Valid"
      (Rendering|SetVisibility hs false))
    (:"Is Not Valid")))
