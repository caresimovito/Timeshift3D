# Generates BP_AttackVariety's graphs (Saved/attack_dsl). The component sits on BP_EnemyBase and watches its owner:
#  - AnimState turns 2 (attack started, UpdateBodyAnim just played the species' Attack clip): roll 0..N; 0 keeps the bite,
#    1..N swaps in one of the species' authored moves and pushes AttackEndTime so UpdateBodyAnim lets it finish
#  - bHasBeenProvoked turns true (it has spotted the player): play the species' Roar
# Flyers have no entries, so they are left alone.
D = r"C:/repos/Unreal Projects/Timeshift3D/Saved/attack_dsl/"
MOVES = {"Raptor": ["Pounce", "TailSwipe", "Frenzy", "Slash", "Sidestep"],
         "Dilophosaurus": ["Pounce", "TailSwipe", "Frenzy", "Slash", "Sidestep"],
         "Compy": ["Pounce", "TailSwipe", "Frenzy", "Slash", "Sidestep"],
         "Caudipteryx": ["Pounce", "TailSwipe", "Frenzy", "Slash", "Sidestep"],
         "Kulindadromeus": ["Pounce", "TailSwipe", "Sidestep"], "RiverAmbusher": ["Pounce", "TailSwipe", "Frenzy", "Stomp"],
         "Triceratops": ["Charge", "Gore", "Stomp"], "Psittacosaurus": ["Charge", "Gore", "Sidestep"],
         "Archaeoceratops": ["Charge", "Gore", "Sidestep"], "Parasaurolophus": ["Charge", "TailSwipe", "Gore", "Stomp"],
         "Spinosaurus": ["Charge", "TailSwipe", "Frenzy", "Slash"], "Ankylosaurus": ["Charge", "TailSwipe", "Gore", "Stomp"],
         "Stegosaurus": ["TailSwipe", "Stomp"]}
LEN = {"Pounce": 1.0, "TailSwipe": 1.1, "Charge": 1.0, "Roar": 1.6, "Stomp": 1.2, "Gore": 0.9, "Frenzy": 1.0, "Slash": 0.9,
       "Sidestep": 1.1}


def path(sp, clip):
    n = "SK_%s_Anim_SK_%s_%s" % (sp, sp, clip)
    return "/Game/Timeshift/Enemies/%s/%s.%s" % (sp, n, n)


def chain(branches, default):
    """nest (if c1 body1 (elif c2 body2 (elif ... (else default)))) - elif/else must be the last form of the previous body"""
    out = default
    for cond, body in reversed(branches):
        out = "(if %s\n%s\n%s)" % (cond, body, out) if out == default and default.startswith("(if") else None
    # build manually
    s = ""
    close = 0
    for i, (cond, body) in enumerate(branches):
        s += ("(if %s\n" if i == 0 else "(elif %s\n") % cond + body + "\n"
        close += 1
    s += default + ")" * close
    return s


# MoveCount(Species) -> number of extra moves
br = [('(Utilities|String|EqualExactly(String) Species "%s")' % sp, "  (return %d)" % len(m)) for sp, m in MOVES.items()]
s = "(fn MoveCount (Species)\n  ; how many authored attack moves this species has (0 = none / flyer)\n"
for cond, body in br:
    s += "  (if %s\n  %s)\n" % (cond, body)
s += "  (return 0))\n"
open(D + "MoveCount.dsl", "w").write(s)

# PlayMove(Body, Species, Move): Move 1..N = authored moves, 9 = Roar; returns the clip length
s = "(fn PlayMove (Body Species Move)\n  ; plays the chosen clip on the enemy's Body; returns its length (0 if nothing played)\n"
for sp, m in MOVES.items():
    s += '  (if (Utilities|String|EqualExactly(String) Species "%s")\n' % sp
    for i, mv in enumerate(m, start=1):
        # an authored move (not the roar) also starts its hit timeline - see MoveFx
        s += '    (if (== Move %d)\n      (Variables|Default|SetCurMove "%s")\n      (Variables|Default|SetMoveStart (Utilities|Time|GetGameTimeinSeconds))\n      (Variables|Default|SetHitsDone 0)\n' % (i, mv)
        s += '      (Components|Animation|PlayAnimation :self Body :NewAnimToPlay "%s" :bLooping false)\n      (return %.2f))\n' % (path(sp, mv), LEN[mv])
    s += '    (if (== Move 9)\n      (Components|Animation|PlayAnimation :self Body :NewAnimToPlay "%s" :bLooping false)\n      (return %.2f)))\n' % (path(sp, "Roar"), LEN["Roar"])
