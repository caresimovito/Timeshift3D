(fn StartMorph ()
  ; become a random dinosaur for 30 s: its body, size, speed, attack and health. Its health is the health component's
  ; ARMOUR (absorbs damage first, has a HUD bar), so the hero's own health is untouched; the morph ends early when it
  ; runs out. Everything changed here is saved for EndMorph.
  (Variables|Default|SetMorphCharges (- (Variables|Default|GetMorphCharges) 1))
  (CallFunction|PickMorphSpecies self (Math|Random|RandomIntegerinRange 0 9))
  (CallFunction|EnsureMorphBody self)
  (Variables|Default|SetMorphed true)
  (Variables|Default|SetMorphEnd (+ (Utilities|Time|GetGameTimeinSeconds) 30.0))
  (Variables|Default|SetMorphAttackEnd (+ (Utilities|Time|GetGameTimeinSeconds) 1.6))
  (bind hc (Variables|Default|GetHealthComponent))
  (bind cap (Variables|Character|GetCapsuleComponent))
  (Variables|Default|SetSavedArmour (Class|BPHealthComponent|GetArmour hc))
  (Variables|Default|SetSavedMaxArmour (Class|BPHealthComponent|GetMaxArmour hc))
  (Variables|Default|SetSavedBaseSpeed (Variables|Default|GetBaseWalkSpeed))
  (Variables|Default|SetSavedAttackRange (Variables|Default|GetAttackRange))
  (Variables|Default|SetSavedCapR (Components|Capsule|GetUnscaledCapsuleRadius cap))
  (Variables|Default|SetSavedCapH (Components|Capsule|GetUnscaledCapsuleHalfHeight cap))
  (Variables|Default|SetSavedMeshScale (Class|SceneComponent|GetRelativeScale3D (Variables|Character|GetMesh)))
  (Variables|Default|SetSavedCamLoc (Class|SceneComponent|GetRelativeLocation (Variables|Components|GetFollowCamera)))
  (Class|BPHealthComponent|SetMaxArmour :self hc :MaxArmour (Variables|Default|GetMorphHP))
  (Class|BPHealthComponent|SetArmour :self hc :Armour (Variables|Default|GetMorphHP))
  (Variables|Default|SetBaseWalkSpeed (Variables|Default|GetMorphSpeed))
  (Variables|Default|SetAttackRange (Variables|Default|GetMorphRange))
  ; grow the capsule upwards: lift first so the bigger capsule does not start inside the ground
  (Transformation|AddActorWorldOffset self (Math|Vector|MakeVector 0.0 0.0 (Math|Float|Max(Float) 0.0 (- (Variables|Default|GetMorphHalf) (Variables|Default|GetSavedCapH)))) false false)
  (Components|Capsule|SetCapsuleSize :self cap :InRadius (Variables|Default|GetMorphRadius) :InHalfHeight (Variables|Default|GetMorphHalf) :bUpdateOverlaps true)
  ; the hero shrinks to nothing (so do his attached weapons and pouch); EndMorph restores the saved scale
  (Transformation|SetRelativeScale3D (Variables|Character|GetMesh) (Math|Vector|MakeVector 0.001 0.001 0.001))
  (bind mb (Variables|Default|GetMorphBody))
  ; SetSkinnedAssetAndUpdate + reinit pose: the body is reused across species, and without a pose reset a skeleton with a
  ; different bone layout (Psittacosaurus has an extra root) kept the old pose and collapsed to a point - invisible
  (Components|SkinnedMesh|SetSkinnedAssetandUpdate :self mb :NewMesh (Variables|Default|GetMorphMeshAsset) :bReinitPose true)
  (Transformation|SetRelativeLocation mb (Math|Vector|MakeVector 0.0 0.0 (- (Variables|Default|GetMorphHalf))) false false)
  ; feet fix: Psittacosaurus keeps its armature bone 63 cm below the mesh origin (engine holds it there) - lift by the gap
  (bind msink (- (.z (Transformation|GetWorldLocation mb)) (.z (Transformation|GetSocketLocation mb (Components|SkinnedMesh|GetBoneName mb 0)))))
  (if (> msink 3.0)
    (Transformation|AddWorldOffset mb (Math|Vector|MakeVector 0.0 0.0 msink) false false))
  (Rendering|SetVisibility mb true)
  ; transform with a roar (MorphTick leaves it playing until MorphAttackEnd)
  (Components|Animation|PlayAnimation :self mb :NewAnimToPlay (Variables|Default|GetMorphRoar) :bLooping false)
  (Variables|Default|SetMorphAnimState 2)
  ; camera: the EventGraph re-sets the boom length / socket offset every tick, so pull the CAMERA back along the boom
  ; (and up) instead - nothing else touches its relative location
  (Transformation|SetRelativeLocation (Variables|Components|GetFollowCamera) (Math|Vector|MakeVector (- (.x (Variables|Default|GetSavedCamLoc)) (Variables|Default|GetMorphCamBack)) (.y (Variables|Default|GetSavedCamLoc)) (+ (.z (Variables|Default|GetSavedCamLoc)) (Variables|Default|GetMorphCamUp))) false false)
  (bind feet (Transformation|GetActorLocation self))
  (Niagara|SpawnSystematLocation :SystemTemplate "/Game/Timeshift/Hazards/VFX/NS_RockDust.NS_RockDust" :Location feet :Scale (Math|Vector|MakeVector 2.0 2.0 2.0))
  (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_Creature_RoarPack_03.S_Creature_RoarPack_03" :Location feet :VolumeMultiplier 1.2 :PitchMultiplier (select (< (Variables|Default|GetMorphHP) 150.0) 1.25 0.85))
  (Development|PrintString :InString (Utilities|String|Append "You become a " (Variables|Default|GetMorphName)) :bPrintToScreen true :bPrintToLog true :TextColor "(R=1.000000,G=0.650000,B=0.100000,A=1.000000)" :Duration 3.0)
  (CallFunction|SetTorchHiddenForMorph self true)
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "MorphTick" :Time 0.1 :bLooping true))
