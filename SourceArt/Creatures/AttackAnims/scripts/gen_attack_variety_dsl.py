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
        s += '    (if (== Move %d)\n      (Components|Animation|PlayAnimation :self Body :NewAnimToPlay "%s" :bLooping false)\n      (return %.2f))\n' % (i, path(sp, mv), LEN[mv])
    s += '    (if (== Move 9)\n      (Components|Animation|PlayAnimation :self Body :NewAnimToPlay "%s" :bLooping false)\n      (return %.2f)))\n' % (path(sp, "Roar"), LEN["Roar"])
s += "  (return 0.0))\n"
open(D + "PlayMove.dsl", "w").write(s)

# Tick
s = """(event AddEvent|EventTick (DeltaSeconds)
  (bind eb (Utilities|Casting|CastToBP_EnemyBase :Object (Components|GetOwner self))
    (:then
      (CallFunction|Watch self eb))
    (:CastFailed)))
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
        (Class|BPEnemyBase|SetAttackEndTime :self Enemy :AttackEndTime (+ (Utilities|Time|GetGameTimeinSeconds) (Variables|Default|GetMoveLen))))))
  (Variables|Default|SetLastState st))
"""
open(D + "Watch.dsl", "w").write(s)
for f in ("MoveCount.dsl", "PlayMove.dsl", "EventGraph.dsl", "Watch.dsl"):
    t = open(D + f).read()
    print(f, "parens", t.count("(") - t.count(")"), "lines", t.count("\n"))