s += "  (return 0.0))\n"
open(D + "PlayMove.dsl", "w").write(s)

# Tick: enemies pick moves (Watch) and run the hit timeline; on the hero (morph) only the hit timeline runs
s = """(event AddEvent|EventBeginPlay
  ; tick after the owner has moved this frame, so Guard sees (and can undo) the move
  (Components|Tick|AddTickPrerequisiteActor :self self :PrerequisiteActor (Components|GetOwner self)))

(event AddEvent|EventTick (DeltaSeconds)
  (bind eb (Utilities|Casting|CastToBP_EnemyBase :Object (Components|GetOwner self))
    (:then
      (Variables|Default|SetIsHero false)
      (Variables|Default|SetOwnerEnemy eb)
      (CallFunction|Guard self eb)
      (CallFunction|ApplyDifficulty self eb)
      (CallFunction|Watch self eb)
      (CallFunction|Senses self eb)
      (CallFunction|FlyerAnim self eb)
      (CallFunction|MoveFx self (== (Class|BPEnemyBase|GetAnimState eb) 2)))
    (:CastFailed
      (CallFunction|HeroFx self))))
"""
open(D + "EventGraph.dsl", "w").write(s)
s = """(fn Watch (Enemy)
  (bind st (Class|BPEnemyBase|GetAnimState Enemy))
  (bind sp (Class|BPEnemyBase|GetSpecies Enemy))
  ; the player comes within its detection range -> roar once (re-armed when he is well clear again). bHasBeenProvoked
  ; was tried first, but it only flips when the PLAYER hits a passive animal - hunters attack without it
  (Variables|Default|SetPlayerDist (Math|Vector|Distance(Vector) (Transformation|GetActorLocation Enemy) (Transformation|GetActorLocation (Game|GetPlayerCharacter 0))))
  (if (and (< (Variables|Default|GetPlayerDist) (Class|BPEnemyBase|GetDetectionRange Enemy)) (not (Variables|Default|GetWasProvoked)))
    (Variables|Default|SetWasProvoked true)
    (Variables|Default|SetMoveLen (CallFunction|PlayMove self (Class|BPEnemyBase|GetBody Enemy) sp 9))
    (if (> (Variables|Default|GetMoveLen) 0.0)
      (Class|BPEnemyBase|SetAttackEndTime :self Enemy :AttackEndTime (+ (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveLen)))))
  (if (> (Variables|Default|GetPlayerDist) (* 1.6 (Class|BPEnemyBase|GetDetectionRange Enemy)))
    (Variables|Default|SetWasProvoked false))
  ; attack just started -> maybe swap in one of the species' moves (0 keeps the original bite)
  (if (and (== st 2) (!= (Variables|Default|GetLastState) 2))
    (Variables|Default|SetPick (Math|Random|RandomIntegerinRange 0 (CallFunction|MoveCount self sp)))
    (if (> (Variables|Default|GetPick) 0)
      (Variables|Default|SetMoveLen (CallFunction|PlayMove self (Class|BPEnemyBase|GetBody Enemy) sp (Variables|Default|GetPick)))
      (if (> (Variables|Default|GetMoveLen) 0.0)
        (Class|BPEnemyBase|SetAttackEndTime :self Enemy :AttackEndTime (+ (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveLen)))
        ; its next attack waits for the move to finish: UpdateBodyAnim never holds an attack, so a cooldown shorter than the
        ; move (Raptor 0.8 s vs Frenzy 1.0 s) would bite over it and cut its last hits off
        (Utilities|Time|SetTimerbyFunctionName :Object Enemy :FunctionName "ResetAttackCooldown" :Time (Math|Float|Max(Float) (Class|BPEnemyBase|GetAttackCooldown Enemy) (+ (Variables|Default|GetMoveLen) 0.2)) :bLooping false))))
  (Variables|Default|SetLastState st))
"""
open(D + "Watch.dsl", "w").write(s)

