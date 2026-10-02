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
