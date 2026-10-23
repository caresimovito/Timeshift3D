(fn HideFXOff ()
  ; undo HideFXOn
  (bind mesh (Variables|Character|GetMesh))
  (Rendering|Material|SetOverlayMaterial :self mesh :NewOverlayMaterial "None")
  (Utilities|IsValid (Variables|Default|GetHideFX)
    (:"Is Valid"
      (Components|DestroyComponent :self (Variables|Default|GetHideFX))
      (Rendering|Material|SetMaterial :self mesh :ElementIndex 0 :Material (Variables|Default|GetHideSavedMat)))
    (:"Is Not Valid"
      (Rendering|Material|SetMaterial :self mesh :ElementIndex 0 :Material (Variables|Default|GetHideSavedMat)))))