# ---------------- move effects: when each move CONNECTS, extra damage + a shove (dodge it by leaving its reach) --------------
# move: (hit times s, reach x the attacker's attack range, hits all round?, damage x its attack damage, push cm/s, up cm/s,
#        push mode 0 away / 1 sideways (tail) / 2 along its facing, fx 0 none / 1 dust + thud / 2 whoosh)
FX = {"Pounce": ([0.35], 1.6, False, 0.5, 500, 250, 0, 0),
      "TailSwipe": ([0.45], 1.4, True, 0.4, 750, 250, 1, 2),
      "Charge": ([0.45], 2.0, False, 0.6, 900, 300, 2, 2),
      "Stomp": ([0.65], 1.9, True, 0.7, 650, 450, 0, 1),
      "Gore": ([0.52], 1.4, False, 0.5, 300, 800, 2, 0),
      "Frenzy": ([0.30, 0.52, 0.74], 1.25, False, 0.3, 150, 0, 0, 0),
      "Slash": ([0.35, 0.52], 1.25, False, 0.35, 250, 100, 0, 0),
      "Sidestep": ([0.55], 1.5, True, 0.4, 350, 150, 0, 0)}
B = lambda b: "true" if b else "false"
s = """(fn MoveFx (Active)
  ; runs every tick: fires the current move's hits at their times; a flinch / death / the move ending cancels the rest
  (if (not (Utilities|String|EqualExactly(String) (Variables|Default|GetCurMove) ""))
    (if (not Active)
      (Variables|Default|SetCurMove "")
      (else
        (bind el (- (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveStart)))
"""
for mv, (times, reach, anyd, dmg, push, up, mode, fx) in FX.items():
    s += '        (if (Utilities|String|EqualExactly(String) (Variables|Default|GetCurMove) "%s")\n' % mv
    for k, t in enumerate(times):
        s += "          (if (and (== (Variables|Default|GetHitsDone) %d) (>= el %.2f))\n" % (k, t)
        s += "            (Variables|Default|SetHitsDone %d)\n" % (k + 1)
        s += "            (CallFunction|Hit self %.2f %s %.2f %.1f %.1f %d %d)" % (reach, B(anyd), dmg, push, up, mode, fx if k == 0 else 0)
        s += '\n            (Variables|Default|SetCurMove ""))' if k == len(times) - 1 else ")"
        s += ")\n" if k == len(times) - 1 else "\n"
s += "))))\n"
open(D + "MoveFx.dsl", "w").write(s)

s = """(fn Hit (Reach AnyDir DmgFrac Push Up Mode Fx)
  (bind loc (Transformation|GetActorLocation (Components|GetOwner self)))
  (if (== Fx 1)
    (Niagara|SpawnSystematLocation :SystemTemplate "/Game/Timeshift/Hazards/VFX/NS_RockDust.NS_RockDust" :Location loc :Scale (Math|Vector|MakeVector 2.5 2.5 2.5))
    (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_RexPrime_Step_02.S_RexPrime_Step_02" :Location loc :VolumeMultiplier 1.3 :PitchMultiplier 0.8))
  (if (== Fx 2)
    (Audio|PlaySoundatLocation :Sound "/Game/Timeshift/Audio/SFX/Creatures/S_Fly_Dive_Whoosh.S_Fly_Dive_Whoosh" :Location loc :VolumeMultiplier 0.7 :PitchMultiplier 1.3))
  (if (Variables|Default|GetIsHero)
    (CallFunction|HeroHit self Reach AnyDir DmgFrac Push Up Mode)
    (else
      (CallFunction|EnemyHit self Reach AnyDir DmgFrac Push Up Mode))))
"""
open(D + "Hit.dsl", "w").write(s)

s = """(fn SetPush (Attacker Target Mode)
  ; PushDir = which way a hit shoves: 0 straight away from the attacker, 1 out to the side the target is on, 2 along its facing
  (bind a (Transformation|GetActorLocation Attacker))
  (bind t (Transformation|GetActorLocation Target))
  (bind d (Math|Vector|MakeVector (- (.x t) (.x a)) (- (.y t) (.y a)) 0.0))
  (if (== Mode 1)
    (bind r (Transformation|GetActorRightVector Attacker))
    (bind sg (select (>= (Math|Vector|DotProduct r d) 0.0) 1.0 -1.0))
    (Variables|Default|SetPushDir (Math|Vector|MakeVector (* (.x r) sg) (* (.y r) sg) 0.0))
    (elif (== Mode 2)
      (Variables|Default|SetPushDir (Transformation|GetActorForwardVector Attacker))
      (else
        (Variables|Default|SetPushDir (Math|Vector|Normalize d))))))
"""
open(D + "SetPush.dsl", "w").write(s)

