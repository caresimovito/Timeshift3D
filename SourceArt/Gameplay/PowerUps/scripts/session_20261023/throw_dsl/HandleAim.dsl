(fn HandleAim ()
  ; hold right mouse to aim: crosshair + camera-facing; R / X throw at the crosshair while held (QuickBola / QuickThrow).
  ; Releasing just stops aiming (it used to throw a stone). Needs stones or bolas - no longer the sling.
  (bind pcon (Game|GetPlayerController 0))
  (bind want (and (and (and (Game|Player|IsInputKeyDown pcon "RightMouseButton") (not (Variables|Default|GetMorphed))) (not (Class|BPHealthComponent|GetIsDead (Variables|Default|GetHealthComponent)))) (or (> (Variables|Default|GetStoneAmmo) 0) (> (Variables|Default|GetBolaCount) 0))))
  (if (xor want (Variables|Default|GetIsAiming))
    (if want
      (Variables|Default|SetIsAiming true)
      (Class|SpringArmComponent|SetTargetArmLength :self (Variables|Components|GetCameraBoom) :TargetArmLength 165.0)
      (Variables|Pawn|SetUseControllerRotationYaw true)
      (Class|CharacterMovementComponent|SetOrientRotationtoMovement :self (Variables|Character|GetCharacterMovement) :bOrientRotationToMovement false)
      (bind w (UserInterface|CreateWidget "/Game/Timeshift/UI/WBP_Crosshair.WBP_Crosshair_C" pcon))
      (Variables|Default|SetCrosshairWidget w)
      (UserInterface|Viewport|AddtoViewport w)
      (else
        (Variables|Default|SetIsAiming false)
        (Class|SpringArmComponent|SetTargetArmLength :self (Variables|Components|GetCameraBoom) :TargetArmLength 300.0)
        (Variables|Pawn|SetUseControllerRotationYaw false)
        (Class|CharacterMovementComponent|SetOrientRotationtoMovement :self (Variables|Character|GetCharacterMovement) :bOrientRotationToMovement true)
        (Utilities|IsValid (Variables|Default|GetCrosshairWidget)
          (:"Is Valid"
            (Widget|RemovefromParent (Variables|Default|GetCrosshairWidget))))))))
