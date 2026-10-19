(fn EnterSinkZone (SpeedMult Rate Depth Damage)
  ; called by BP_SinkZone (mud / tar) when the hero walks in
  (Variables|Default|SetHazardSpeedMult SpeedMult)
  (Variables|Default|SetSinkRate Rate)
  (Variables|Default|SetSinkDepth Depth)
  (Variables|Default|SetSinkDamage Damage))
