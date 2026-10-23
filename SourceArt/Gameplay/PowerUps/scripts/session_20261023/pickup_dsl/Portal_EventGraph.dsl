(event EventBeginPlay
  ; DORMANT until every key piece is collected (user 2026-10-23: the portal is the big key ring the pieces come from) - the
  ; swirl is hidden; EventTick wakes it. The trigger still works while hidden: E at a dormant portal says how many are left
  (Rendering|SetActorHiddenInGame self true))

(event EventTick (DeltaSeconds)
  (bind now (Utilities|Time|GetGameTimeinSeconds))
  (if (and (not (Variables|Default|GetAwake)) (> now (Variables|Default|GetNextKeyCheck)))
    (Variables|Default|SetNextKeyCheck (+ now 1.0))
    (if (Utilities|Array|IsEmpty (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Interactables/BP_Pickup_KeyArtifact.BP_Pickup_KeyArtifact_C"))
      (Variables|Default|SetAwake true)
      (Rendering|SetActorHiddenInGame self false)
      (Audio|PlaySound2D :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_RexPrime_VictoryRoar.S_RexPrime_VictoryRoar" :VolumeMultiplier 0.5 :PitchMultiplier 1.4)
      (Development|PrintString :InString "The portal awakens - walk into the ring and press E" :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.000000,G=0.900000,B=1.000000,A=1.000000)" :Duration 6.0 :Key "Portal"))))

(event EventInteract
  (bind pc (Game|GetPlayerController 0))
  (bind left (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Interactables/BP_Pickup_KeyArtifact.BP_Pickup_KeyArtifact_C"))
  (if (Utilities|Array|IsEmpty left)
    (if (not (Variables|Default|GetEraComplete))
      (Variables|Default|SetEraComplete true)
      (UserInterface|Viewport|AddtoViewport :self (UserInterface|CreateWidget :Class "/Game/Timeshift/UI/WBP_EraComplete.WBP_EraComplete_C" :OwningPlayer pc))
      (Input|DisableInput :self (Game|GetPlayerCharacter 0) :PlayerController pc)
      (Audio|PlaySound2D :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_RexPrime_VictoryRoar.S_RexPrime_VictoryRoar" :VolumeMultiplier 0.8 :PitchMultiplier 0.85)
      (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "RestartEra" :Time 8.0))
    (else
      (Development|PrintString :InString (Utilities|String|Append (Utilities|String|Append "The portal is dormant. " (Utilities|String|ToString(Integer) (Utilities|Array|Length left))) " key piece(s) still out there.") :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.000000,G=0.660000,B=1.000000,A=1.000000)" :Duration 3.0 :Key "Portal"))))
