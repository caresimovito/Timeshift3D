(fn HeroFx ()
  (CallFunction|LoadDifficulty self)
  (bind h (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Components|GetOwner self))
    (:then
      (Variables|Default|SetIsHero true)
      (Variables|Default|SetOwnerHero h)
      (CallFunction|MoveFx self (and (Class|BPThirdPersonCharacter|GetMorphed h) (== (Class|BPThirdPersonCharacter|GetMorphAnimState h) 2))))
    (:CastFailed)))
