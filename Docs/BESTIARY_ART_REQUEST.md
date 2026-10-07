# Bestiary portrait art request

What to generate, and the exact filenames to save as. Drop everything into
`C:\agentpy\bestiary_art\` and I'll import and wire it up.

## Style prompt (prepend to every creature)

> Naturalistic palaeoart portrait of a {CREATURE}. Painted, scientifically
> plausible, muted earthy palette — olive, grey-brown, ochre, cream. Three-quarter
> view facing left, animal fills most of the frame. Lit from upper left. Background
> is a softly blurred {HABITAT} that falls off to near-black at the edges and
> corners. No text, no logos, no border, no UI framing, no human-made objects.
> Not a film or franchise creature design — generic palaeoart.

**Format:** PNG, **512 × 320** (16:10 landscape), no alpha needed.

Keep the style identical across all 20 — same lighting direction, same level of
finish, same saturation. Consistency matters more than any single image.

## The 20 creatures

| Save as | Creature | Habitat for background |
|---|---|---|
| `RexPrime.png` | massive tyrannosaur, heavy scarring, dark charcoal and rust hide | volcanic ash plain |
| `Raptor.png` | man-sized feathered dromaeosaur, sickle claw | dense jungle |
| `Dilophosaurus.png` | slender theropod, twin head crests | jungle clearing |
| `Spinosaurus.png` | sail-backed semi-aquatic theropod, crocodile snout | wide river |
| `Compy.png` | small feathered Compsognathus, chicken-sized | forest floor |
| `RiverAmbusher.png` | crocodile-snouted theropod, wet olive hide | reed-choked river |
| `Pterosaur.png` | large pterosaur, membrane wings, long beak | coastal cliffs |
| `Dimorphodon.png` | small pterosaur, deep puffin-like beak | jungle canopy |
| `Triceratops.png` | three-horned ceratopsian, heavy frill | open fern plain |
| `Ankylosaurus.png` | armoured quadruped, osteoderms, tail club | dry scrub |
| `Stegosaurus.png` | plated back, four tail spikes | conifer woodland |
| `Parasaurolophus.png` | hadrosaur with long backward tube crest | marshy meadow |
| `Brontosaurus.png` | very large long-necked sauropod | open floodplain |
| `Psittacosaurus.png` | small parrot-beaked ceratopsian, bipedal | undergrowth |
| `Kulindadromeus.png` | small feathered ornithischian, striped tail | fern meadow |
| `Caudipteryx.png` | feathered, peacock-like tail fan, flightless | riverbank |
| `Archaeoceratops.png` | small ceratopsian, short frill, bipedal | dry woodland |
| `Pteranodon.png` | large crested pterosaur, toothless beak | sea cliffs |
| `Tupandactylus.png` | pterosaur with enormous sail-like head crest | lagoon |
| `Palaeophis.png` | giant prehistoric sea snake, banded | warm shallow sea |

## Also needed

| Save as | What |
|---|---|
| `_LOCKED.png` | 512 × 320. Dark red-tinted static / scanline interference, a creature silhouette barely readable through the noise. Reads as "no signal". One image, reused by every undiscovered entry. |
| `icon_lock.png` | 128 × 128, transparent. Simple padlock, white, flat. |
| `icon_apex.png` | 128 × 128, transparent. Theropod skull or silhouette, white, flat. |
| `icon_leaf.png` | 128 × 128, transparent. Simple leaf, white, flat. |
| `icon_fish.png` | 128 × 128, transparent. Simple fish, white, flat. |

## Notes

- **Palaeophis currently points at the River Ambusher's portrait** — a real bug in
  `DA_Bestiary_Palaeophis.thumbnailPath`. Its own art fixes it.
- Match the in-game retextures where you can: the creatures are deliberately muted
  and earthy, no saturated markings. A vivid portrait next to a drab model looks worse
  than a plain one.
- The existing `T_Bestiary_*` textures stay in place until the replacements import
  cleanly, so there's no broken state in between.
