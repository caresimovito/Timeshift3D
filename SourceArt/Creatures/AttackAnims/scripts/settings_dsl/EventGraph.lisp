(event UserInterface|EventConstruct
  (Widget|SetVisibility (Variables|WBP_Settings|GetDim) "Collapsed")
  (Widget|SetVisibility (Variables|WBP_Settings|GetPanel) "Collapsed")
  (Widget|SetVisibility self "SelfHitTestInvisible")
  (if (and (Development|IsPackagedforDistribution) (not (SaveGame|DoesSaveGameExist "ChronoshiftSettings" 0)))
    (bind g (Settings|GetGameUserSettings))
    (Settings|RunHardwareBenchmark g 10 1.0 1.0)
    (Settings|ApplyHardwareBenchmarkResults g)
    (Settings|ApplySettings g false)
    (Settings|SaveSettings g)
    (SaveGame|SaveGametoSlot (SaveGame|CreateSaveGameObject "/Game/Timeshift/UI/BP_SettingsSave.BP_SettingsSave_C") "ChronoshiftSettings" 0)))

(event UserInterface|EventTick (MyGeometry InDeltaTime)
  (bind pc (Game|GetPlayerController 0))
  (bind down (or (Game|Player|IsInputKeyDown pc "P") (Game|Player|IsInputKeyDown pc "Gamepad_Special_Right")))
  (if (and down (not (Variables|Default|GetKeyWasDown)))
    (if (Variables|Default|GetOpen)
      (CallFunction|CloseMenu self)
      (else
        (CallFunction|OpenMenu self))))
  (Variables|Default|SetKeyWasDown down)
  (if (Variables|Default|GetShowFps)
    (Variables|Default|SetFpsTime (+ (Variables|Default|GetFpsTime) InDeltaTime))
    (Variables|Default|SetFpsCount (+ (Variables|Default|GetFpsCount) 1.0))
    (if (>= (Variables|Default|GetFpsTime) 0.5)
      (Widget|SetText(Text) :self (Variables|WBP_Settings|GetFpsText)
        :InText (Utilities|Text|ToText(String) (Utilities|String|Append "FPS  " (Utilities|String|ToString(Integer) (Math|Float|Round (/ (Variables|Default|GetFpsCount) (Variables|Default|GetFpsTime)))))))
      (Variables|Default|SetFpsTime 0.0)
      (Variables|Default|SetFpsCount 0.0))))

(event OnClicked(BtnLow)
    (Settings|SetOverallScalabilityLevel (Settings|GetGameUserSettings) 0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnMedium)
    (Settings|SetOverallScalabilityLevel (Settings|GetGameUserSettings) 1)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnHigh)
    (Settings|SetOverallScalabilityLevel (Settings|GetGameUserSettings) 2)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnUltra)
    (Settings|SetOverallScalabilityLevel (Settings|GetGameUserSettings) 3)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnAuto)
    (bind g (Settings|GetGameUserSettings))
    (Settings|RunHardwareBenchmark g 10 1.0 1.0)
    (Settings|ApplyHardwareBenchmarkResults g)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(Btn30)
    (Settings|SetFrameRateLimit (Settings|GetGameUserSettings) 30.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(Btn60)
    (Settings|SetFrameRateLimit (Settings|GetGameUserSettings) 60.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(Btn120)
    (Settings|SetFrameRateLimit (Settings|GetGameUserSettings) 120.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnUnlimited)
    (Settings|SetFrameRateLimit (Settings|GetGameUserSettings) 0.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnFullscreen)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "WindowedFullscreen")
    (Settings|SetScreenResolution g (Settings|GetDesktopResolution g))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnWindowed)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "Windowed")
    (Settings|SetScreenResolution g (Utilities|Struct|MakeIntPoint 1600 900))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnVSync)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetVSyncEnabled g (not (Settings|IsVSyncEnabled g)))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnShowFps)
    (Variables|Default|SetShowFps (not (Variables|Default|GetShowFps)))
    (Variables|Default|SetFpsTime 0.0)
    (Variables|Default|SetFpsCount 0.0)
    (if (Variables|Default|GetShowFps)
      (Widget|SetVisibility (Variables|WBP_Settings|GetFpsText) "HitTestInvisible")
      (else
        (Widget|SetVisibility (Variables|WBP_Settings|GetFpsText) "Collapsed"))))

(event OnClicked(BtnResume)
    (CallFunction|CloseMenu self))

(event OnClicked(BtnQuit)
    (Game|QuitGame (Game|GetPlayerController 0) "Quit" false))

(event OnClicked(BtnR720)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "Windowed")
    (Settings|SetScreenResolution g (Utilities|Struct|MakeIntPoint 1280 720))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnR900)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "Windowed")
    (Settings|SetScreenResolution g (Utilities|Struct|MakeIntPoint 1600 900))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnR1080)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "Windowed")
    (Settings|SetScreenResolution g (Utilities|Struct|MakeIntPoint 1920 1080))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnR1440)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "Windowed")
    (Settings|SetScreenResolution g (Utilities|Struct|MakeIntPoint 2560 1440))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnRNative)
    (bind g (Settings|GetGameUserSettings))
    (Settings|SetFullscreenMode g "WindowedFullscreen")
    (Settings|SetScreenResolution g (Settings|GetDesktopResolution g))
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnS50)
    (Settings|SetResolutionScaleValue (Settings|GetGameUserSettings) 50.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnS67)
    (Settings|SetResolutionScaleValue (Settings|GetGameUserSettings) 67.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnS75)
    (Settings|SetResolutionScaleValue (Settings|GetGameUserSettings) 75.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnS100)
    (Settings|SetResolutionScaleValue (Settings|GetGameUserSettings) 100.0)
    (CallFunction|ApplyAndRefresh self))

(event OnClicked(BtnEasy)
    (CallFunction|SetDifficulty self 0))

(event OnClicked(BtnNormal)
    (CallFunction|SetDifficulty self 1))

(event OnClicked(BtnHard)
    (CallFunction|SetDifficulty self 2))
