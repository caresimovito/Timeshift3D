(event EventBeginPlay)

(event Collision|EventActorBeginOverlap (OtherActor)
  (bind h (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object OtherActor)
    (:then
      (Variables|Default|SetOverlappingCharacter h)
      (Class|BPThirdPersonCharacter|SetCurrentInteractable :self h :CurrentInteractable self)
      ; pickups are collected by walking over them (user 2026-10-23: "nothing happens when I walk over it" - they used to
      ; wait for E). Other interactables (the portal) still wait for E.
      (if (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_")
        (CallFunction|Interact self)
        ; the F2 status panel lists what was picked up, newest first - only once it really was (herbs at full health stay)
        (Utilities|IsValid self
          (:"Is Not Valid"
            (Class|BPThirdPersonCharacter|SetPickupLog :self h :PickupLog (Utilities|String|Append (Utilities|String|Append (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_MaxHealth") "max HP egg" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Health") "herbs" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Regen") "regen fern" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Armour") "armour" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Fury") "fury" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Adrenaline") "adrenaline" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Hide") "hide" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Morph") "morph amber" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_KeyArtifact") "KEY PIECE" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_EggLarge") "sauropod egg" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_EggSmall") "nest egg" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Stones") "stones" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Spear") "spear" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_BoneClub") "bone club" (select (Utilities|String|Contains (Utilities|GetObjectName self) "BP_Pickup_Torch") "torch" "pickup"))))))))))))))) "  ") (Class|BPThirdPersonCharacter|GetPickupLog h)))))))
    (:CastFailed)))

(event EventTick (DeltaSeconds))
