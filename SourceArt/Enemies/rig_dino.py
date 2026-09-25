"""Auto-rig and animate a Meshy dinosaur in Blender, then export an FBX for Unreal.

Run inside Blender:  exec(open(r'.../rig_dino.py').read()); build('Raptor')

Pipeline per species:
  1. import the GLB, turn it so the head points +X, scale to game size, feet at Z=0
  2. decimate to a game-friendly triangle count
  3. find landmarks from the mesh (feet, legs, spine centre line, neck, head, tail)
  4. build an armature (root > pelvis > spine/neck/head, tail chain, 2 or 4 legs, arms or wings)
  5. skin with automatic weights
  6. key Idle / Walk / Run / Attack / Death / Hit actions (IK feet planted, then baked to FK)
  7. export SK_<name>.fbx with all actions
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

SRC = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Enemies/'
OUT = r'C:/repos/Unreal Projects/Timeshift3D/SourceArt/Enemies/Export/'
FPS = 30

# kind, length nose-to-tail (m, wingspan for the flyer), target tris, head fraction, chest fraction
SPECIES = {
    'Compy':         dict(kind='biped', length=1.1, tris=14000, head=0.11, chest=0.42),
    'Raptor':        dict(kind='biped', length=3.2, tris=26000, head=0.12, chest=0.45),
    'Dilophosaurus': dict(kind='biped', length=6.0, tris=30000, head=0.13, chest=0.45),
    'Triceratops':   dict(kind='quad',  length=8.0, tris=36000, head=0.24, chest=0.0),
    'Ankylosaur':    dict(kind='quad',  length=6.5, tris=32000, head=0.12, chest=0.0),
    'RiverAmbusher': dict(kind='quad',  length=9.0, tris=34000, head=0.17, chest=0.0, sprawl=True),
    'Spinosaurus':   dict(kind='biped', length=9.0, tris=34000, head=0.16, chest=0.45),
    'Stegosaurus':   dict(kind='quad',  length=9.0, tris=34000, head=0.09, chest=0.0),
    'Parasaurolophus': dict(kind='quad',  length=10.0, tris=34000, head=0.10, chest=0.0),
    'Ankylosaurus':  dict(kind='quad',  length=7.0, tris=32000, head=0.12, chest=0.0),
    'Dimorphodon':   dict(kind='ptero', length=2.6, tris=18000, head=0.30, chest=0.0),
    'Kulindadromeus': dict(kind='biped', length=1.6, tris=16000, head=0.14, chest=0.42),
    'Brontosaurus':  dict(kind='quad',  length=20.0, tris=36000, head=0.05, chest=0.0),
    'Pterosaur':     dict(kind='ptero', length=6.0, tris=26000, head=0.22, chest=0.0),
    'RexPrime':      dict(kind='biped', length=12.0, tris=40000, head=0.16, chest=0.46),
}


# ------------------------------------------------------------------ helpers
def clear_scene():
    for o in list(bpy.data.objects):
        if not o.name.startswith('SWC_Cam'):
            bpy.data.objects.remove(o, do_unlink=True)
    for a in list(bpy.data.actions):
        bpy.data.actions.remove(a)
    for arm in list(bpy.data.armatures):
        if arm.users == 0:
            bpy.data.armatures.remove(arm)


def select_only(o):
    bpy.ops.object.mode_set(mode='OBJECT') if bpy.context.object and bpy.context.object.mode != 'OBJECT' else None
    bpy.ops.object.select_all(action='DESELECT')
    o.select_set(True)
    bpy.context.view_layer.objects.active = o


def world_verts(o):
    mw = o.matrix_world
    return [mw @ v.co for v in o.data.vertices]


def centroid(pts):
    if not pts:
        return None
    s = Vector((0, 0, 0))
    for p in pts:
        s += p
    return s / len(pts)


# ------------------------------------------------------------------ 1-2 import and normalise
def import_mesh(name, spec):
    before = set(bpy.data.objects)
    bpy.ops.import_scene.gltf(filepath=SRC + name + '.glb')
    new = [o for o in bpy.data.objects if o not in before]
    mesh = [o for o in new if o.type == 'MESH'][0]
    for o in new:
        if o is not mesh:
            mesh.parent = None
            bpy.data.objects.remove(o, do_unlink=True)
    mesh.name = name
    select_only(mesh)
    bpy.ops.object.transform_apply(location=True, rotation=True, scale=True)
    # head points -Y in the Meshy output: turn it to +X
    mesh.data.transform(Matrix.Rotation(math.radians(90), 4, 'Z'))
    ws = [v.co for v in mesh.data.vertices]
    mn = Vector([min(p[k] for p in ws) for k in range(3)])
    mx = Vector([max(p[k] for p in ws) for k in range(3)])
    span = (mx.y - mn.y) if spec['kind'] == 'ptero' else (mx.x - mn.x)
    s = spec['length'] / span
    mesh.data.transform(Matrix.Scale(s, 4))
    mesh.data.transform(Matrix.Translation(Vector((0, 0, -mn.z * s))))
    # weld the vertices glTF splits along UV seams, otherwise skinning tears along every seam
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.remove_doubles(threshold=0.0005 * spec['length'])
    bpy.ops.object.mode_set(mode='OBJECT')
    # decimate
    tris = sum(len(p.vertices) - 2 for p in mesh.data.polygons)
    if tris > spec['tris']:
        dec = mesh.modifiers.new('dec', 'DECIMATE')
        dec.ratio = spec['tris'] / tris
        bpy.ops.object.modifier_apply(modifier='dec')
    for p in mesh.data.polygons:
        p.use_smooth = True
    return mesh


# ------------------------------------------------------------------ 3 landmarks
def midline_profile(V, xmin, xmax, bins=80, zcut=0.0):
    """Per X slice: centre Z and thickness of the body along the midline (legs excluded).

    Vertices below zcut (the legs) are ignored unless a slice has nothing above it."""
    prof = []
    width = []
    for i in range(bins):
        x0 = xmin + (xmax - xmin) * i / bins
        x1 = xmin + (xmax - xmin) * (i + 1) / bins
        sl_all = [p for p in V if x0 <= p.x < x1]
        sl = [p for p in sl_all if p.z > zcut] or sl_all
        if not sl:
            prof.append(None); width.append(0); continue
        hw = max(abs(p.y) for p in sl)
        mid = [p for p in sl if abs(p.y) < max(0.25 * hw, 0.01)]
        if len(mid) < 3:
            mid = sl
        zs = [p.z for p in mid]
        prof.append(((x0 + x1) / 2, (min(zs) + max(zs)) / 2, max(zs) - min(zs)))
        width.append(hw)
    return prof, width


def profile_at(prof, x):
    best = None
    for e in prof:
        if e is None:
            continue
        if best is None or abs(e[0] - x) < abs(best[0] - x):
            best = e
    return best


def find_feet(V, H, kind, spec):
    low = [p for p in V if p.z < 0.045 * H]
    if kind == 'biped':
        groups = {'L': [p for p in low if p.y > 0], 'R': [p for p in low if p.y <= 0]}
    else:
        groups = {}
        for side, sel in (('L', lambda p: p.y > 0), ('R', lambda p: p.y <= 0)):
            pts = [p for p in low if sel(p)]
            xs = sorted(p.x for p in pts)
            # split this side's footprints into back/front at the biggest gap along X
            gaps = [(xs[i + 1] - xs[i], (xs[i + 1] + xs[i]) / 2) for i in range(len(xs) - 1)]
            split = max(gaps)[1] if gaps else 0
            groups[side] = [p for p in pts if p.x < split]
            groups['F' + side] = [p for p in pts if p.x >= split]
    feet = {}
    for k, g in groups.items():
        if not g:
            continue
        c = centroid(g)
        feet[k] = dict(c=c, toe=max(g, key=lambda p: p.x), heel=min(g, key=lambda p: p.x))
    return feet


def leg_centre(V, side_sign, x_lo, x_hi, z_lo, z_hi):
    pts = [p for p in V if x_lo <= p.x <= x_hi and z_lo <= p.z <= z_hi and p.y * side_sign > 0]
    return centroid(pts)


def landmarks(mesh, spec):
    V = world_verts(mesh)
    kind = spec['kind']
    xmin = min(p.x for p in V); xmax = max(p.x for p in V)
    H = max(p.z for p in V)
    L = xmax - xmin
    zcut = {'biped': 0.45, 'quad': 0.3, 'ptero': 0.0}[kind] * H
    if spec.get('sprawl'):
        zcut = 0.2 * H
    prof, width = midline_profile(V, xmin, xmax, zcut=zcut)
    lm = dict(V=V, xmin=xmin, xmax=xmax, H=H, L=L, prof=prof)
    feet = find_feet(V, H, kind, spec) if kind != 'ptero' else {}
    lm['feet'] = feet
    legs = {}
    for k, f in feet.items():
        sign = 1 if f['c'].y > 0 else -1
        pc = profile_at(prof, f['c'].x)
        hip_z = pc[1] - 0.15 * pc[2]
        span = 0.12 * L if kind == 'biped' else 0.09 * L
        def at(fz):
            z = hip_z * fz
            c = leg_centre(V, sign, f['c'].x - span, f['c'].x + span, z - 0.05 * hip_z, z + 0.05 * hip_z)
            return c if c else Vector((f['c'].x, f['c'].y, z))
        top = at(0.8)
        hip = Vector((top.x, top.y * 0.75, hip_z))
        if kind == 'biped':
            knee = at(0.55); ankle = at(0.2)
            knee.x = max(knee.x, hip.x + 0.06 * hip_z)      # theropod knees point forward
        else:
            knee = at(0.5); ankle = at(0.12)
            if k.startswith('F'):
                knee.x = min(knee.x, hip.x - 0.03 * hip_z)  # front elbows point back
            else:
                knee.x = max(knee.x, hip.x + 0.04 * hip_z)
        ball = Vector((f['c'].x + 0.3 * (f['toe'].x - f['c'].x), f['c'].y, 0.02 * H))
        toe = Vector((f['toe'].x, f['c'].y, 0.01 * H))
        legs[k] = dict(hip=hip, knee=knee, ankle=ankle, ball=ball, toe=toe, sign=sign)
    lm['legs'] = legs
    # pelvis / shoulders along the centre line
    if kind == 'biped':
        px = (legs['L']['hip'].x + legs['R']['hip'].x) / 2
    elif kind == 'quad':
        px = (legs['L']['hip'].x + legs['R']['hip'].x) / 2
    else:
        px = xmin + 0.55 * L
    lm['pelvis'] = Vector((px, 0, profile_at(prof, px)[1]))
    head_base_x = xmax - spec['head'] * L
    lm['head_base'] = Vector((head_base_x, 0, profile_at(prof, head_base_x)[1]))
    snout = profile_at(prof, xmax - 0.01 * L)
    lm['snout'] = Vector((xmax, 0, snout[1]))
    if kind == 'quad':
        sx = (legs['FL']['hip'].x + legs['FR']['hip'].x) / 2
    else:
        sx = px + spec['chest'] * (head_base_x - px) if kind == 'biped' else xmin + 0.6 * L
    lm['shoulder'] = Vector((sx, 0, profile_at(prof, sx)[1]))
    tip = profile_at(prof, xmin + 0.01 * L)
    lm['tail_tip'] = Vector((xmin, 0, tip[1]))
    # biped arms
    if kind == 'biped':
        arms = {}
        pc = profile_at(prof, sx)
        for k, sign in (('L', 1), ('R', -1)):
            cand = [p for p in V if sx - 0.06 * L <= p.x <= sx + 0.12 * L and p.y * sign > 0.02 * L
                    and 0.15 * H < p.z < pc[1] - 0.25 * pc[2]]
            hand = min(cand, key=lambda p: p.z) if cand else Vector((sx + 0.06 * L, sign * 0.04 * L, pc[1] - 0.6 * pc[2]))
            sh = Vector((sx, sign * 0.035 * L, pc[1] - 0.2 * pc[2]))
            elbow = (sh + hand) / 2 + Vector((-0.02 * L, 0, 0))
            arms[k] = dict(shoulder=sh, elbow=elbow, hand=Vector(hand))
        lm['arms'] = arms
    if kind == 'ptero':
        wings = {}
        for k, sign in (('L', 1), ('R', -1)):
            side = [p for p in V if p.y * sign > 0]
            far = max(side, key=lambda p: abs(p.y))
            span = abs(far.y)
            base = Vector((lm['shoulder'].x, sign * 0.06 * span, lm['shoulder'].z))
            def wpt(f):
                pts = [p for p in side if abs(abs(p.y) - f * span) < 0.04 * span]
                c = centroid(pts)
                front = max(pts, key=lambda p: p.x) if pts else None
                return Vector((front.x - 0.03 * L if front else base.x, sign * f * span, c.z if c else base.z))
            wings[k] = dict(shoulder=base, elbow=wpt(0.3), wrist=wpt(0.55), tip=Vector((far.x, far.y, far.z)))
        lm['wings'] = wings
        # small hind legs trailing behind the pelvis
        for k, sign in (('L', 1), ('R', -1)):
            pz = lm['pelvis'].z
            legs[k] = dict(hip=Vector((lm['pelvis'].x, sign * 0.04 * L, pz)),
                           knee=Vector((lm['pelvis'].x - 0.08 * L, sign * 0.05 * L, pz - 0.01 * L)),
                           ankle=Vector((lm['pelvis'].x - 0.15 * L, sign * 0.05 * L, pz - 0.01 * L)),
                           ball=Vector((lm['pelvis'].x - 0.18 * L, sign * 0.05 * L, pz - 0.01 * L)),
                           toe=Vector((lm['pelvis'].x - 0.2 * L, sign * 0.05 * L, pz - 0.01 * L)), sign=sign)
    return lm


def centre_point(lm, x):
    p = profile_at(lm['prof'], x)
    return Vector((x, 0, p[1]))


# ------------------------------------------------------------------ 4 armature
def build_armature(name, lm, spec):
    arm_data = bpy.data.armatures.new(name + '_Skel')
    arm = bpy.data.objects.new('SK_' + name, arm_data)
    bpy.context.collection.objects.link(arm)
    select_only(arm)
    bpy.ops.object.mode_set(mode='EDIT')
    eb = arm_data.edit_bones
    L = lm['L']

    def bone(nm, head, tail, parent=None, connect=False, deform=True):
        b = eb.new(nm)
        b.head = head; b.tail = tail
        if (b.tail - b.head).length < 1e-4:
            b.tail = b.head + Vector((0, 0, 0.02 * L))
        b.parent = eb[parent] if parent else None
        b.use_connect = connect
        b.use_deform = deform
        return b

    pel = lm['pelvis']
    bone('root', Vector((pel.x, 0, 0)), Vector((pel.x + 0.1 * L, 0, 0)), deform=False)
    bone('pelvis', pel, pel + Vector((0.06 * L, 0, 0)), 'root')
    # spine: pelvis -> shoulder (3 bones)
    sh = lm['shoulder']
    prev = 'pelvis'
    pts = [centre_point(lm, pel.x + (sh.x - pel.x) * t) for t in (0.0, 0.34, 0.67, 1.0)]
    pts[0] = pel.copy(); pts[-1] = sh.copy()
    for i in range(3):
        bone('spine_%02d' % (i + 1), pts[i], pts[i + 1], prev, connect=(i > 0))
        prev = 'spine_%02d' % (i + 1)
    eb['pelvis'].tail = pel + (pts[1] - pel) * 0.3
    # neck: shoulder -> head base (2 bones), head: head base -> snout
    hb = lm['head_base']
    mid = centre_point(lm, (sh.x + hb.x) / 2)
    bone('neck_01', sh, mid, prev, connect=True)
    bone('neck_02', mid, hb, 'neck_01', connect=True)
    bone('head', hb, lm['snout'], 'neck_02', connect=True)
    # tail: pelvis -> tip (6 bones)
    tip = lm['tail_tip']
    prev = 'pelvis'
    tpts = [centre_point(lm, pel.x + (tip.x - pel.x) * (1 - (1 - t) ** 1.0)) for t in [i / 6 for i in range(7)]]
    tpts[0] = pel.copy(); tpts[-1] = tip.copy()
    for i in range(6):
        bone('tail_%02d' % (i + 1), tpts[i], tpts[i + 1], prev, connect=(i > 0))
        prev = 'tail_%02d' % (i + 1)
    # legs
    for k, g in lm['legs'].items():
        front = k.startswith('F')
        par = 'spine_03' if front else 'pelvis'
        pre = ('arm' if front else 'leg') + '_' + k[-1]
        bone(pre + '_upper', g['hip'], g['knee'], par)
        bone(pre + '_lower', g['knee'], g['ankle'], pre + '_upper', connect=True)
        bone(pre + '_foot', g['ankle'], g['ball'], pre + '_lower', connect=True)
        bone(pre + '_toe', g['ball'], g['toe'], pre + '_foot', connect=True)
        # IK helpers (not exported)
        bone('IK_' + pre, g['ankle'], g['ankle'] + Vector((0.08 * L, 0, 0)), 'root', deform=False)
        pole_dir = Vector((-1, 0, 0)) if front else Vector((1, 0, 0))
        pole = g['knee'] + pole_dir * 0.4 * L
        bone('POLE_' + pre, pole, pole + Vector((0, 0, 0.04 * L)), 'root', deform=False)
    if spec['kind'] == 'biped':
        for k, a in lm['arms'].items():
            bone('hand_arm_%s_upper' % k, a['shoulder'], a['elbow'], 'spine_03')
            bone('hand_arm_%s_lower' % k, a['elbow'], a['hand'], 'hand_arm_%s_upper' % k, connect=True)
    if spec['kind'] == 'ptero':
        for k, w in lm['wings'].items():
            bone('wing_%s_upper' % k, w['shoulder'], w['elbow'], 'spine_03')
            bone('wing_%s_lower' % k, w['elbow'], w['wrist'], 'wing_%s_upper' % k, connect=True)
            bone('wing_%s_finger' % k, w['wrist'], w['tip'], 'wing_%s_lower' % k, connect=True)
    bpy.ops.object.mode_set(mode='OBJECT')
    return arm


# ------------------------------------------------------------------ 5 skinning
def skin(mesh, arm):
    """Distance-based skinning that never crosses sides, then smoothed over the surface.

    Blender's heat weighting fails on Meshy meshes (not watertight), leaving limbs rigid,
    so weights are computed here: each vertex blends its 3 nearest bones by inverse distance."""
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    bpy.ops.object.parent_set(type='ARMATURE_NAME')
    mw = mesh.matrix_world
    segs = []
    for b in arm.data.bones:
        if not b.use_deform:
            continue
        side = 0
        if b.name.endswith(('_L', '_FL')) or '_L_' in b.name:
            side = 1
        if b.name.endswith(('_R', '_FR')) or '_R_' in b.name:
            side = -1
        segs.append((b.name, arm.matrix_world @ b.head_local, arm.matrix_world @ b.tail_local, side))
    L = max((s[2] - s[1]).length for s in segs) * 4
    def seg_dist(p, a, b):
        ab = b - a
        t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
        return (a + ab * t - p).length
    groups = {n: (mesh.vertex_groups.get(n) or mesh.vertex_groups.new(name=n)) for n, _, _, _ in segs}
    for v in mesh.data.vertices:
        p = mw @ v.co
        side = 1 if p.y > 0.01 * L else (-1 if p.y < -0.01 * L else 0)
        cands = []
        for n, a, b, sd in segs:
            if sd and side and sd != side:
                continue
            d = seg_dist(p, a, b)
            if n.endswith('_upper') and p.z > a.z:
                d *= 1.0 + 3.0 * min(1.0, (p.z - a.z) / max(0.05, 0.25 * a.z))   # flank above the hip stays with the torso
            elif n.startswith(('pelvis', 'spine', 'tail', 'neck')):
                d *= 0.85
            cands.append((d, n))
        cands.sort()
        near = cands[:4]
        ws = [(1.0 / (d * d + 1e-6), n) for d, n in near]
        tot = sum(w for w, _ in ws)
        for w, n in ws:
            if w / tot > 0.04:
                groups[n].add([v.index], w / tot, 'REPLACE')
    select_only(mesh)
    bpy.ops.object.mode_set(mode='WEIGHT_PAINT')
    bpy.ops.object.vertex_group_smooth(group_select_mode='ALL', factor=0.6, repeat=12)
    bpy.ops.object.vertex_group_normalize_all(lock_active=False)
    bpy.ops.object.mode_set(mode='OBJECT')
    weighted = sum(1 for v in mesh.data.vertices if len(v.groups) > 0)
    return weighted / max(1, len(mesh.data.vertices)), []


# ------------------------------------------------------------------ 6 animation
def leg_names(arm):
    return [b.name[3:] for b in arm.data.bones if b.name.startswith('IK_')]


def pole_angle(base, ik, pole_loc):
    """Pole angle that keeps a 2-bone chain untwisted at rest (standard Blender formula)."""
    def signed_angle(v, u, normal):
        a = v.angle(u)
        if v.cross(u).angle(normal) < 1:
            a = -a
        return a
    base_dir = base.tail_local - base.head_local
    pole_normal = (ik.tail_local - base.head_local).cross(pole_loc - base.head_local)
    projected = pole_normal.cross(base_dir)
    x_axis = base.matrix_local.to_3x3() @ Vector((1, 0, 0))
    return signed_angle(x_axis, projected, base_dir)


def setup_ik(arm):
    for pre in leg_names(arm):
        pb = arm.pose.bones[pre + '_lower']
        c = pb.constraints.new('IK')
        c.target = arm; c.subtarget = 'IK_' + pre
        c.pole_target = arm; c.pole_subtarget = 'POLE_' + pre
        bones = arm.data.bones
        c.pole_angle = pole_angle(bones[pre + '_upper'], bones[pre + '_lower'], bones['POLE_' + pre].head_local)
        c.chain_count = 2


def key_all(arm, frame):
    for pb in arm.pose.bones:
        pb.keyframe_insert('location', frame=frame)
        pb.keyframe_insert('rotation_quaternion', frame=frame)


def reset_pose(arm):
    for pb in arm.pose.bones:
        pb.location = (0, 0, 0)
        pb.rotation_mode = 'QUATERNION'
        pb.rotation_quaternion = (1, 0, 0, 0)
        pb.scale = (1, 1, 1)


def setloc(pb, v):
    """Set a pose bone's location from a WORLD-space offset."""
    pb.location = pb.bone.matrix_local.to_3x3().inverted() @ Vector(v)


