; only EventInteract: with no BeginPlay / overlap / tick overrides here, BP_InteractableBase's own events run (its overlap
; collects pickups on walk-over)
(event EventInteract
  ; nest egg +25 health - at full health it stays where it is for later, like the herbs (2026-10-23)
  (bind hc (Class|BPThirdPersonCharacter|GetHealthComponent (Variables|Default|GetOverlappingCharacter)))
  (if (>= (Class|BPHealthComponent|GetCurrentHealth hc) (Class|BPHealthComponent|GetMaxHealth hc))
    (Development|PrintString :InString "You're at full health - the egg will keep for later" :bPrintToScreen true :bPrintToLog false :TextColor "(R=0.600000,G=1.000000,B=0.600000,A=1.000000)" :Duration 2.0 :Key "NestEgg")
    (else
      (Class|BPHealthComponent|Heal hc 25.0)
      (Development|PrintString :InString "Nest egg  +25 health" :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.400000,G=0.850000,B=1.000000,A=1.000000)" :Duration 3.0 :Key "NestEgg")
      (Actor|DestroyActor self))))

