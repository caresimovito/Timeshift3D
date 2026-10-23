(fn SaveDifficulty (D)
  (if (SaveGame|DoesSaveGameExist "ChronoshiftSettings" 0)
    (bind s1 (Utilities|Casting|CastToBP_SettingsSave :Object (SaveGame|LoadGamefromSlot "ChronoshiftSettings" 0))
      (:then
        (Class|BPSettingsSave|SetDifficulty :self s1 :Difficulty D)
        (SaveGame|SaveGametoSlot s1 "ChronoshiftSettings" 0))
      (:CastFailed))
    (else
      (bind s2 (Utilities|Casting|CastToBP_SettingsSave :Object (SaveGame|CreateSaveGameObject "/Game/Timeshift/UI/BP_SettingsSave.BP_SettingsSave_C"))
        (:then
          (Class|BPSettingsSave|SetDifficulty :self s2 :Difficulty D)
          (SaveGame|SaveGametoSlot s2 "ChronoshiftSettings" 0))
        (:CastFailed)))))
