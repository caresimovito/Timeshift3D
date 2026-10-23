(fn FuryFXOn ()
  ; FURY LOOK (user 2026-10-23 reference image: normal clothes, tall flames off the back / shoulders / arms / hands / boots,
  ; a dark smoke plume, the whole spear burning, embers everywhere) - no new artwork:
  ;  - NS_FuryAura bound to the body: Niagara SkeletalMeshLocation, Random (Filtered Bones) - spine_03-05, neck, clavicles,
  ;    upper / lower arms, hands, calves, feet - 200 flames/s, 18-40 cm, rising fast, with embers
  ;  - NS_LavaSmoke at the head (x0.3) for the dark plume
  ;  - NS_FurySpearFire (a bigger torch flame) at 5 points along the spear in his hand (its long axis is local Z, -31..169),
  ;    only while that spear is shown
  ;  - the flickering orange light. No body overlay any more (v1-v4 turned his clothes into orange speckle).
  ; FuryTick fades the FuryPP screen effect in / out; FuryFXOff removes it all.
  (bind mesh (Variables|Character|GetMesh))
  (Rendering|Components|Light|SetLightColor :self (Variables|Default|GetFuryLight) :NewLightColor "(R=1.000000,G=0.350000,B=0.080000,A=1.000000)")
  (if (== (Utilities|Array|Length (Variables|Default|GetFuryFX)) 0)
      (bind f0 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FuryAura.NS_FuryAura" :AttachToComponent mesh :AttachPointName "root" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
      (Transformation|SetRelativeScale3D f0 (Math|Vector|MakeVector 1.00 1.00 1.00))
      (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f0)
      (bind f1 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/NS_LavaSmoke.NS_LavaSmoke" :AttachToComponent mesh :AttachPointName "head" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
      (Transformation|SetRelativeScale3D f1 (Math|Vector|MakeVector 0.30 0.30 0.30))
      (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f1)
      (bind spear (Variables|Default|GetSpearMeshComponent))
      (if (and (Variables|Default|GetHasSpear) (Rendering|IsVisible spear))
        (bind f10 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 10.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
        (Transformation|SetRelativeScale3D f10 (Math|Vector|MakeVector 1.00 1.00 1.00))
        (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f10)
        (bind f11 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 50.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
        (Transformation|SetRelativeScale3D f11 (Math|Vector|MakeVector 1.00 1.00 1.00))
        (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f11)
        (bind f12 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 90.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
        (Transformation|SetRelativeScale3D f12 (Math|Vector|MakeVector 1.00 1.00 1.00))
        (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f12)
        (bind f13 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 125.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
        (Transformation|SetRelativeScale3D f13 (Math|Vector|MakeVector 1.00 1.00 1.00))
        (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f13)
        (bind f14 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 160.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
        (Transformation|SetRelativeScale3D f14 (Math|Vector|MakeVector 1.00 1.00 1.00))
        (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f14)))
  (bind pps (Actor|GetAllActorsWithTag :Tag "FuryPP"))
  (if (> (Utilities|Array|Length pps) 0)
    (Variables|Default|SetFuryPP (Utilities|Casting|CastToPostProcessVolume :Object (Utilities|Array|Get(acopy) pps 0)))))