s = """(fn EnemyHit (Reach AnyDir DmgFrac Push Up Mode)
  ; an enemy's move connects with the player if he is still within reach (and in front, unless it hits all round)
  (bind en (Variables|Default|GetOwnerEnemy))
  (bind pl (Game|GetPlayerCharacter 0))
  (if (and (< (Transformation|GetHorizontalDistanceTo :self en :OtherActor pl) (* Reach (Class|BPEnemyBase|GetAttackRange en))) (or AnyDir (> (Transformation|GetHorizontalDotProductTo :self en :OtherActor pl) 0.3)))
    (bind hero (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object pl)
      (:then
        (Class|BPHealthComponent|ApplyDamage :self (Class|BPThirdPersonCharacter|GetHealthComponent hero) :DamageAmount (* DmgFrac (Class|BPEnemyBase|GetAttackDamage en)))
        ; the shove scales with the attacker (attack damage / 25, 0.2..1): a Compy nudges, a Triceratops throws. No launch while
        ; the player is already in the air, or a swarm of small ones juggles him (seen 2026-10-21 in a Compy swarm)
        (if (not (Movement|IsFalling (Class|Character|GetCharacterMovement hero)))
          (bind k (Math|Float|Clamp(Float) (/ (Class|BPEnemyBase|GetAttackDamage en) 25.0) 0.2 1.0))
          (CallFunction|SetPush self en hero Mode)
          (bind pd (Variables|Default|GetPushDir))
          (Character|LaunchCharacter :self hero :LaunchVelocity (Math|Vector|MakeVector (* (.x pd) (* Push k)) (* (.y pd) (* Push k)) (* Up (* k k))) :bXYOverride true :bZOverride (> (* Up (* k k)) 50.0))))
      (:CastFailed))))
"""
open(D + "EnemyHit.dsl", "w").write(s)

s = """(fn HeroHit (Reach AnyDir DmgFrac Push Up Mode)
  ; the morphed hero's move connects with every enemy within reach (in front, unless it hits all round)
  (bind me (Variables|Default|GetOwnerHero))
  (bind all (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Enemies/BP_EnemyBase.BP_EnemyBase_C"))
  (for a all
    (if (and (< (Transformation|GetHorizontalDistanceTo :self me :OtherActor a) (* Reach (Class|BPThirdPersonCharacter|GetMorphRange me))) (or AnyDir (> (Transformation|GetHorizontalDotProductTo :self me :OtherActor a) 0.3)))
      (bind eb (Utilities|Casting|CastToBP_EnemyBase :Object a)
        (:then
          (bind hc (Class|BPEnemyBase|GetHealthComponent eb))
          (if (not (Class|BPHealthComponent|GetIsDead hc))
            (Class|BPHealthComponent|ApplyDamage :self hc :DamageAmount (* DmgFrac (Class|BPThirdPersonCharacter|GetMorphDmg me)))
            (CallFunction|SetPush self me eb Mode)
            (bind pd (Variables|Default|GetPushDir))
            (Class|BPEnemyBase|ReceiveKnockback :self eb :Push (Math|Vector|MakeVector (* (.x pd) (* 1.5 Push)) (* (.y pd) (* 1.5 Push)) 0.0))))
        (:CastFailed)))))
"""
open(D + "HeroHit.dsl", "w").write(s)

