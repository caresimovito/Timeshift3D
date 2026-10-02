# Chronoshift — Temporal Log (encyclopedia) design

Aesthetic: **Field Technology vs. Primal History.** An advanced temporal tracker rig
struggling to log raw chronological data. Brass-and-teal instrument chrome around the
edge, cyan holographic analyzer for the subject, warm parchment for the written record.
The rig is *fallible* — it glitches, mis-reads, and hedges. That is the voice.

## Screen layout

```
┌──────────────────────────────────────────────────────────────────────┐
│                      CHRONOSHIFT · TEMPORAL LOG            [HP][ARM] │
│   (LB) [ ENEMIES ] [ BUILDINGS ] [ HISTORIC FACTS ] (RB)             │
├────────────────────────┬─┬───────────────────────────────────────────┤
│  TEMPORAL INDEX        │T│   ╔═══════════════════════════════════╗   │
│  ENEMIES (CURRENT: X)  │I│   ║   holographic analyzer portrait   ║   │
│  ┌──────────────────┐  │M│   ║                                   ║   │
│  │ [tn] [Entry A]   │  │E│   ╟───────────────────────────────────╢   │
│  │ [tn] [Entry B] ◄ │  │L│   ║ ORIGIN · STABILITY · THREAT       ║   │
│  │ [tn] [Entry C]   │  │I│   ║ PRIMARY ATTACK · WEAKNESS         ║   │
│  │ [tn] [Entry D]   │  │N│   ╚═══════════════════════════════════╝   │
│  │        ...       │  │E│   ┌───────────────────────────────────┐   │
│  └──────────────────┘  │ │   │  ENTRY TITLE                      │   │
│  [HISTORIC FACTS]      │▲│   │  italic subtitle                  │   │
│                        │▼│   │  technical scan ...               │   │
│                        │ │   │  Protagonist Log Notes: '...'     │   │
│                        │ │   │  Location: ...                    │   │
│                        │ │   └───────────────────────────────────┘   │
├────────────────────────┴─┴───────────────────────────────────────────┤
│   (LB) Categories   │   Timeline   │   (A) Inspect   │   (X) Close   │
└──────────────────────────────────────────────────────────────────────┘
```

The timeline rail between the panels is the era scrubber: **FORWARD** at the top,
**PAST** at the bottom, with a floating marker reading the current era. Scrubbing it
filters the Temporal Index to that era.

## Entry schema

Fields marked **new** do not exist on `BP_BestiaryEntry` yet.

| Field | Type | Feeds | Notes |
|---|---|---|---|
| `Id` | Name | — | stable key, also used by discovery |
| `EntryType` | Enum **new** | category tabs | `Enemies` / `Buildings` / `HistoricFacts` |
| `EraName` | Text **new** | era marker | e.g. `EOCENE PERIOD` |
| `EraYearText` | Text **new** | era marker | e.g. `-40,000,000 BCE` |
| `EraSortIndex` | Int **new** | timeline rail | ascending = further in the past |
| `DisplayName` | Text | index row + entry title | |
| `Subtitle` | Text **new** | italic line under the title | |
| `ThumbnailPath` | SoftObject | index row portrait | |
| `MeshPath` | SoftObject | analyzer portrait | |
| `TemporalOrigin` | Text **new** | metadata bar | |
| `Stability` | Text **new** | metadata bar | the rig's confidence in its own read |
| `Threat` | Text **new** | metadata bar | |
| `PrimaryAttack` | Text **new** | metadata bar | |
| `Weakness` | Text **new** | metadata bar | |
| `TechnicalScan` | Text | body paragraph 1 | existing `Description` renamed in use |
| `LogNotes` | Text **new** | body paragraph 2, quoted | first person, tactical |
| `LocationText` | Text **new** | body paragraph 3 | prose, not the one-word `Habitat` |
| `Discovered` | Bool | lock state | |
| `Category` | Text | — | existing diet/class field, kept |
| `Diet`, `LengthText`, `Habitat`, `facts`, `nextId`, `prevId` | | | existing, kept |

### Voice rules

- **Technical Scan** is the rig talking: analytical, third person, present tense. It may
  admit uncertainty, but it never gives tactical advice.
- **Protagonist Log Notes** is the player character talking: first person, conversational,
  practical. Always in single quotes. It gives the thing you actually do about it.
- **Stability** is the rig grading its own signal, never the creature's temperament.

---

## Entry: Palaeophis

| | |
|---|---|
| **Id** | `Palaeophis` |
| **Entry Type** | ENEMIES |
| **Era** | EOCENE PERIOD (-40,000,000 BCE) |
| **Display Name** | PALAEOPHIS |
| **Subtitle** | *The Long Current* |

