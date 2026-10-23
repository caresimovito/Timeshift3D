(fn AdrenalineFXOn ()
  ; ADRENALINE LOOK v2 (user 2026-10-23: v1 feet-only lightning "i dont like" - wants an electric speedster look with
  ; lightning wrapped over the whole body; original effect, no character costume / emblem copied):
  ;  - NS_AdrenalineBody: random bolts (procedural T_Lightning_4x4, M_Lightning) crawling over all the main bones in
  ;    local space + blue sparks shed in world space, so a glittering trail stays behind him when he runs
  ;  - NS_AdrenalineSpark at each foot: bolts striking the ground, world space -> a crackling trail
  ;  - a cyan point light (AdrenalineLight, made on first use) so the ground and nearby plants glow blue
  ;  - v3 (user reference: thin bright lightning lines running over the whole body): M_ElectricSkin overlay - animated
  ;    lightning lines stuck to his body + faint cyan rim; NS_AdrenalineArcs - long bolts whipping off around / behind
  ;    him (world space); the cyan light sits low so the ground pools blue
  ; v1 (feet only) kept in AdrenalineFXOn_v1_feetonly.dsl.bak
  (bind mesh (Variables|Character|GetMesh))
  (Rendering|Material|SetOverlayMaterial :self mesh :NewOverlayMaterial "/Game/Timeshift/VFX/Adrenaline/MI_ElectricSkin.MI_ElectricSkin")
  (if (== (Utilities|Array|Length (Variables|Default|GetAdrenalineFX)) 0)
    (bind b0 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Adrenaline/NS_AdrenalineBody.NS_AdrenalineBody" :AttachToComponent mesh :AttachPointName "root" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetAdrenalineFX) :NewItem b0)
    (bind a0 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Adrenaline/NS_AdrenalineSpark.NS_AdrenalineSpark" :AttachToComponent mesh :AttachPointName "foot_l" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetAdrenalineFX) :NewItem a0)
    (bind a1 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Adrenaline/NS_AdrenalineSpark.NS_AdrenalineSpark" :AttachToComponent mesh :AttachPointName "foot_r" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetAdrenalineFX) :NewItem a1)
    (bind c0 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Adrenaline/NS_AdrenalineArcs.NS_AdrenalineArcs" :AttachToComponent mesh :AttachPointName "pelvis" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetAdrenalineFX) :NewItem c0))
  (Utilities|IsValid (Variables|Default|GetAdrenalineLight)
    (:"Is Valid"
      (Rendering|SetVisibility (Variables|Default|GetAdrenalineLight) true))
    (:"Is Not Valid"
      (bind al (Utilities|Casting|CastToPointLightComponent :Object (Game|AddComponentbyClass self "/Script/Engine.PointLightComponent"))
        (:then
          (Variables|Default|SetAdrenalineLight al)
          (Rendering|Components|Light|SetLightColor :self al :NewLightColor "(R=0.300000,G=0.650000,B=1.000000,A=1.000000)")
          (Rendering|Components|Light|SetIntensity :self al :NewIntensity 20000.0)
          (Transformation|SetRelativeLocation al (Math|Vector|MakeVector 0.0 0.0 -50.0) false false)
          (Rendering|SetVisibility al true))
        (:CastFailed)))))