def rot(pb, axis, deg):
    """Rotate a pose bone about a WORLD axis (approximately; bones are close to rest)."""
    m = pb.bone.matrix_local.to_3x3()
    local_axis = (m.inverted() @ Vector(axis)).normalized()
    q = pb.rotation_quaternion.copy()
    q.rotate(Matrix.Rotation(math.radians(deg), 3, local_axis).to_quaternion())
    pb.rotation_quaternion = q


def gait_phases(kind, mode):
    if kind == 'biped' or kind == 'ptero':
        return {'leg_L': 0.0, 'leg_R': 0.5}
    if mode == 'Run':
        return {'leg_L': 0.0, 'arm_R': 0.0, 'leg_R': 0.5, 'arm_L': 0.5}
    return {'leg_L': 0.0, 'arm_L': 0.25, 'leg_R': 0.5, 'arm_R': 0.75}


def foot_offset(phase, stride, lift, duty):
    """Foot position relative to its rest spot for a gait phase in [0,1)."""
    if phase < duty:                      # stance: slide back on the ground
        t = phase / duty
        return Vector((stride * (0.5 - t), 0, 0))
    t = (phase - duty) / (1 - duty)       # swing: arc forward
    return Vector((stride * (-0.5 + t), 0, lift * math.sin(math.pi * t)))