s = """(fn Senses (Enemy)
  ; HEARING (user 2026-10-21: "no dinosaurs come near me, they need to investigate"): a hunter / big herbivore that hears
  ; the player beyond its sight range walks over to where it heard him (its roam target), re-aimed every 0.5 s while it can
  ; still hear him; once he is in sight range the normal chase takes over, and if it loses him its roaming drifts it home.
  ; Hearing range = sight range x 2.5 x noise: crouched 0.4, standing 0.5, walking 1, sprinting 1.3. Timid (fleeing),
  ; flying and dying animals do not investigate, and nobody listens in the first 8 s of play.
  (bind now (Utilities|Time|GetGameTimeinSeconds))
  (if (and (> now (Variables|Default|GetNextHearTime)) (> now 8.0))
    (Variables|Default|SetNextHearTime (+ now 0.5))
    (if (not (or (or (or (Class|BPEnemyBase|GetDying Enemy) (Class|BPEnemyBase|GetIsFlying Enemy)) (Class|BPEnemyBase|ShouldFlee Enemy)) (== (Class|BPEnemyBase|GetAnimState Enemy) 2)))
      (bind pl (Game|GetPlayerCharacter 0))
      (bind d (Transformation|GetHorizontalDistanceTo :self Enemy :OtherActor pl))
      (bind det (Class|BPEnemyBase|GetDetectionRange Enemy))
      (bind spd (Math|Vector|VectorLengthXY (Transformation|GetVelocity pl)))
      (bind noise (select (Class|Character|GetIsCrouched pl) 0.4 (select (> spd 450.0) 1.3 (select (> spd 30.0) 1.0 0.5))))
      (if (and (> d det) (< d (* det (* 2.5 noise))))
        (bind pp (Transformation|GetActorLocation pl))
        (bind me (Transformation|GetActorLocation Enemy))
        (Class|BPEnemyBase|SetRoamTarget :self Enemy :RoamTarget (Math|Vector|MakeVector (+ (.x pp) (Math|Random|RandomFloatInRange -250.0 250.0)) (+ (.y pp) (Math|Random|RandomFloatInRange -250.0 250.0)) (.z me)))
        (Class|BPEnemyBase|SetRoamHolding :self Enemy :RoamHolding false)
        (Class|BPEnemyBase|SetNextRoamTime :self Enemy :NextRoamTime (+ now 10.0))
        (Class|BPEnemyBase|SetStuckCheckPos :self Enemy :StuckCheckPos me)
        (Class|BPEnemyBase|SetStuckCheckTime :self Enemy :StuckCheckTime (+ now 3.0))
        (Variables|Default|SetInvestigating true)
        (else
          (Variables|Default|SetInvestigating false))))))
"""
open(D + "Senses.dsl", "w").write(s)

s = """(fn ApplyDifficulty (Enemy)
  ; DIFFICULTY (user 2026-10-21): the hero's AttackVariety holds the level (0 easy, 1 medium, 2 hard - saved in the settings
  ; save). Each enemy captures its species stats once, then re-applies multipliers whenever the level changes:
  ;   damage 0.6 / 1 / 1.4, health 0.75 / 1 / 1.3, sight + hearing 0.8 / 1 / 1.25, attack cooldown 1.3 / 1 / 0.8.
  ; Health keeps its current fraction. A hidden player (Hide power-up) has detection zeroed with the real value in
  ; DetectionRangeBackup, so the scaled range goes there while it is in use.
  (bind now (Utilities|Time|GetGameTimeinSeconds))
  (if (> now (Variables|Default|GetNextDiffCheck))
    (Variables|Default|SetNextDiffCheck (+ now 1.0))
    (bind hc (Class|BPEnemyBase|GetHealthComponent Enemy))
    (if (not (Variables|Default|GetBaseCaptured))
      (Variables|Default|SetBaseCaptured true)
      ; the captured species stats ARE the medium level (don't trust the component's default here: templates inside
      ; BP_EnemyBase / the hero kept 0 when the variable was added)
      (Variables|Default|SetAppliedDifficulty 1)
      (Variables|Default|SetBaseDamage (Class|BPEnemyBase|GetAttackDamage Enemy))
      (Variables|Default|SetBaseDetection (select (> (Class|BPEnemyBase|GetDetectionRange Enemy) 0.0) (Class|BPEnemyBase|GetDetectionRange Enemy) (Class|BPEnemyBase|GetDetectionRangeBackup Enemy)))
      (Variables|Default|SetBaseCooldown (Class|BPEnemyBase|GetAttackCooldown Enemy))
      (Variables|Default|SetBaseMaxHealth (Class|BPHealthComponent|GetMaxHealth hc)))
    (bind hero (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Game|GetPlayerCharacter 0))
      (:then
        (Variables|Default|SetDifficulty (CallFunction|GetLevel (Class|BPThirdPersonCharacter|GetAttackVariety hero)))
        (if (and (!= (Variables|Default|GetDifficulty) (Variables|Default|GetAppliedDifficulty)) (not (Class|BPHealthComponent|GetIsDead hc)))
          (Variables|Default|SetAppliedDifficulty (Variables|Default|GetDifficulty))
          (bind d (Variables|Default|GetDifficulty))
          (Class|BPEnemyBase|SetAttackDamage :self Enemy :AttackDamage (* (Variables|Default|GetBaseDamage) (select (== d 0) 0.6 (select (== d 2) 1.4 1.0))))
          (Class|BPEnemyBase|SetAttackCooldown :self Enemy :AttackCooldown (* (Variables|Default|GetBaseCooldown) (select (== d 0) 1.3 (select (== d 2) 0.8 1.0))))
          (if (> (Class|BPEnemyBase|GetDetectionRange Enemy) 0.0)
            (Class|BPEnemyBase|SetDetectionRange :self Enemy :DetectionRange (* (Variables|Default|GetBaseDetection) (select (== d 0) 0.8 (select (== d 2) 1.25 1.0))))
            (else
              (Class|BPEnemyBase|SetDetectionRangeBackup :self Enemy :DetectionRangeBackup (* (Variables|Default|GetBaseDetection) (select (== d 0) 0.8 (select (== d 2) 1.25 1.0))))))
          ; current health first (it reads the OLD max), then the new max
          (Class|BPHealthComponent|SetCurrentHealth :self hc :CurrentHealth (* (Class|BPHealthComponent|GetCurrentHealth hc) (/ (* (Variables|Default|GetBaseMaxHealth) (select (== d 0) 0.75 (select (== d 2) 1.3 1.0))) (Class|BPHealthComponent|GetMaxHealth hc))))
          (Class|BPHealthComponent|SetMaxHealth :self hc :MaxHealth (* (Variables|Default|GetBaseMaxHealth) (select (== d 0) 0.75 (select (== d 2) 1.3 1.0))))))
      (:CastFailed))))
"""
open(D + "ApplyDifficulty.dsl", "w").write(s)

