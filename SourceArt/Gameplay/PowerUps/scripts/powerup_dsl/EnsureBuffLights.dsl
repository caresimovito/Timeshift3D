(fn EnsureBuffLights ()
  ; one red (Fury) and one green (Regeneration) point light on the hero, created on first use, hidden when idle
  (Utilities|IsValid (Variables|Default|GetFuryLight)
    (:"Is Valid")
    (:"Is Not Valid"
      (bind fl (Utilities|Casting|CastToPointLightComponent :Object (Game|AddComponentbyClass self "/Script/Engine.PointLightComponent"))
        (:then
          (Variables|Default|SetFuryLight fl)
          (Rendering|Components|Light|SetLightColor :self fl :NewLightColor "(R=1.000000,G=0.120000,B=0.050000,A=1.000000)")
          (Rendering|Components|Light|SetIntensity :self fl :NewIntensity 3000.0)
          (Transformation|SetRelativeLocation fl (Math|Vector|MakeVector 0.0 0.0 40.0) false false)
          (Rendering|SetVisibility fl false)
          (bind gl (Utilities|Casting|CastToPointLightComponent :Object (Game|AddComponentbyClass self "/Script/Engine.PointLightComponent"))
            (:then
              (Variables|Default|SetRegenLight gl)
              (Rendering|Components|Light|SetLightColor :self gl :NewLightColor "(R=0.150000,G=1.000000,B=0.250000,A=1.000000)")
              (Rendering|Components|Light|SetIntensity :self gl :NewIntensity 2500.0)
              (Transformation|SetRelativeLocation gl (Math|Vector|MakeVector 0.0 0.0 20.0) false false)
              (Rendering|SetVisibility gl false))
            (:CastFailed)))
        (:CastFailed)))))