def make_action(arm, name, frames, pose_fn, loop=True):
    act = bpy.data.actions.new(name)
    arm.animation_data_create()
    arm.animation_data.action = act
    for f in range(frames + (1 if loop else 0)):
        reset_pose(arm)
        pose_fn(arm, f / frames if loop else f / max(1, frames - 1), f)
        key_all(arm, f + 1)
    return act


def chain(arm, prefix, n):
    return [arm.pose.bones['%s_%02d' % (prefix, i + 1)] for i in range(n) if ('%s_%02d' % (prefix, i + 1)) in arm.pose.bones]


def animate(arm, lm, spec):
    kind = spec['kind']
    L = lm['L']
    legs = leg_names(arm)
    hip_h = max((lm['legs'][k]['hip'].z for k in lm['legs']), default=0.2 * L)
    tail = chain(arm, 'tail', 6)
    spine = chain(arm, 'spine', 3)
    pbs = arm.pose.bones

    def body(t, bob, sway, head_nod, tail_amp, tail_speed=1.0):
        setloc(pbs['pelvis'], (0, 0, bob * 0.5 * (1 + math.cos(4 * math.pi * t))))
        for i, b in enumerate(tail):
            rot(b, (0, 0, 1), tail_amp * math.sin(2 * math.pi * (t * tail_speed) - 0.6 * i))
            rot(b, (0, 1, 0), 0.3 * tail_amp * math.sin(4 * math.pi * t - 0.5 * i))
        for b in spine:
            rot(b, (0, 0, 1), -sway * math.sin(2 * math.pi * t))
        rot(pbs['neck_01'], (0, 1, 0), head_nod * math.sin(4 * math.pi * t))
        rot(pbs['head'], (0, 1, 0), -head_nod * math.sin(4 * math.pi * t))

    def feet(t, stride, lift, duty, mode):
        ph = gait_phases(kind, mode)
        for pre in legs:
            off = foot_offset((t + ph.get(pre, 0)) % 1.0, stride, lift, duty) if stride else Vector()
            setloc(pbs['IK_' + pre], off)

    if kind == 'ptero':
        def flap(amp, speed):
            def f(arm, t, fr):
                a = amp * math.sin(2 * math.pi * t * speed)
                for k, s in (('L', 1), ('R', -1)):
                    rot(pbs['wing_%s_upper' % k], (1, 0, 0), -s * a)
                    rot(pbs['wing_%s_lower' % k], (1, 0, 0), -s * a * 0.5)
                    rot(pbs['wing_%s_finger' % k], (1, 0, 0), -s * a * 0.3)
                setloc(pbs['pelvis'], (0, 0, 0.03 * L * math.sin(2 * math.pi * t * speed + 1.5)))
                body(t, 0, 0, 3, 4)
            return f
        make_action(arm, 'Idle', 60, flap(8, 1))
        make_action(arm, 'Walk', 40, flap(24, 1))
        make_action(arm, 'Run', 24, flap(30, 1))

        def dive(arm, t, fr):
            a = math.sin(math.pi * t)
            rot(pbs['pelvis'], (0, 1, 0), 35 * a)
            for k, s in (('L', 1), ('R', -1)):
                rot(pbs['wing_%s_upper' % k], (1, 0, 0), s * 25 * a)
                rot(pbs['leg_%s_upper' % k], (0, 1, 0), -60 * a)
            rot(pbs['head'], (0, 1, 0), -20 * a)
        make_action(arm, 'Attack', 24, dive, loop=False)

        def fall(arm, t, fr):
            rot(pbs['pelvis'], (1, 0, 0), 120 * t)
            setloc(pbs['pelvis'], (0, 0, -0.3 * L * t))
            for k, s in (('L', 1), ('R', -1)):
                rot(pbs['wing_%s_upper' % k], (1, 0, 0), s * 50 * t)
        make_action(arm, 'Death', 40, fall, loop=False)

        def flinch_air(arm, t, fr):
            a = math.sin(math.pi * min(1.0, t * 1.15)) ** 0.7
            shock = max(0.0, 1 - abs(t - 0.12) / 0.12)
            rot(pbs['pelvis'], (0, 1, 0), -22 * a)
            setloc(pbs['pelvis'], (-0.04 * L * a, 0, 0.02 * L * shock))
            for k, s in (('L', 1), ('R', -1)):
                rot(pbs['wing_%s_upper' % k], (1, 0, 0), s * 32 * a)
                rot(pbs['wing_%s_lower' % k], (1, 0, 0), s * 18 * shock)
            rot(pbs['head'], (0, 1, 0), -25 * a)
            rot(pbs['head'], (0, 0, 1), 12 * shock)
        make_action(arm, 'Hit', 14, flinch_air, loop=False)
        return

    sprawl = spec.get('sprawl', False)
    walk_stride = (0.9 if kind == 'biped' else 0.6) * hip_h
    run_stride = walk_stride * 1.8

    def idle(arm, t, fr):
        feet(t, 0, 0, 0.6, 'Walk')
        body(t, -0.01 * hip_h, 0, 4, 6, 1)
        rot(pbs['neck_01'], (0, 0, 1), 12 * math.sin(2 * math.pi * t))
        rot(pbs['spine_01'], (0, 1, 0), 1.5 * math.sin(4 * math.pi * t))
    make_action(arm, 'Idle', 60, idle)

    def gait(stride, lift, duty, bob, sway, nod, tail_amp, mode):
        def f(arm, t, fr):
            feet(t, stride, lift, duty, mode)
            body(t, -bob, sway, nod, tail_amp)
            if sprawl:
                for b in spine:
                    rot(b, (0, 0, 1), 6 * math.sin(2 * math.pi * t))
        return f
    make_action(arm, 'Walk', 32, gait(walk_stride, 0.25 * hip_h, 0.6, 0.04 * hip_h, 3, 3, 8, 'Walk'))
    make_action(arm, 'Run', 20, gait(run_stride, 0.35 * hip_h, 0.45, 0.08 * hip_h, 4, 5, 10, 'Run'))

    def attack(arm, t, fr):
        feet(0, 0, 0, 0.6, 'Walk')
        wind = max(0.0, 1 - abs(t - 0.25) / 0.25) if t < 0.5 else 0
        strike = max(0.0, 1 - abs(t - 0.55) / 0.2)
        setloc(pbs['pelvis'], (0.15 * hip_h * strike - 0.08 * hip_h * wind, 0, -0.05 * hip_h * wind))
        rot(pbs['spine_01'], (0, 1, 0), 8 * wind - 10 * strike)
        rot(pbs['neck_01'], (0, 1, 0), -15 * wind + 25 * strike)
        rot(pbs['head'], (0, 1, 0), 10 * strike)
        if 'Triceratops' in arm.name or kind == 'quad':
            rot(pbs['head'], (0, 1, 0), 20 * strike)       # horn thrust / bite
        for i, b in enumerate(tail):
            rot(b, (0, 0, 1), 12 * strike * math.sin(i))
    make_action(arm, 'Attack', 24, attack, loop=False)

    def death(arm, t, fr):
        e = t * t * (3 - 2 * t)
        feet(0, 0, 0, 0.6, 'Walk')
        rot(pbs['root'], (1, 0, 0), 88 * e)
        setloc(pbs['root'], (0, 0, 0.07 * hip_h * math.sin(math.pi * min(1, t * 1.5))))
        rot(pbs['neck_01'], (0, 1, 0), 20 * e)
        for i, b in enumerate(tail):
            rot(b, (0, 0, 1), 6 * e)
    make_action(arm, 'Death', 40, death, loop=False)

    def flinch(arm, t, fr):
        # sharp recoil on impact, then settle back - about half a second
        feet(0, 0, 0, 0.6, 'Walk')
        a = math.sin(math.pi * min(1.0, t * 1.15)) ** 0.7
        shock = max(0.0, 1 - abs(t - 0.12) / 0.12)
        setloc(pbs['pelvis'], (-0.12 * hip_h * a, 0, -0.06 * hip_h * shock))
        rot(pbs['spine_01'], (0, 1, 0), -13 * a)
        rot(pbs['neck_01'], (0, 1, 0), -22 * a - 8 * shock)
        rot(pbs['neck_01'], (0, 0, 1), 9 * shock)
        rot(pbs['head'], (0, 1, 0), -16 * a)
        rot(pbs['head'], (0, 0, 1), 12 * shock)
        for i, b in enumerate(tail):
            rot(b, (0, 0, 1), 11 * a * math.sin(1.2 * i + 1.5))
    make_action(arm, 'Hit', 14, flinch, loop=False)


