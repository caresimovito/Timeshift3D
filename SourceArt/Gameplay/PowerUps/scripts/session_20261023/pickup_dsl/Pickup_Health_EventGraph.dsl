; only EventInteract: with no BeginPlay / overlap / tick overrides here, BP_InteractableBase's own events run (its overlap
; collects pickups on walk-over)
(event EventInteract
  ; healing herbs +40 - but at full health they stay where they are for later (user 2026-10-23)
  (bind hc (Class|BPThirdPersonCharacter|GetHealthComponent (Variables|Default|GetOverlappingCharacter)))
  (if (>= (Class|BPHealthComponent|GetCurrentHealth hc) (Class|BPHealthComponent|GetMaxHealth hc))
    (Development|PrintString :InString "You're at full health - the herbs will keep for later" :bPrintToScreen true :bPrintToLog false :TextColor "(R=0.600000,G=1.000000,B=0.600000,A=1.000000)" :Duration 2.0 :Key "Herbs")
    (else
      (Class|BPHealthComponent|Heal hc 40.0)
      (Development|PrintString :InString "Healing herbs  +40 health" :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.200000,G=1.000000,B=0.400000,A=1.000000)" :Duration 3.0 :Key "Herbs")
      (Actor|DestroyActor self))))

