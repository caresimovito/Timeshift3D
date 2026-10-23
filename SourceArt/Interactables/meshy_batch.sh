#!/bin/bash
# Meshy text-to-3D for the remaining pickups, all in parallel (user 2026-10-23: "use meshy to build the others in parallel")
S="C:/repos/Unreal Projects/Timeshift3D/SourceArt/Interactables"
run() {  # name, prompt, texture prompt
  mkdir -p "$S/$1"
  MESHY_POLY=30000 python -I C:/agentpy/meshy_t23d.py "$S/$1/$1_meshy_raw.glb" "$2" "$3" > "C:/agentpy/meshy_logs/$1.log" 2>&1
  echo "[$1] exit $? $(tail -1 C:/agentpy/meshy_logs/$1.log)"
}
mkdir -p C:/agentpy/meshy_logs
run SauropodEgg "a single huge long oval sauropod dinosaur egg, cream white shell with brown speckles, lying half buried in a small mound of warm sand, realistic game prop pickup, one object" "cream white eggshell with brown speckles, warm golden sand" &
run Fury "a small cluster of jagged spiky fiery red and orange prehistoric mushrooms with sharp pointed caps, realistic game prop pickup, one compact object" "vivid fiery red and orange mushroom caps, dark red stems, glowing hot edges" &
run Adrenaline "a short thorny branch covered in clusters of bright yellow glowing berries, realistic game prop pickup, one compact object, lying on the ground" "bright yellow and golden berries, dark green thorny branch, small green leaves" &
run Hide "a bundle of large dark purple camouflage leaves curled together like a cloak, realistic game prop pickup, one compact object, lying on the ground" "deep purple and violet leaves with dark veins, slightly glossy" &
run Regen "a small glowing succulent plant with thick juicy pointed leaves like aloe vera, in a clump of soil, realistic game prop pickup, one compact object" "teal and turquoise succulent leaves with pale green tips, dark soil" &
run Armour "a set of primitive armour plates made of bone and dinosaur scales tied together with leather straps, stacked on the ground, realistic game prop pickup, one compact object" "off-white bone plates, grey-blue scales, brown leather straps" &
run MorphAmber "a large polished chunk of golden amber with a small prehistoric insect trapped inside, resting on a small rock, realistic game prop pickup, one object" "translucent glowing golden orange amber, dark insect inside, grey rock" &
run Stones "a small neat pile of six round smooth grey river stones for throwing, realistic game prop pickup, one compact object" "smooth grey and brown river stones, slightly wet look" &
wait
echo "[BATCH] all done"
