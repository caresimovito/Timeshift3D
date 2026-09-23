"""Headless Blender: rebuild each dinosaur rig and export its Hit flinch on its own.

Each file holds only the Hit action, for importing onto the skeleton Unreal already has.
Run:  blender --background --python export_hit_anims.py
"""
import sys
import bpy

SRC = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Enemies/rig_dino.py'
exec(compile(open(SRC).read(), SRC, 'exec'))

for name in ['Compy', 'Raptor', 'Dilophosaurus', 'Triceratops', 'Ankylosaur',
             'RiverAmbusher', 'Pterosaur']:
    try:
        info = build(name, only_action='Hit')
        print('HITANIM %s -> %s (bones %d)' % (name, info['path'], info['bones']))
    except Exception as e:
        print('HITANIM FAILED %s: %s' % (name, e))
