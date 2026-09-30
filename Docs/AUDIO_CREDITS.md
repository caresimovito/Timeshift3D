# Chronoshift - Audio Credits and Licensing

All audio currently in the project was downloaded from **Pixabay** and is covered by the
**Pixabay Content License**.

## Licence summary

- Free for commercial use.
- **No attribution required** (credit is optional but appreciated by the creators).
- No royalties, no revenue share.
- **Restriction that applies to us:** you may not sell or redistribute the audio on a
  *standalone* basis, e.g. as loose audio files or as a stock/sound pack. Embedding the
  sounds inside the game is exactly the permitted use, so shipping Chronoshift is fine.

Source: https://pixabay.com/service/license-summary/

## Assets

| Project asset | Original file | Uploader |
|---|---|---|
| S_Creature_Growl_Triple_01 | 53439420-large-animal-triple-growl-2-467847 | 53439420 |
| S_Creature_Roar_01 | dffdv-dinosaur-roar-with-screams-and-growls-193210 | dffdv |
| S_Creature_Growl_01 | dragon-studio-dinosaur-growl-487679 | DRAGON-STUDIO |
| S_Creature_Roar_02 | dragon-studio-dinosaur-roar-390283 | DRAGON-STUDIO |
| S_Creature_RoarPack_01..15 | febixaj5-edited-dinosaur-roars-15-566149 (split into 15) | febixaj5 |
| S_Creature_Vocal_01 | freesound_community-dinosaur-2-86565 | freesound_community |
| S_Creature_Vocal_02 | freesound_community-dinosaur-99810 | freesound_community |
| S_Pterosaur_Wings_Loop | freesound_community-giant-wings-flappingmp3-14881 | freesound_community |
| S_Pterosaur_Chirp_01 | freesound_community-pterodactyl-85046 | freesound_community |
| S_Creature_Pain_01 | gsmsea-dinosaur-calling-amp-roaring-in-pain-428070 | gsmsea |
| S_Creature_Growl_02 | gsmsea-dinosaur-growls-431298 | gsmsea |
| S_Creature_Footsteps_Gravel_Loop | audiopapkin-monster-footsteps-on-gravel-295850 | audiopapkin |
| S_Amb_Jungle_Creatures_Loop | juliush-jurassic-creatures-animal-nature-sounds-9682 | juliush |

`freesound_community` is Pixabay's account that mirrors CC0 sounds from Freesound.

## Processing applied

Converted from MP3 (which Unreal cannot import) to 48 kHz / 16-bit PCM WAV.
Creature sounds downmixed to **mono** so they spatialise correctly; the ambience bed kept
**stereo** since it plays unspatialised. All peak-normalised to -1 dBFS.

## Rule for anything added later

Record the source and licence in this file **at the time you download it**. Reconstructing
provenance later is painful, and some sources (notably Freesound) contain a mix of CC0,
CC-BY and CC-BY-NC in the same search results - CC-BY needs credit and CC-BY-NC cannot be
used in a commercial release at all.
