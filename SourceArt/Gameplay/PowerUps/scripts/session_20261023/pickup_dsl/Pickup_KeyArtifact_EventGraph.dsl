; only EventInteract: BP_InteractableBase's own overlap collects it on walk-over
(event EventInteract
  ; KEY PIECE (user 2026-10-23): the portal opens once ALL pieces are found (it counts the ones left in the world), so say
  ; how many are found / still out there instead of "take it to the portal" after the first one
  (bind h (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Variables|Default|GetOverlappingCharacter))
    (:then
      (Class|BPThirdPersonCharacter|SetHasKey :self h :bHasKey true)
      (Class|BPThirdPersonCharacter|SetKeyPieces :self h :KeyPieces (+ (Class|BPThirdPersonCharacter|GetKeyPieces h) 1))
      (bind left (- (Utilities|Array|Length (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Interactables/BP_Pickup_KeyArtifact.BP_Pickup_KeyArtifact_C")) 1))
      (bind got (Class|BPThirdPersonCharacter|GetKeyPieces h))
      (if (<= left 0)
        (Development|PrintString :InString (Utilities|String|Append (Utilities|String|Append "ALL " (Utilities|String|ToString(Integer) got)) " KEY PIECES FOUND - take them to the portal!") :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.000000,G=0.900000,B=1.000000,A=1.000000)" :Duration 6.0 :Key "KeyPiece")
        (else
          (Development|PrintString :InString (Utilities|String|Append (Utilities|String|Append (Utilities|String|Append (Utilities|String|Append "Key piece " (Utilities|String|ToString(Integer) got)) " of ") (Utilities|String|ToString(Integer) (+ got left))) (Utilities|String|Append (Utilities|String|Append " found - " (Utilities|String|ToString(Integer) left)) " still out there")) :bPrintToScreen true :bPrintToLog true :TextColor "(R=0.000000,G=0.900000,B=1.000000,A=1.000000)" :Duration 5.0 :Key "KeyPiece")))
      (Actor|DestroyActor self))
    (:CastFailed)))
