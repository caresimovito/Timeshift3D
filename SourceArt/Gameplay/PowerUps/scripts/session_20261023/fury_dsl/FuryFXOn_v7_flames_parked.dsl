(fn FuryFXOn ()
  ; FURY v7 (user 2026-10-23: v6 flames "not even attached to him and way too many" -> new Gemini concept
  ; "Prehistoric Explorer VFX Concept Art": small tight flames clinging to the shoulders and forearms, one thin line of
  ; fire along the spear, few embers, nothing at the feet). Emitters are LOCAL SPACE now, so the fire stays on him
  ; when he runs; M_FuryFlame is additive so the small tongues merge. v6 kept in FuryFXOn_v6.dsl.bak.
  ; FURY LOOK v6 (user 2026-10-23: "build fury like the gemini concept" - flames off the shoulders / back / forearms,
  ; whole spear burning, embers, smoke plume, fire at the boots, clothes stay readable):
  ;  - NS_FuryAura on the body: SkeletalMeshLocation Random (Filtered Bones) - spine_04-05, clavicles, upper / lower arms,
  ;    hands only (legs dropped) - flame TONGUES now: M_FuryFlame = procedural 8x8 flipbook T_FuryFlame_8x8
  ;    (SourceArt/VFX, made by make_flame_flipbook.py), velocity-aligned so they lick upward / trail when running
  ;  - (head smoke removed - user screenshot showed it as a bright blob on his head)
  ;  - NS_FurySpearFire at 5 points along the spear (long axis local Z, -31..169), only while that spear is shown
  ;  - NS_FurySpearFire (x1) at each foot for the burning ground at his boots
  ;  - the flickering orange light. No body overlay (v1-v4 turned his clothes into orange speckle).
  ; v5 (glowing blobs, user disliked) kept in FuryFXOn_v5_parked.dsl. FuryTick fades FuryPP; FuryFXOff removes it all.
  (bind mesh (Variables|Character|GetMesh))
  ; remember which weapon the fire was built for (ApplyWeaponSelection rebuilds on a switch)
  (Variables|Default|SetFuryFXWeapon (Variables|Default|GetCurrentWeaponIndex))
  (Rendering|Components|Light|SetLightColor :self (Variables|Default|GetFuryLight) :NewLightColor "(R=1.000000,G=0.350000,B=0.080000,A=1.000000)")
  ; FURY GLOW option (dev key '-', user: "cant we just use like a fiery glow?"): no particles - hot orange rim +
  ; faint ember warmth on the body (M_FuryGlow overlay), red-hot spear (MI_FuryGlowSpear overlay), the orange light
  (if (Variables|Default|GetFuryGlowStyle)
    (Rendering|Material|SetOverlayMaterial :self mesh :NewOverlayMaterial "/Game/Timeshift/VFX/Fury/M_FuryGlow.M_FuryGlow")
    (Rendering|Material|SetOverlayMaterial :self (Variables|Default|GetSpearMeshComponent) :NewOverlayMaterial "/Game/Timeshift/VFX/Fury/MI_FuryGlowSpear.MI_FuryGlowSpear")
    (else
      (if (== (Utilities|Array|Length (Variables|Default|GetFuryFX)) 0)
          (bind f0 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FuryAura.NS_FuryAura" :AttachToComponent mesh :AttachPointName "root" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "SnapToTarget" :bAutoDestroy false))
          (Transformation|SetRelativeScale3D f0 (Math|Vector|MakeVector 1.00 1.00 1.00))
          (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f0)
          (bind spear (Variables|Default|GetSpearMeshComponent))
          (if (and (Variables|Default|GetHasSpear) (Rendering|IsVisible spear))
            (bind f10 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 -20.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f10)
            (bind f11 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f11)
            (bind f12 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 20.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f12)
            (bind f13 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 40.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f13)
            (bind f14 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 60.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f14)
            (bind f15 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 80.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f15)
            (bind f16 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 100.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f16)
            (bind f17 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 120.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f17)
            (bind f18 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 140.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f18)
            (bind f19 (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/Fury/NS_FurySpearFire.NS_FurySpearFire" :AttachToComponent spear :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 160.0) :LocationType "KeepRelativeOffset" :bAutoDestroy false))
            (Utilities|Array|Add :TargetArray (Variables|Default|GetFuryFX) :NewItem f19)))))
  (bind pps (Actor|GetAllActorsWithTag :Tag "FuryPP"))
  (if (> (Utilities|Array|Length pps) 0)
    (Variables|Default|SetFuryPP (Utilities|Casting|CastToPostProcessVolume :Object (Utilities|Array|Get(acopy) pps 0)))))
