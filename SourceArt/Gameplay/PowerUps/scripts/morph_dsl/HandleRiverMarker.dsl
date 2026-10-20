(fn HandleRiverMarker ()
  ; the M "river marker" dev key was removed 2026-10-20 (M is the morph key now; DropRiverMarker is left unused).
  ; This function still has to chain on to the B terrain-marker check.
  (CallFunction|HandleTerrainMarker self))
