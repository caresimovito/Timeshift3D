(fn ThrowSwing ()
  (bind anim (Components|SkeletalMesh|GetAnimInstance (Variables|Character|GetMesh)))
  (if (Variables|Default|GetThrowLeft)
    (Animation|Montage|PlaySlotAnimationasDynamicMontage anim "/Game/Timeshift/Characters/Hero/Anims/A_Hero_ThrowL.A_Hero_ThrowL" "DefaultSlot" 0.12 0.3 1.25 :InTimeToStartMontageAt 0.17)
    (else
      (Animation|Montage|PlaySlotAnimationasDynamicMontage anim "/Game/Timeshift/Characters/Hero/Anims/A_Hero_Throw.A_Hero_Throw" "DefaultSlot" 0.12 0.3 1.25 :InTimeToStartMontageAt 0.17))))
