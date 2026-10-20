(fn SetTorchHiddenForMorph (Hide)
  ; the torch mesh is added straight to the capsule (EquipTorch), so shrinking the hero's mesh doesn't hide it; its light
  ; and flame are attached to it. HiddenInGame is a separate flag from the visibility ApplyWeaponSelection drives.
  (Utilities|IsValid (Variables|Default|GetTorchMeshComponent)
    (:"Is Valid"
      (Development|SetHiddeninGame :self (Variables|Default|GetTorchMeshComponent) :NewHidden Hide :bPropagateToChildren true))
    (:"Is Not Valid")))
