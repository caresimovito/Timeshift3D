# Chronoshift trailer

44.5 s, 1920x1080, one shot per area of Era 1.

## Pipeline

1. `make_camera_path.py` writes `Saved/trailer_path.json` - a shot list eased into per-frame
   camera poses, with heights taken from the live heightmap so the camera holds a constant
   distance above the ground.
2. `Saved/make_sequence_job.py` (run in the editor) builds `/Game/Timeshift/Cinematics/LS_Trailer`
   from that path. The camera is a **spawnable**, not a possessable - a possessable binds to an
   actor that already exists in the level, which it does not in a standalone session, so the
   camera cut never resolves and the render sits at the player start.
3. Render from a standalone game process, which keeps the world live (animations, particles,
   water) and uses the game's own post-process, so exposure is correct:

   ```
   UnrealEditor-Cmd.exe <uproject> /Game/Timeshift/Maps/Lvl_Era1_DinosaurEra -game
     -MovieSceneCaptureType=/Script/MovieSceneCapture.AutomatedLevelSequenceCapture
     -LevelSequence="/Game/Timeshift/Cinematics/LS_Trailer.LS_Trailer"
     -MovieFolder=<out> -MovieName=frame -MovieFormat=PNG -MovieFrameRate=30
     -ResX=1920 -ResY=1080 -ForceRes -windowed -Unattended
   ```

   `-ForceRes` matters: without it the capture takes the window size (1280x800).
   Do **not** pass `-MovieCinematicMode=yes` if the player should be visible - it hides the pawn.
4. `make_narration_neural.py` records the voice with edge-tts and writes `narration_layout.json`,
   pushing a line later if the one before it would overrun.
5. `rebuild_compose.py` regenerates the audio graph in `compose.sh` from that layout - run it
   after changing the narration, or the mix will use stale timings.
6. `compose.sh` lays narration, music and titles over the frames and encodes.

## Notes

- The first 6 s of the render (frames 0-179) are an opening hero shot that is **cut** in
  `compose.sh` via `-start_number 180`. The frames are still rendered.
- Music is side-chain ducked against the narration, so the voice needs no manual level riding.
- Movie Render Queue is enabled in the uproject but is **not** what renders this. Its in-editor
  render exhausted RAM on this machine and its command-line manifest path crashed.
- The sequence camera ignores the focal length set on its spawnable template. Framing has to be
  done by moving the camera, not by choosing a lens.

## Music

`The Battle of 1066` by Patrick Patrikios, from the YouTube Audio Library. Check the library
entry for whether attribution is required before publishing. `Hero's Theme` by Twin Musicom is
also in this folder and is CC-BY, which definitely requires a credit.
