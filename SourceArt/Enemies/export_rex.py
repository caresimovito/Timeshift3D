"""Headless Blender: rig Rex Prime and export him with all actions, hit flinch included."""
SRC = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Enemies/rig_dino.py'
exec(compile(open(SRC).read(), SRC, 'exec'))
info = build('RexPrime')
print('REXRIG', info['path'], 'bones', info['bones'], 'tris', info['tris'], 'actions', info['actions'])
