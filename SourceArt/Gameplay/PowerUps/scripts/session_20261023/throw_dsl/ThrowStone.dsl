(fn ThrowStone ()
  (if (and (not (Variables|Default|GetIsRangedAttacking)) (> (select (Variables|Default|GetThrowingBola) (Variables|Default|GetBolaCount) (Variables|Default|GetStoneAmmo)) 0))
    (Variables|Default|SetIsRangedAttacking true)
    (Variables|Default|SetThrowLeft true)   ; one pouch, on the left hip: always throw left-handed
    (bind anim (Components|SkeletalMesh|GetAnimInstance (Variables|Character|GetMesh)))
    (if (Variables|Default|GetThrowLeft)
      (Animation|Montage|PlaySlotAnimationasDynamicMontage anim "/Game/Timeshift/Characters/Hero/Anims/A_Hero_PouchReachL.A_Hero_PouchReachL" "DefaultSlot" 0.15 0.1 1.4 :InTimeToStartMontageAt 0.35)
      (else
        (Animation|Montage|PlaySlotAnimationasDynamicMontage anim "/Game/Timeshift/Characters/Hero/Anims/A_Hero_PouchReach.A_Hero_PouchReach" "DefaultSlot" 0.15 0.1 1.4 :InTimeToStartMontageAt 0.35)))
    (Utilities|Time|SetTimerbyFunctionName self "GrabStone" 0.29)
    (Utilities|Time|SetTimerbyFunctionName self "ThrowSwing" 0.43)
    (Utilities|Time|SetTimerbyFunctionName self "LaunchStone" 0.97)
    (Utilities|Time|SetTimerbyFunctionName self "EndThrow" 1.4)))