def bake_actions(arm):
    select_only(arm)
    bpy.ops.object.mode_set(mode='POSE')
    for act in list(bpy.data.actions):
        if act.name.endswith('_baked'):
            continue
        arm.animation_data.action = act
        fr = act.frame_range
        bpy.ops.pose.select_all(action='SELECT')
        bpy.ops.nla.bake(frame_start=int(fr[0]), frame_end=int(fr[1]), only_selected=False, visual_keying=True,
                         clear_constraints=False, use_current_action=False, bake_types={'POSE'})
        baked = arm.animation_data.action
        name = act.name
        bpy.data.actions.remove(act)
        baked.name = name
        baked.use_fake_user = True
    bpy.ops.object.mode_set(mode='OBJECT')
    for pb in arm.pose.bones:
        for c in list(pb.constraints):
            pb.constraints.remove(c)


# ------------------------------------------------------------------ 7 export
def export(name, mesh, arm):
    import os
    os.makedirs(OUT, exist_ok=True)
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True); arm.select_set(True)
    bpy.context.view_layer.objects.active = arm
    arm.animation_data.action = bpy.data.actions.get('Idle')
    bpy.ops.export_scene.fbx(filepath=OUT + 'SK_%s.fbx' % name, use_selection=True, global_scale=1.0,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                             add_leaf_bones=False, use_armature_deform_only=True,
                             bake_anim=True, bake_anim_use_all_actions=True, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
                             path_mode='COPY', embed_textures=True, mesh_smooth_type='FACE')
    return OUT + 'SK_%s.fbx' % name


