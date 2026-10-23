# Procedural Regen coil mesh (user 2026-10-23 Regen concept: green / gold light ribbons coiling around his arms, legs and
# torso). A flat ribbon following a helix: unit radius, 2.25 turns over height 1 along +Z (pivot at the base), the strip
# faces outward with a slight twist, width 0.09 along Z. Scaled per bone in the game (radius ~10-25 cm, length = bone).
# UV: U = 0..1 along the whole ribbon (the material pans along it), V = 0..1 across. Writes an OBJ (cm units, size 100).
import sys, math
TURNS, SEG, W = 2.25, 180, 0.09
verts, uvs, faces = [], [], []
for i in range(SEG + 1):
    t = i / SEG
    a = t * TURNS * 2 * math.pi
    z = t
    # ribbon edge offsets along the helix axis, tapering at both ends
    taper = min(1.0, t / 0.08, (1 - t) / 0.08)
    hw = W * 0.5 * taper
    r = 1.0
    for s, v in ((-1, 0.0), (1, 1.0)):
        verts.append((r * math.cos(a) * 100, r * math.sin(a) * 100, (z + s * hw) * 100))
        uvs.append((t, v))
for i in range(SEG):
    a0, b0, a1, b1 = 2 * i + 1, 2 * i + 2, 2 * i + 3, 2 * i + 4
    faces.append((a0, a1, b1, b0))
out = sys.argv[1]
with open(out, "w") as f:
    f.write("# SM_RegenCoil - procedural helix ribbon\n")
    for v in verts:
        f.write("v %.4f %.4f %.4f\n" % v)
    for uv in uvs:
        f.write("vt %.4f %.4f\n" % uv)
    for q in faces:
        f.write("f %d/%d %d/%d %d/%d %d/%d\n" % tuple(x for k in q for x in (k, k)))
print("ok", len(verts), "verts", len(faces), "quads")