**Analyzer portrait** — a sea snake better than twelve metres long, coiled in slow
suspension as though the hologram were holding water rather than air. The body is
laterally flattened into a swimmer's blade, keeled along the spine, banded in drowned
olive and silt-grey that breaks up the moment it stops moving. The scan resolves the
skull cleanly — blunt, wide-jointed, eyes set high for watching the surface from
below — but the last third of the tail stays unresolved, fraying into scan static, as
if the rig cannot decide where the animal ends.

| | |
|---|---|
| **Temporal Origin** | Eocene Epoch |
| **Stability** | Unstable / Submerged Read |
| **Threat** | Extreme |
| **Primary Attack** | Constricting Coil / Ambush Strike |
| **Weakness** | Open Ground, Fire, Sustained Piercing |

**Technical Scan**

A palaeophiid serpent adapted wholly to warm shallow sea. The vertebral column is
compressed into a vertical paddle, trading all terrestrial movement for thrust, and
the specimen exceeds twelve metres without reaching the limit of its growth. It does
not envenom. It anchors with recurved teeth and then drowns what it has caught, using
its own body as the weight. Sensory emphasis is pressure and vibration rather than
sight; the rig logs it reacting to disturbance four seconds before any visual contact
is possible. Temporal readings degrade sharply below the waterline, and the entity
spends most of its cycle there.

**Protagonist Log Notes**

'The scanner is useless the second it goes under — I get a shape and a lot of noise.
Don't trust the water being quiet, that's the tell, everything else goes quiet first.
It has to commit to a strike and it's enormous, so it cannot turn: break sideways, not
backwards. If it gets a coil on you, stop struggling, that is what it is waiting for —
go for the same spot twice with something sharp instead. And it will not follow you
more than a few metres onto dry land. The bank is the win condition. Fire on the water
moves it off, though it does not move it far.'

**Location**

Encountered in the warm shallow channels and flooded mangrove margins of the Eocene
coastal shelf, and in the drowned river mouths that feed it.

---

## Frame art

The ornate chrome is generated, not painted: `Tools/gen_ui_frames.py` writes ten
9-slice PNGs to `SourceArt/UI/`, and `Tools/import_ui_frames.py` imports them to
`/Game/Timeshift/UI/Frames/` and binds them to the panels. Both are idempotent,
so iterating on the look means editing the colour ramp or the band profile in the
generator and re-running the pair.

Each texture is authored at the pixel size it renders at: the brass band is a
fixed number of pixels and the slice margin sits just outside it, so Slate
stretches only the flat centre and the frame stays crisp at any panel size.
Corner ornaments fit entirely inside the margin square or 9-slicing would cut
them in half.

| Texture | px | Margin | Used by |
|---|---|---|---|
| `T_UI_FrameOuter` | 72 | 0.389 | `Backdrop` — heavy band, corner brackets |
| `T_UI_PanelDark` | 40 | 0.400 | `LeftPanel` — rosette corners |
| `T_UI_PanelAnalyzer` | 40 | 0.400 | `AnalyzerBox` — cyan inner glow |
| `T_UI_PanelParchment` | 40 | 0.400 | `RecordBox` — parchment + keyline |
| `T_UI_MetaBar` | 24 | 0.417 | `MetaBar`, `FooterBar`, `IndexContextBox` |
| `T_UI_RowIdle` | 24 | 0.417 | `RowButton` normal |
| `T_UI_RowSelected` | 24 | 0.417 | `RowButton` hovered, `EraMarkerBox` |
| `T_UI_TabActive` | 40 | 0.400 | `TabEnemies` |
| `T_UI_TabIdle` | 40 | 0.400 | `TabBuildings`, `TabFacts` |
| `T_UI_Rail` | 32 | 0.375 | `TimelineRail` — recessed channel |

Buttons take their art through `WidgetStyle.normal/hovered/pressed` rather than
`Background`, and their `BackgroundColor` must stay white or it tints the brush.

### Gotchas

- A `SlateBrush` with `drawAs: RoundedBox` defaults to
  `roundingType: HalfHeightRadius`, which rounds each panel by half its own
  height — panels become ellipses. Use `FixedRadius`, or `Box` with a texture.
- `Appearance|SetBrushFromTexture` resolves to the Border overload, so any widget
  that receives a texture at runtime must be a `Border`, not an `Image`.
- `LoadAssetBlocking` on an empty soft path aborts the node chain, so an entry
  with a blank `ThumbnailPath` silently kills the rest of its `Construct`.
