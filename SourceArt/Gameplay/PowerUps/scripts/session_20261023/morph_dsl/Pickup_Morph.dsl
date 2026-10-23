; only the interact event: BeginPlay / overlap / tick are inherited from BP_InteractableBase
(event EventInteract
  (Class|BPThirdPersonCharacter|AddMorphCharge :self (Variables|Default|GetOverlappingCharacter))
  (Actor|DestroyActor self))