s = """(fn Guard (Enemy)
  ; MOVEMENT GUARD (user 2026-10-21: "dinosaurs walking through trees"): enemies move by SetActorLocation without a
  ; sweep, so roaming / chasing / fleeing all slid through trunks and rocks. Each tick, sweep a sphere at body height
  ; along the step just taken; if it hit a tree / rock / wall (not the landscape, not another dinosaur or the player),
  ; put the enemy back on its last good spot and slide it along the obstacle so it works its way round.
  (bind cur (Transformation|GetActorLocation Enemy))
  (if (not (Variables|Default|GetGuardInit))
    (Variables|Default|SetGuardInit true)
    (Variables|Default|SetIgnoreList (Actor|GetAllActorsOfClass :ActorClass "/Game/Timeshift/Enemies/BP_EnemyBase.BP_EnemyBase_C"))
    (Utilities|Array|Add :TargetArray (Variables|Default|GetIgnoreList) :NewItem (Game|GetPlayerCharacter 0))
    (Variables|Default|SetLastGood cur)
    ; FEET FIX (user 2026-10-21: "dino is in the ground"): some Blender skeletons (Psittacosaurus, Caudipteryx) keep their
    ; armature bone below the mesh origin and the engine holds it there whatever the clips say, so the body sank 40-60 cm.
    ; Measure where that first bone really is and lift the body by the gap (0 for species that stand right).
    (bind body (Class|BPEnemyBase|GetBody Enemy))
    (bind sink (- (.z (Transformation|GetWorldLocation body)) (.z (Transformation|GetSocketLocation body (Components|SkinnedMesh|GetBoneName body 0)))))
    (if (> sink 3.0)
      (Transformation|AddWorldOffset body (Math|Vector|MakeVector 0.0 0.0 sink) false false))
    (else
      (bind last (Variables|Default|GetLastGood))
      (bind dx (- (.x cur) (.x last)))
      (bind dy (- (.y cur) (.y last)))
      (bind dl (Math|Vector|VectorLengthXY (Math|Vector|MakeVector dx dy 0.0)))
      ; only real steps: not standing still, not a teleport / big knockback, not flyers
      (if (and (and (> dl 1.0) (< dl 400.0)) (not (Class|BPEnemyBase|GetIsFlying Enemy)))
        (bind r (Math|Float|Clamp(Float) (* 0.5 (Class|BPEnemyBase|GetBodyRadius Enemy)) 15.0 60.0))
        (bind h (+ r 35.0))
        (bind (hit ok) (Collision|SphereTraceByChannel :Start (Math|Vector|MakeVector (.x last) (.y last) (+ (.z cur) h)) :End (Math|Vector|MakeVector (.x cur) (.y cur) (+ (.z cur) h)) :Radius r :ActorsToIgnore (Variables|Default|GetIgnoreList)))
        (bind (hb hio ht hd hl hip hn hin hpm hha hhc) (Collision|BreakHitResult hit))
        (if (and (and ok (not hio)) (not (Utilities|String|Contains (Utilities|GetDisplayName hhc) "Landscape")))
          ; slide = step minus its part going into the obstacle (impact normal, flattened), plus 1 cm clearance
          (bind nx (.x hin))
          (bind ny (.y hin))
          (bind nn (Math|Float|Max(Float) (+ (* nx nx) (* ny ny)) 0.0001))
          (bind into (Math|Float|Min(Float) (/ (+ (* dx nx) (* dy ny)) nn) 0.0))
          (bind inv (/ 1.0 (Math|Float|Sqrt nn)))
          (Transformation|SetActorLocation Enemy (Math|Vector|MakeVector (+ (+ (.x last) (- dx (* nx into))) (* nx inv)) (+ (+ (.y last) (- dy (* ny into))) (* ny inv)) (.z cur)) false false)))
      (Variables|Default|SetLastGood (Transformation|GetActorLocation Enemy)))))
"""
open(D + "Guard.dsl", "w").write(s)

