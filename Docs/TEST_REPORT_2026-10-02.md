# Chronoshift — automated test pass, 2 Oct 2026

> **Corrected after follow-up.** Two findings below were wrong on first pass and
> are struck through in place. See `## Corrections` at the end.

## Scope and limits

**This is not a human play test.** Synthetic input is rejected in my environment,
so I could not move the character, press J, or click anything. What follows is a
runtime error sweep plus exhaustive data and blueprint validation. Everything
input-driven is listed as untested at the bottom — treat that list as the work
still owed, not as passing.

---

## Verified working (actually executed)

| Check | Result |
|---|---|
| PIE cold start | clean, twice — **0 errors, 0 warnings** |
| Blueprint compiles (7 BPs + 3 widgets) | all pass |
| Discovery → save → disk | `Compy` written to `ChronoshiftSave.sav` as `ArrayProperty`/`StrProperty` |
| Discovery reload across sessions | second session recorded **0** species — it loaded `Compy` and correctly skipped it |
| Bestiary entry integrity (18) | no empty fields, `Id` matches filename, thumbnails resolve, `EntryTypeIndex` all 0, `Discovered` all false |
| `EntryPaths` list | 18 paths, all resolve, no duplicates, exactly matches assets on disk |
| `Saved/` gitignored | yes — save files cannot be committed |

The save-game migration from the previous task is confirmed working end to end.

---

## Bugs found

### 1. Eleven flyers can never be logged — HIGH

Five `Pteranodon_*` and six `Tupandactylus_*` actors are `BP_EnemyBase`
instances with **no `Species` value set**. `RecordDiscovery` builds
`/Game/Timeshift/UI/Bestiary/DA_Bestiary_` + `""`, which resolves to nothing, so
walking up to any flyer logs nothing and silently fails a blocking asset load
once per second while in range.

Compounding it: there is no `DA_Bestiary_Pteranodon` or
`DA_Bestiary_Tupandactylus`. The bestiary has `Pterosaur` and `Dimorphodon`
instead, which are the older flyer assets. The entries and the placed actors are
simply different species.

Fix: decide the canonical names, set `Species` on all 11 actors, and rename or
add the matching entries.

### 2. The 18/18 counter is unreachable — HIGH

Species with a bestiary entry but nothing discoverable in the level:

| Species | Situation |
|---|---|
| `RexPrime` | the boss is placed, but `BP_Boss_RexPrime` derives from `StaticMeshActor`, **not** `BP_EnemyBase`, so `GetAllActorsOfClass` in `RecordDiscovery` never sees it |
| `Dimorphodon` | zero actors anywhere in the level |
| `Brontosaurus` | appears only as scenery meshes, not as a `BP_EnemyBase` |
| `Pterosaur` | superseded by the Pteranodon/Tupandactylus flyers (see bug 1) |
| `Palaeophis` | intentional — Eocene, a later era |

So the log advertises 18 but at most ~13 are currently obtainable. Either the
counter should count only obtainable entries for the current era, or these need
placing. `RexPrime` is the cheapest real fix: reparent the boss to
`BP_EnemyBase`, or widen the discovery scan.

### 3. Species/label mismatches — MEDIUM, needs confirmation

A binary scan of the external actor files found actors whose label and `Species`
disagree:

- `Enemy_Raptor_*` carrying `Triceratops`, `Spinosaurus`, `Compy`
- `Enemy_Dilophosaurus_*` carrying `Compy`

These would log the wrong species on approach. **Lower confidence than the
others** — the scan reads strings out of binary packages and can pick up
references rather than the `Species` property itself. Confirm by selecting the
actors in the editor before changing anything.

---

## Not tested — needs a human

Nothing below was exercised, because all of it requires input:

- Opening the Temporal Log with **J**, closing with J/Backspace/Esc
- Clicking index rows to switch the right-hand pane
- The category tabs (Enemies / Buildings / Historic Facts)
- Movement, jump, crouch, combat, weapon switching, pickups
- The invisible-wall issue in the level (still open from earlier)
- Whether the log's margins and ornaments hold up at other resolutions

Discovery was only observed for species adjacent to the player start, since the
character never moved.


---

## Corrections

I re-ran the census properly, by reading `Species` off every loaded
`BP_EnemyBase` actor in the editor rather than scanning strings out of binary
packages. Two of the three bugs above were misdiagnosed.

### Bug 1 — cause was wrong, symptom was real

The flyers are **not** missing `Species`. All 97 enemies have one, with zero
blanks. The five Pteranodon and six Tupandactylus actors carry `Pteranodon` and
`Tupandactylus` correctly — there was simply **no bestiary entry by those
names**, so `RecordDiscovery` still failed its asset load and they could never
be logged. My original scan only looked for species tokens matching an existing
entry, so "no species token" meant "no matching entry", and I reported it as
"no Species set".

**Fixed**: added `DA_Bestiary_Pteranodon` and `DA_Bestiary_Tupandactylus`, with
portraits captured from `SK_Pteranodon` and `SK_Tupandactylus`. No actor edits
were needed.

### Bug 3 — false positive, withdrawn

There are **no species/label mismatches**. The 15 placed species are all
sensible and all now have entries. The apparent `Enemy_Raptor_* → Triceratops`
style mismatches were strings picked up from asset references inside the binary
packages, not `Species` values. This is exactly the failure mode I flagged as
"lower confidence" — the lesson is that the binary scan is not evidence, and the
editor census is.

### Bug 2 — stands, with updated numbers

20 entries now exist and **15 are obtainable**. Five have no placed actors:

| Species | Situation |
|---|---|
| `RexPrime` | boss is placed but derives from `StaticMeshActor`, not `BP_EnemyBase`, so the discovery scan never sees it |
| `Dimorphodon` | no actors in the level |
| `Brontosaurus` | scenery meshes only |
| `Pterosaur` | superseded in the level by Pteranodon/Tupandactylus |
| `Palaeophis` | intentional — Eocene, a later era |

The counter reads "N OF 20" but tops out at 15.
