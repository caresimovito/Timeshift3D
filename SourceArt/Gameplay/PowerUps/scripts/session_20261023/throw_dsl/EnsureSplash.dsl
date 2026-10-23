(fn EnsureSplash ()
  (Utilities|IsValid (Variables|Default|GetSplashComponent)
    (:"Is Valid")
    (:"Is Not Valid"
      (bind n (Niagara|SpawnSystemAttached :SystemTemplate "/Game/Timeshift/VFX/NS_WaterSplash.NS_WaterSplash" :AttachToComponent (Variables|Character|GetMesh) :AttachPointName "None" :Location (Math|Vector|MakeVector 0.0 0.0 0.0) :bAutoDestroy false :bAutoActivate false))
      (Variables|Default|SetSplashComponent n))))