s = """(fn GetLevel ()
  ; another instance's variable cannot be read from inside this blueprint's own graphs - a function call can target it
  (return (Variables|Default|GetDifficulty)))
"""
open(D + "GetLevel.dsl", "w").write(s)

s = """(fn LoadDifficulty ()
  ; the hero's copy: read the saved level once (the settings save; missing = medium)
  (if (not (Variables|Default|GetDiffLoaded))
    (Variables|Default|SetDiffLoaded true)
    (Variables|Default|SetDifficulty 1)
    (if (SaveGame|DoesSaveGameExist "ChronoshiftSettings" 0)
      (bind sv (Utilities|Casting|CastToBP_SettingsSave :Object (SaveGame|LoadGamefromSlot "ChronoshiftSettings" 0))
        (:then
          (Variables|Default|SetDifficulty (Class|BPSettingsSave|GetDifficulty sv)))
        (:CastFailed)))))
"""
open(D + "LoadDifficulty.dsl", "w").write(s)

s = """(fn HeroFx ()
  (CallFunction|LoadDifficulty self)
  (bind h (Utilities|Casting|CastToBP_ThirdPersonCharacter :Object (Components|GetOwner self))
    (:then
      (Variables|Default|SetIsHero true)
      (Variables|Default|SetOwnerHero h)
      (CallFunction|MoveFx self (and (Class|BPThirdPersonCharacter|GetMorphed h) (== (Class|BPThirdPersonCharacter|GetMorphAnimState h) 2))))
    (:CastFailed)))
"""
open(D + "HeroFx.dsl", "w").write(s)

# ---------------- flyers: wing beats (user 2026-10-22: "flying dinosaur is just floating, no wing flap") -----------------
# Glide / Soar / Tuck clips hold the wings still (2-3 deg of bone motion) and the flight logic shows them half the time and
# whenever a flyer circles - so it hung in the air. While a flyer sits in a still-wing state this alternates its Flap clip
# (2.5-4.5 s) with that state's own glide (1.5-3 s). Dimorphodon / Pterosaur only have clips for states 0-5: the flight
# logic's states 6-15 fell through to their Death clip (a dead pose in mid air) - those get mapped to flap / glide / idle.
FLY = {"Pteranodon": ("/Game/Timeshift/Enemies/Pteranodon/A_Fly_Flap_Pteranodon.A_Fly_Flap_Pteranodon",
                      "/Game/Timeshift/Enemies/Pteranodon/A_Fly_Glide_Pteranodon.A_Fly_Glide_Pteranodon",
                      "/Game/Timeshift/Enemies/Pteranodon/A_Fly_Soar_Pteranodon.A_Fly_Soar_Pteranodon", None),
       "Tupandactylus": ("/Game/Timeshift/Enemies/Tupandactylus/A_Fly_Flap_Tupandactylus.A_Fly_Flap_Tupandactylus",
                         "/Game/Timeshift/Enemies/Tupandactylus/A_Fly_Glide_Tupandactylus.A_Fly_Glide_Tupandactylus",
                         "/Game/Timeshift/Enemies/Tupandactylus/A_Fly_Soar_Tupandactylus.A_Fly_Soar_Tupandactylus", None),
       "Dimorphodon": ("/Game/Timeshift/Enemies/Dimorphodon/A_Flyer_Flap_Dimorphodon_Anim.A_Flyer_Flap_Dimorphodon_Anim",
                       "/Game/Timeshift/Enemies/Dimorphodon/A_Flyer_Glide_Dimorphodon_Anim.A_Flyer_Glide_Dimorphodon_Anim", None,
                       "/Game/Timeshift/Enemies/Dimorphodon/SK_Dimorphodon_Anim_SK_Dimorphodon_Idle.SK_Dimorphodon_Anim_SK_Dimorphodon_Idle"),
       "Pterosaur": ("/Game/Timeshift/Enemies/Pterosaur/A_Flyer_Flap_Pterosaur_Anim.A_Flyer_Flap_Pterosaur_Anim",
                     "/Game/Timeshift/Enemies/Pterosaur/A_Flyer_Glide_Pterosaur_Anim.A_Flyer_Glide_Pterosaur_Anim", None,
                     "/Game/Timeshift/Enemies/Pterosaur/SK_Pterosaur_Anim_SK_Pterosaur_Idle.SK_Pterosaur_Anim_SK_Pterosaur_Idle")}
