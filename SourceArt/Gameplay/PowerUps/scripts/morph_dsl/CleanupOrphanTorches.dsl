(fn CleanupOrphanTorches ()
  ; EquipTorch (I key, torch pickups) adds a NEW torch mesh + light + flame every time and never removes the old one,
  ; leaving unlit torches stuck to the hero. Remove every SM_Torch mesh that is not the current TorchMeshComponent.
  (bind arr (Actor|GetComponentsByClass self "/Script/Engine.StaticMeshComponent"))
  (for c arr
    (CallFunction|RemoveIfOrphanTorch self c)))
