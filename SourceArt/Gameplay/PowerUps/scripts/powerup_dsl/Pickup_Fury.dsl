; only the interact event: BeginPlay / overlap / tick are inherited from BP_InteractableBase (the DSL can't create
; 'call parent' nodes, and leaving the events out runs the base versions)
(event EventInteract
  (Class|BPThirdPersonCharacter|StartFury :self (Variables|Default|GetOverlappingCharacter) :Duration 15.0)
  (Actor|DestroyActor self))
