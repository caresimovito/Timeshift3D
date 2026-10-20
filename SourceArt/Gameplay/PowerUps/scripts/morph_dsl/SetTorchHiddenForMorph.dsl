(fn SetTorchHiddenForMorph (Hide)
  ; every torch mesh on the hero, not just TorchMeshComponent: EquipTorch adds a NEW torch component each time it runs
  ; (I key, torch pickups) and never removes the old one, so unlit "orphan" torches stay stuck to the capsule.
  ; HiddenInGame is a separate flag from the visibility ApplyWeaponSelection / TorchBurnOut drive.
  (bind arr (Actor|GetComponentsByClass self "/Script/Engine.StaticMeshComponent"))
  (for c arr
    (CallFunction|HideIfTorch self c Hide)))