def export_action(name, mesh, arm, action):
    """Export one action on its own, for importing onto a skeleton Unreal already has."""
    import os
    os.makedirs(OUT, exist_ok=True)
    act = bpy.data.actions.get(action)
    if act is None:
        raise Exception('no action %s' % action)
    bpy.ops.object.select_all(action='DESELECT')
    arm.select_set(True)                      # armature only: an animation-only FBX
    bpy.context.view_layer.objects.active = arm
    arm.animation_data.action = act
    fr = act.frame_range
    bpy.context.scene.frame_start = int(fr[0])
    bpy.context.scene.frame_end = int(fr[1])          # just this action, not Blender's default 250
    path = OUT + 'SK_%s_%s.fbx' % (name, action)
    bpy.ops.export_scene.fbx(filepath=path, use_selection=True, global_scale=1.0,
                             apply_unit_scale=True, apply_scale_options='FBX_SCALE_NONE',
                             add_leaf_bones=False, use_armature_deform_only=True,
                             object_types={'ARMATURE'},
                             bake_anim=True, bake_anim_use_all_actions=False, bake_anim_use_nla_strips=False,
                             bake_anim_force_startend_keying=True, bake_anim_simplify_factor=0.0,
                             path_mode='COPY', embed_textures=False, mesh_smooth_type='FACE')
    return path


def build(name, do_export=True, only_action=None):
    spec = SPECIES[name]
    clear_scene()
    bpy.context.scene.render.fps = FPS
    mesh = import_mesh(name, spec)
    lm = landmarks(mesh, spec)
    arm = build_armature(name, lm, spec)
    cover, empty = skin(mesh, arm)
    setup_ik(arm)
    animate(arm, lm, spec)
    bake_actions(arm)
    if only_action:
        path = export_action(name, mesh, arm, only_action)
    else:
        path = export(name, mesh, arm) if do_export else None
    return dict(name=name, tris=sum(len(p.vertices) - 2 for p in mesh.data.polygons), cover=round(cover, 3),
                bones=len(arm.data.bones), actions=[a.name for a in bpy.data.actions], path=path,
                feet=sorted(lm['legs'].keys()), H=round(lm['H'], 2), L=round(lm['L'], 2))