PA = '(Components|Animation|PlayAnimation :self body :NewAnimToPlay "%s" :bLooping true)'
s = """(fn FlyerAnim (Enemy)
  (if (and (Class|BPEnemyBase|GetIsFlying Enemy) (not (Class|BPEnemyBase|GetDying Enemy)))
    (bind st (Class|BPEnemyBase|GetAnimState Enemy))
    (bind sp (Class|BPEnemyBase|GetSpecies Enemy))
    (bind body (Class|BPEnemyBase|GetBody Enemy))
    (bind now (Utilities|Time|GetGameTimeinSeconds))
    (if (!= st (Variables|Default|GetFlyLastState))
      ; a new still-wing state shows its glide briefly, then the wings start beating
      (Variables|Default|SetFlyLastState st)
      (Variables|Default|SetFlyFlapping false)
      (Variables|Default|SetFlyMapped false)
      (Variables|Default|SetFlyNextSwitch (+ now (Math|Random|RandomFloatInRange 0.4 1.2))))
"""
for sp, (flap, glide, soar, idle) in FLY.items():
    big = soar is not None
    still = "(or (== st 0) (== st 6))" if big else "(or (or (or (or (== st 0) (== st 6)) (== st 8)) (== st 9)) (== st 10))"
    s += '    (if (Utilities|String|EqualExactly(String) sp "%s")\n' % sp
    if not big:
        # states 6-15 have no clip of their own on this species (UpdateBodyAnim played Death): replace it the same frame
        s += "      (if (and (>= st 6) (not (Variables|Default|GetFlyMapped)))\n"
        s += "        (Variables|Default|SetFlyMapped true)\n"
        s += "        (if (or (or (== st 7) (== st 11)) (== st 12))\n          %s)\n" % (PA % flap)
        s += "        (if (>= st 13)\n          %s)\n" % (PA % idle)
        s += "        (if (or (or (or (== st 6) (== st 8)) (== st 9)) (== st 10))\n          %s))\n" % (PA % glide)
        s += "      (if (< st 6)\n        (Variables|Default|SetFlyMapped false))\n"
    s += "      (if (and %s (> now (Variables|Default|GetFlyNextSwitch)))\n" % still
    s += "        (Variables|Default|SetFlyFlapping (not (Variables|Default|GetFlyFlapping)))\n"
    s += "        (if (Variables|Default|GetFlyFlapping)\n"
    s += "          %s\n" % (PA % flap)
    s += "          (Variables|Default|SetFlyNextSwitch (+ now (Math|Random|RandomFloatInRange 2.5 4.5))))\n"
    s += "        (if (not (Variables|Default|GetFlyFlapping))\n"
    if big:
        s += "          (if (== st 6)\n            %s)\n          (if (!= st 6)\n            %s)\n" % (PA % soar, PA % glide)
    else:
        s += "          %s\n" % (PA % glide)
    s += "          (Variables|Default|SetFlyNextSwitch (+ now (Math|Random|RandomFloatInRange 1.5 3.0))))))\n"
s += "  ))\n"
open(D + "FlyerAnim.dsl", "w").write(s)
for f in ("MoveCount.dsl", "PlayMove.dsl", "EventGraph.dsl", "Watch.dsl", "MoveFx.dsl", "Hit.dsl", "SetPush.dsl", "EnemyHit.dsl",
          "HeroHit.dsl", "HeroFx.dsl", "Senses.dsl", "ApplyDifficulty.dsl", "LoadDifficulty.dsl", "GetLevel.dsl", "Guard.dsl",
          "FlyerAnim.dsl"):
    t = open(D + f).read()
    print(f, "parens", t.count("(") - t.count(")"), "lines", t.count("\n"))
