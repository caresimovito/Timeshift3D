(fn SetHazardSpeed (Mult)
  ; BP_HazardZone calls this instead of setting MaxWalkSpeed (UpdateWading owns MaxWalkSpeed and multiplies this in)
  (Variables|Default|SetHazardSpeedMult Mult))
