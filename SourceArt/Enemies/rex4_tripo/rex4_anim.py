# Rex4 animation authoring (headless Blender). Usage:
#   blender -b --python rex4_anim.py -- [Idle Walk Run Roar Bite Hit Death]
# Own FK from rest matrices + Newton leg IK (feet locked to world targets), keys written straight to fcurves.
import bpy, math, sys
from mathutils import Matrix, Vector as V, Euler

BLEND = r"C:\repos\Unreal Projects\Timeshift3D\SourceArt\Enemies\rex4_tripo\rex4_rig.blend"
FPS = 30
bpy.ops.wm.open_mainfile(filepath=BLEND)
arm = bpy.data.objects["Rex4_Rig"]
B = arm.data.bones
ORDER = [b.name for b in B]
PARENT = {b.name: (b.parent.name if b.parent else None) for b in B}
R = {b.name: b.matrix_local.copy() for b in B}
REL = {n: (R[PARENT[n]].inverted() @ R[n]) if PARENT[n] else R[n] for n in ORDER}
LEN = {b.name: b.length for b in B}
for pb in arm.pose.bones:
    pb.rotation_mode = 'XYZ'


def fk(rot, loc, only=None):
    """rot: name->(x,y,z) euler; loc: name->Vector (bone-local). Returns name->posed 4x4 (armature space)."""
    M = {}
    for n in ORDER:
        if only is not None and n not in only:
            continue
        L = Matrix.Translation(loc.get(n, V((0, 0, 0)))) @ Euler(rot.get(n, (0, 0, 0)), 'XYZ').to_matrix().to_4x4()
        p = PARENT[n]
        M[n] = (M[p] @ REL[n] @ L) if p else (REL[n] @ L)
    return M


def head(M, n):
    return M[n].translation.copy()


def tail(M, n):
    return M[n] @ V((0, LEN[n], 0))


def xz_ang(a, b):
    return math.atan2(b.z - a.z, b.x - a.x)


CHAIN = {s: ["root", "pelvis", "thigh_" + s, "calf_" + s, "foot_" + s, "toe_" + s] for s in ("l", "r")}
M0 = fk({}, {})
REST = {}
for s in ("l", "r"):
    REST[s] = dict(ball=head(M0, "toe_" + s), tip=tail(M0, "toe_" + s), ankle=head(M0, "foot_" + s),
                   meta=xz_ang(head(M0, "foot_" + s), head(M0, "toe_" + s)), toe=xz_ang(head(M0, "toe_" + s), tail(M0, "toe_" + s)))
RP3 = R["pelvis"].to_3x3()
RROOT3 = R["root"].to_3x3()


def pelvis_loc(world_offset):
    return RP3.inverted() @ V(world_offset)


def solve_leg(s, rot, loc, ball_t, meta_t, guess):
    """Newton on (thigh, calf, foot) local X so the ball sits at ball_t (x,z) with ankle->ball XZ angle meta_t."""
    q = list(guess)
    names = ["thigh_" + s, "calf_" + s, "foot_" + s]
    only = set(CHAIN[s])

    def F(qq):
        r = dict(rot)
        for n, a in zip(names, qq):
            e = r.get(n, (0, 0, 0)); r[n] = (a, e[1], e[2])
        M = fk(r, loc, only)
        b = head(M, "toe_" + s); a_ = head(M, "foot_" + s)
        return [b.x - ball_t[0], b.z - ball_t[1], math.atan2(math.sin(xz_ang(a_, b) - meta_t), math.cos(xz_ang(a_, b) - meta_t))]
    res = F(q)
    for _ in range(12):
        if max(abs(x) for x in res) < 1e-4:
            break
        J = Matrix(((0.0,) * 3,) * 3)
        for j in range(3):
            qq = list(q); qq[j] += 1e-4
            rj = F(qq)
            for i in range(3):
                J[i][j] = (rj[i] - res[i]) / 1e-4
        try:
            dq = J.inverted() @ V(res)
        except ValueError:
            break
        step = max(1.0, max(abs(x) for x in dq) / 0.3)
        q = [q[i] - dq[i] / step for i in range(3)]
        res = F(q)
    return q, max(abs(x) for x in res)


def solve_toe(s, rot, loc, toe_t, guess):
    a = guess
    only = set(CHAIN[s])
    for _ in range(8):
        def f(x):
            r = dict(rot); e = r.get("toe_" + s, (0, 0, 0)); r["toe_" + s] = (x, e[1], e[2])
            M = fk(r, loc, only)
            return math.atan2(math.sin(xz_ang(head(M, "toe_" + s), tail(M, "toe_" + s)) - toe_t), math.cos(xz_ang(head(M, "toe_" + s), tail(M, "toe_" + s)) - toe_t))
        y = f(a)
        if abs(y) < 1e-4:
            break
        d = (f(a + 1e-4) - y) / 1e-4
        if abs(d) < 1e-6:
            break
        a -= y / d
    return a


def smooth(u):
    u = max(0.0, min(1.0, u)); return u * u * (3 - 2 * u)


def track(keys, t):
    """keys: sorted [(t, v)], smoothstep between keys, clamped at ends."""
    if t <= keys[0][0]:
        return keys[0][1]
    for (t0, v0), (t1, v1) in zip(keys, keys[1:]):
        if t0 <= t <= t1:
            return v0 + (v1 - v0) * smooth((t - t0) / (t1 - t0))
    return keys[-1][1]


def periodic(pts, u):
    pts = sorted(pts); n = len(pts)
    for i in range(n):
        u0, v0 = pts[i]; u1, v1 = pts[(i + 1) % n]
        if i == n - 1:
            u1 += 1.0
        uu = u if u >= u0 else u + 1.0
        if u0 <= uu <= u1:
            return v0 + (v1 - v0) * (0.5 - 0.5 * math.cos(math.pi * (uu - u0) / (u1 - u0)))
    return pts[0][1]


class Clip:
    def __init__(self, name, nframes):
        self.name, self.n = name, nframes
        old = bpy.data.actions.get(name)
        if old:
            bpy.data.actions.remove(old)
        self.act = bpy.data.actions.new(name); self.act.use_fake_user = True
        if not arm.animation_data:
            arm.animation_data_create()
        arm.animation_data.action = self.act
        self.curves = {}
        self.stats = {"res": 0.0, "slide": {"l": [], "r": []}}

    def key(self, f, rot, loc):
        rot = {n: rot.get(n, (0.0, 0.0, 0.0)) for n in ORDER}          # key EVERY bone: unkeyed bones keep stale poses
        loc = dict(loc); loc.setdefault("root", V((0, 0, 0))); loc.setdefault("pelvis", V((0, 0, 0)))
        for n, e in rot.items():
            for i in range(3):
                self._k('pose.bones["%s"].rotation_euler' % n, i, f, e[i])
        for n, l in loc.items():
            for i in range(3):
                self._k('pose.bones["%s"].location' % n, i, f, l[i])

    def _k(self, path, i, f, v):
        k = (path, i)
        if k not in self.curves:
            self.curves[k] = self.act.fcurve_ensure_for_datablock(arm, path, index=i)
            self.curves[k].keyframe_points.clear()
        self.curves[k].keyframe_points.insert(f, v, options={'FAST'})

    def done(self):
        for c in self.curves.values():
            for kp in c.keyframe_points:
                kp.interpolation = 'LINEAR'
        self.act.frame_range = (0, self.n)
        print("[ANIM] %-6s frames %d curves %d worst IK residual %.4f" % (self.name, self.n, len(self.curves), self.stats["res"]))


JAW_CLOSED = -0.30
GUESS = {"l": [0.0, 0.0, 0.0], "r": [0.0, 0.0, 0.0]}


def plant_legs(clip, rot, loc, targets, toe_targets=None):
    """targets: side -> (ball_x, ball_z, meta). Solves and writes leg rotations into rot."""
    for s, (bx, bz, mt) in targets.items():
        q, res = solve_leg(s, rot, loc, (bx, bz), mt, GUESS[s])
        GUESS[s] = q
        clip.stats["res"] = max(clip.stats["res"], res)
        for n, a in zip(["thigh_" + s, "calf_" + s, "foot_" + s], q):
            rot[n] = (a, 0.0, 0.0)
        tt = (toe_targets or {}).get(s, REST[s]["toe"])
        rot["toe_" + s] = (solve_toe(s, rot, loc, tt, rot.get("toe_" + s, (0, 0, 0))[0]), 0.0, 0.0)


def planted(s):
    return (REST[s]["ball"].x, REST[s]["ball"].z, REST[s]["meta"])


# ---------------------------------------------------------------- locomotion
def locomotion(name, T, VEL, DUTY, LIFT, CROUCH, BOB, PITCH, META, NECK, TAILAMP, ARMAMP):
    n = int(round(T * FPS)); clip = Clip(name, n)
    S = VEL * DUTY * T
    XC = 0.5 * (REST["l"]["ball"].x + REST["l"]["ankle"].x) + 0.05
    meta = [(u, REST["l"]["meta"] + math.radians(d)) for u, d in META]
    for f in range(n + 1):
        u = (f % n) / n
        rot = {}; loc = {}
        bob = -CROUCH + BOB * math.cos(2 * math.pi * 2 * (u - 0.31))
        pitch = PITCH + math.radians(1.2) * math.sin(2 * math.pi * 2 * (u - 0.1))
        side = math.sin(2 * math.pi * (u - 0.31))
        loc["pelvis"] = pelvis_loc((0, 0, bob)); rot["pelvis"] = (pitch, 0, 0)
        targets = {}; toes = {}
        for s, us in (("l", u), ("r", (u + 0.5) % 1.0)):
            bz0 = REST[s]["ball"].z
            if us < DUTY:
                bx = XC + S / 2 - (us / DUTY) * S; bz = bz0; toe = REST[s]["toe"]
            else:
                w = (us - DUTY) / (1 - DUTY); e = w * w * (3 - 2 * w)
                bx = XC - S / 2 + e * S
                bz = bz0 + LIFT * math.sin(math.pi * min(1.0, w ** 0.85))
                toe = REST[s]["toe"] + (math.radians(-55) - REST[s]["toe"]) * math.sin(math.pi * min(1.0, w / 0.85)) if w < 0.85 else REST[s]["toe"]
            targets[s] = (bx, bz, periodic(meta, us)); toes[s] = toe
            if us < DUTY:
                clip.stats["slide"][s].append(bx)
        rot["spine_01"] = (0, math.radians(1.8) * side, math.radians(1.5) * side)
        rot["spine_03"] = (-pitch * 0.5, 0, 0)
        look = math.radians(5.0) * math.sin(2 * math.pi * 0.5 * u + 0.6)          # slow look across the 2-cycle span
        rot["neck_01"] = (-pitch * 0.8 + NECK + math.radians(2.0) * math.sin(2 * math.pi * 2 * (u - 0.15)), 0, -math.radians(3.0) * side + look * 0.5)
        rot["neck_02"] = (math.radians(1.5) * math.sin(2 * math.pi * 2 * (u - 0.22)), 0, -math.radians(2.0) * side + look * 0.3)
        rot["head"] = (math.radians(3.0) * math.sin(2 * math.pi * 2 * (u - 0.3)), math.radians(2.0) * side, look * 0.2)
        rot["jaw"] = (JAW_CLOSED + 0.02 * math.sin(2 * math.pi * 2 * u), 0, 0)
        for i, amp in enumerate(TAILAMP):
            lag = 0.06 * (i + 1)
            rot["tail_0%d" % (i + 1)] = (math.radians(0.8 + 0.3 * i) * math.sin(2 * math.pi * 2 * (u - 0.31 - lag)) - pitch * (0.6 if i == 0 else 0), 0,
                                         -math.radians(amp) * math.sin(2 * math.pi * (u - 0.31 - lag)))
        for s, sg in (("l", 1), ("r", -1)):
            rot["upperarm_" + s] = (math.radians(ARMAMP) * sg * math.sin(2 * math.pi * (u - 0.2)), 0, 0)
            rot["lowerarm_" + s] = (-0.15 + math.radians(ARMAMP * 0.7) * sg * math.sin(2 * math.pi * (u - 0.3)), 0, 0)
        plant_legs(clip, rot, loc, targets, toes)
        clip.key(f, rot, loc)
    for s in ("l", "r"):
        xs = clip.stats["slide"][s]
        steps = [xs[i] - xs[i + 1] for i in range(len(xs) - 1) if 0 < xs[i] - xs[i + 1] < 1]
        print("[ANIM]   %s stance ball dx/frame %.4f (expect %.4f)" % (s, sum(steps) / max(1, len(steps)), VEL / FPS))
    clip.done()


def make_walk():
    locomotion("Rex4_Walk", 2.0, 1.6, 0.62, 0.55, 0.20, 0.045, 0.0,
               [(0.00, -3), (0.30, -11), (0.48, -26), (0.62, -51), (0.76, -61), (0.90, -25), (0.985, -6)],
               0.02, (2.0, 3.0, 4.5, 6.0, 7.0), 4)


def make_run():
    locomotion("Rex4_Run", 1.0, 6.0, 0.42, 1.00, 0.42, 0.10, math.radians(8),
               [(0.00, -3), (0.20, -14), (0.33, -34), (0.42, -60), (0.60, -74), (0.85, -28), (0.97, -6)],
               0.10, (1.5, 2.5, 3.5, 4.5, 5.0), 7)


# ---------------------------------------------------------------- planted clips
def planted_clip(name, seconds, chans, ploc_keys=None, root_keys=None, plant_until=None, extra=None):
    """chans: (bone, axis_index) -> keys [(t, v)]; ploc_keys: axis(0 fwd x,1 y,2 up z) -> keys (world metres)."""
    n = int(round(seconds * FPS)); clip = Clip(name, n)
    last_leg = None
    for f in range(n + 1):
        t = f / FPS
        rot = {}; loc = {}
        for (b, ax), keys in chans.items():
            e = list(rot.get(b, (0.0, 0.0, 0.0))); e[ax] += track(keys, t); rot[b] = tuple(e)
        if "jaw" not in rot:
            rot["jaw"] = (JAW_CLOSED, 0, 0)
        off = V((0, 0, 0))
        for ax, keys in (ploc_keys or {}).items():
            off[ax] = track(keys, t)
        loc["pelvis"] = pelvis_loc(off)
        if root_keys:
            rr = [track(root_keys.get(k, [(0, 0)]), t) for k in ("roll", "drop")]
            rot["root"] = (0.0, rr[0], 0.0)
            loc["root"] = RROOT3.inverted() @ V((0, 0, -rr[1]))
        if extra:
            extra(t, rot, loc)
        if plant_until is None or t <= plant_until:
            plant_legs(clip, rot, loc, {"l": planted("l"), "r": planted("r")})
            last_leg = {k: v for k, v in rot.items() if k.split("_")[0] in ("thigh", "calf", "foot", "toe")}
        else:
            for k, v in last_leg.items():
                add = rot.get(k, (0.0, 0.0, 0.0)) if k in rot else (0.0, 0.0, 0.0)
                rot[k] = (v[0] + add[0], v[1] + add[1], v[2] + add[2])
        clip.key(f, rot, loc)
    clip.done()


def make_idle():
    T = 3.0
    w = lambda a, ph=0.0, cyc=1: [(i / 30.0 * T, a * math.sin(2 * math.pi * (cyc * i / 30.0 + ph))) for i in range(31)]
    planted_clip("Rex4_Idle", T, {
        ("spine_01", 0): w(0.015), ("spine_03", 0): w(-0.02, 0.1), ("neck_01", 0): w(0.03, 0.2),
        ("neck_01", 2): w(0.12, 0.0), ("neck_02", 2): w(0.08, 0.08), ("head", 2): w(0.10, 0.15), ("head", 0): w(0.04, 0.3, 2), ("head", 1): w(0.05, 0.4),
        ("jaw", 0): [(t, JAW_CLOSED + 0.03 + 0.03 * math.sin(2 * math.pi * t / T)) for t in [i * T / 30 for i in range(31)]],
        ("tail_02", 2): w(0.04, 0.1), ("tail_03", 2): w(0.05, 0.2), ("tail_04", 2): w(0.06, 0.3), ("tail_05", 2): w(0.07, 0.4),
        ("tail_02", 0): w(0.01, 0.2), ("upperarm_l", 0): w(0.05, 0.1), ("upperarm_r", 0): w(-0.05, 0.6),
        ("lowerarm_l", 0): [(0, -0.15), (T, -0.15)], ("lowerarm_r", 0): [(0, -0.15), (T, -0.15)],
    }, ploc_keys={2: [(i / 30.0 * T, -0.06 + 0.025 * math.sin(2 * math.pi * i / 30.0)) for i in range(31)]})


def make_roar():
    shake = [(1.05 + i * 0.08, 0.06 * (1 if i % 2 else -1) * (1 - i / 16)) for i in range(16)]
    planted_clip("Rex4_Roar", 3.2, {
        ("neck_01", 0): [(0, 0), (0.55, -0.22), (1.0, 0.08), (2.3, 0.06), (2.9, 0), (3.2, 0)],
        ("neck_02", 0): [(0, 0), (0.55, -0.18), (1.0, 0.02), (2.3, 0.0), (2.9, 0), (3.2, 0)],
        ("head", 0): [(0, 0), (0.55, -0.12), (1.0, -0.12), (2.3, -0.10), (2.9, 0), (3.2, 0)],
        ("head", 2): [(0, 0), (1.0, 0)] + shake + [(2.5, 0), (3.2, 0)],
        ("jaw", 0): [(0, JAW_CLOSED), (0.55, -0.12), (1.0, 0.50), (2.3, 0.46), (2.7, JAW_CLOSED), (3.2, JAW_CLOSED)],
        ("spine_03", 0): [(0, 0), (0.55, -0.08), (1.0, 0.08), (2.3, 0.06), (2.9, 0), (3.2, 0)],
        ("pelvis", 0): [(0, 0), (0.55, -0.05), (1.0, 0.06), (2.3, 0.05), (2.9, 0), (3.2, 0)],
        ("tail_01", 0): [(0, 0), (0.55, 0.06), (1.0, -0.08), (2.3, -0.06), (2.9, 0), (3.2, 0)],
        ("tail_03", 2): [(0, 0), (1.0, 0.08), (1.6, -0.08), (2.2, 0.06), (3.2, 0)],
        ("tail_05", 2): [(0, 0), (1.1, 0.12), (1.7, -0.12), (2.3, 0.08), (3.2, 0)],
        ("upperarm_l", 0): [(0, 0), (1.0, -0.35), (2.3, -0.3), (3.2, 0)], ("upperarm_r", 0): [(0, 0), (1.0, -0.35), (2.3, -0.3), (3.2, 0)],
        ("lowerarm_l", 0): [(0, -0.15), (1.0, -0.5), (2.3, -0.45), (3.2, -0.15)], ("lowerarm_r", 0): [(0, -0.15), (1.0, -0.5), (2.3, -0.45), (3.2, -0.15)],
    }, ploc_keys={0: [(0, 0), (0.55, -0.25), (1.0, 0.45), (2.3, 0.40), (2.9, 0), (3.2, 0)],
                  2: [(0, 0), (0.55, -0.12), (1.0, -0.20), (2.3, -0.18), (2.9, 0), (3.2, 0)]})


def make_bite():
    planted_clip("Rex4_Bite", 1.3, {
        ("neck_01", 0): [(0, 0), (0.35, -0.18), (0.62, 0.38), (0.80, 0.34), (1.3, 0)],
        ("neck_02", 0): [(0, 0), (0.35, -0.12), (0.62, 0.20), (0.80, 0.18), (1.3, 0)],
        ("head", 0): [(0, 0), (0.35, -0.10), (0.62, 0.08), (0.80, 0.05), (1.3, 0)],
        ("head", 2): [(0, 0), (0.70, 0), (0.76, 0.07), (0.84, -0.06), (0.92, 0.03), (1.0, 0), (1.3, 0)],
        ("jaw", 0): [(0, JAW_CLOSED), (0.35, 0.40), (0.60, 0.45), (0.68, JAW_CLOSED - 0.02), (1.3, JAW_CLOSED)],
        ("pelvis", 0): [(0, 0), (0.35, -0.04), (0.62, 0.10), (0.80, 0.08), (1.3, 0)],
        ("spine_03", 0): [(0, 0), (0.62, 0.08), (1.3, 0)],
        ("tail_01", 0): [(0, 0), (0.35, 0.04), (0.62, -0.10), (1.3, 0)],
        ("tail_04", 2): [(0, 0), (0.62, 0.08), (1.0, -0.05), (1.3, 0)],
    }, ploc_keys={0: [(0, 0), (0.35, -0.30), (0.62, 0.75), (0.85, 0.65), (1.3, 0)],
                  2: [(0, 0), (0.35, -0.05), (0.62, -0.30), (0.85, -0.25), (1.3, 0)]})


def make_hit():
    planted_clip("Rex4_Hit", 0.8, {
        ("neck_01", 0): [(0, 0), (0.12, -0.30), (0.35, -0.10), (0.8, 0)],
        ("neck_01", 2): [(0, 0), (0.12, 0.18), (0.35, 0.06), (0.8, 0)],
        ("head", 2): [(0, 0), (0.12, 0.15), (0.40, 0.02), (0.8, 0)],
        ("jaw", 0): [(0, JAW_CLOSED), (0.12, 0.15), (0.45, JAW_CLOSED), (0.8, JAW_CLOSED)],
        ("pelvis", 0): [(0, 0), (0.12, -0.06), (0.8, 0)],
        ("spine_01", 1): [(0, 0), (0.12, 0.06), (0.8, 0)],
        ("tail_02", 2): [(0, 0), (0.15, -0.10), (0.5, 0.04), (0.8, 0)],
        ("tail_04", 2): [(0, 0), (0.2, -0.15), (0.55, 0.06), (0.8, 0)],
    }, ploc_keys={0: [(0, 0), (0.12, -0.30), (0.8, 0)], 2: [(0, 0), (0.12, -0.10), (0.8, 0)]})


def make_death():
    planted_clip("Rex4_Death", 3.6, {
        ("neck_01", 0): [(0, 0), (0.45, -0.25), (1.2, 0.05), (2.4, 0.25), (3.6, 0.30)],
        ("neck_02", 0): [(0, 0), (0.45, -0.15), (2.4, 0.20), (3.6, 0.22)],
        ("neck_01", 2): [(0, 0), (1.2, 0.10), (2.8, -0.35), (3.6, -0.40)],
        ("head", 0): [(0, 0), (0.45, -0.20), (2.4, 0.10), (3.6, 0.15)],
        ("jaw", 0): [(0, JAW_CLOSED), (0.45, 0.40), (1.2, 0.10), (2.6, -0.05), (3.6, -0.10)],
        ("spine_01", 1): [(0, 0), (1.2, 0.08), (3.6, 0.05)],
        ("tail_02", 2): [(0, 0), (1.2, -0.06), (2.6, 0.15), (3.6, 0.18)],
        ("tail_04", 2): [(0, 0), (1.4, -0.08), (2.8, 0.22), (3.6, 0.25)],
        ("tail_01", 0): [(0, 0), (1.6, 0.05), (2.8, -0.15), (3.6, -0.15)],
        ("upperarm_l", 0): [(0, 0), (0.45, -0.3), (3.6, 0.2)], ("upperarm_r", 0): [(0, 0), (0.45, -0.3), (3.6, 0.3)],
        ("lowerarm_l", 0): [(0, -0.15), (3.6, -0.6)], ("lowerarm_r", 0): [(0, -0.15), (3.6, -0.7)],
        ("thigh_l", 0): [(0, 0), (2.0, 0), (3.0, -0.30), (3.6, -0.35)], ("calf_l", 0): [(0, 0), (2.0, 0), (3.0, 0.30), (3.6, 0.35)],
        ("thigh_r", 0): [(0, 0), (2.0, 0), (3.0, -0.12), (3.6, -0.15)], ("calf_r", 0): [(0, 0), (2.0, 0), (3.0, 0.15), (3.6, 0.20)],
    }, ploc_keys={0: [(0, 0), (0.45, -0.20), (1.2, 0.15), (2.0, 0.2)],
                  2: [(0, 0), (0.45, -0.10), (1.2, -0.45), (1.9, -1.10), (2.0, -1.15)]},
        root_keys={"roll": [(0, 0), (1.8, 0), (2.9, 1.42), (3.2, 1.38), (3.6, 1.40)],
                   "drop": [(0, 0), (3.6, 0)]},
        plant_until=1.9)


def neck(chans, axis, keys, split=(0.40, 0.35, 0.25)):
    """Spread a head turn (axis 0 pitch +down, 2 yaw +right) over neck_01/neck_02/head."""
    for b, w in zip(("neck_01", "neck_02", "head"), split):
        k = (b, axis)
        new = [(t, v * w) for t, v in keys]
        if k in chans:
            old = chans[k]
            ts = sorted(set([t for t, _ in old] + [t for t, _ in new]))
            chans[k] = [(t, track(old, t) + track(new, t)) for t in ts]
        else:
            chans[k] = new


def osc(t0, t1, amp, hz, decay=True, phase=0.0):
    n = int((t1 - t0) * hz * 4) + 1
    out = []
    for i in range(n + 1):
        t = t0 + (t1 - t0) * i / n
        a = amp * ((1 - (t - t0) / (t1 - t0)) if decay else 1.0)
        out.append((t, a * math.sin(2 * math.pi * hz * (t - t0) + phase)))
    return out


def make_idle_look():
    c = {}
    neck(c, 2, [(0, 0), (0.6, 0), (1.4, -0.55), (2.1, -0.55), (2.9, 0.50), (3.6, 0.50), (4.4, 0), (4.8, 0)])
    neck(c, 0, [(0, 0), (1.4, -0.08), (1.6, 0.06), (1.75, -0.04), (1.9, 0.05), (2.1, -0.06), (2.9, -0.10), (3.6, -0.05), (4.8, 0)])
    c[("jaw", 0)] = [(0, JAW_CLOSED), (1.6, JAW_CLOSED + 0.06), (1.8, JAW_CLOSED), (3.2, JAW_CLOSED + 0.05), (4.8, JAW_CLOSED)]
    c[("head", 1)] = [(0, 0), (1.4, 0.08), (2.1, 0.10), (2.9, -0.08), (3.6, -0.10), (4.8, 0)]
    c[("spine_03", 2)] = [(0, 0), (1.4, -0.06), (2.9, 0.06), (4.8, 0)]
    c[("tail_03", 2)] = [(0, 0), (1.6, 0.06), (3.1, -0.06), (4.8, 0)]
    c[("tail_05", 2)] = [(0, 0), (1.8, 0.10), (3.3, -0.10), (4.8, 0)]
    planted_clip("Rex4_IdleLook", 4.8, c, ploc_keys={2: [(0, -0.05), (2.4, -0.08), (4.8, -0.05)]})


def make_idle_shake():
    c = {}
    neck(c, 0, [(0, 0), (0.4, -0.15), (0.6, 0.05), (2.2, 0.02), (2.6, 0)])
    neck(c, 2, [(0, 0), (0.6, 0)] + osc(0.6, 2.1, 0.30, 4.0) + [(2.6, 0)], split=(0.25, 0.35, 0.40))
    c[("head", 1)] = [(0, 0), (0.6, 0)] + osc(0.6, 2.1, 0.18, 4.0, phase=0.8) + [(2.6, 0)]
    c[("jaw", 0)] = [(0, JAW_CLOSED), (0.5, 0.05), (0.7, JAW_CLOSED), (1.4, -0.05), (2.6, JAW_CLOSED)]
    c[("spine_03", 2)] = [(0, 0), (0.6, 0)] + osc(0.6, 2.1, 0.04, 4.0, phase=2.5) + [(2.6, 0)]
    c[("tail_04", 2)] = [(0, 0), (0.8, 0)] + osc(0.8, 2.4, 0.08, 2.0) + [(2.6, 0)]
    planted_clip("Rex4_IdleShake", 2.6, c)


def make_alert():
    c = {}
    neck(c, 0, [(0, 0), (0.25, -0.40), (0.9, -0.32), (1.6, -0.30), (2.2, 0)])
    neck(c, 2, [(0, 0), (0.25, 0), (0.45, 0.35), (0.75, 0.35), (0.95, -0.40), (1.3, -0.40), (1.55, 0.05), (2.2, 0)])
    c[("head", 0)] = [(0, 0), (0.25, -0.10), (0.5, 0.05), (0.6, -0.06), (0.7, 0.05), (2.2, 0)]
    c[("jaw", 0)] = [(0, JAW_CLOSED), (0.25, 0.05), (0.5, JAW_CLOSED + 0.06), (1.4, 0.10), (1.7, JAW_CLOSED), (2.2, JAW_CLOSED)]
    c[("spine_03", 0)] = [(0, 0), (0.25, -0.08), (1.6, -0.06), (2.2, 0)]
    c[("tail_02", 0)] = [(0, 0), (0.25, 0.05), (2.2, 0)]
    c[("tail_04", 2)] = [(0, 0), (0.5, -0.10), (1.0, 0.12), (1.5, -0.06), (2.2, 0)]
    planted_clip("Rex4_Alert", 2.2, c, ploc_keys={0: [(0, 0), (0.25, -0.15), (1.6, -0.10), (2.2, 0)], 2: [(0, 0), (0.25, 0.04), (2.2, 0)]})


def make_taunt():
    c = {}
    neck(c, 0, [(0, 0), (0.5, 0.45), (0.9, 0.40), (1.2, -0.45), (1.9, -0.40), (2.4, 0.10), (2.8, 0)])
    neck(c, 2, [(0, 0), (0.5, 0.10), (0.9, -0.10), (1.2, 0)] + osc(1.25, 2.0, 0.18, 3.0) + [(2.8, 0)])
    c[("jaw", 0)] = [(0, JAW_CLOSED), (0.5, JAW_CLOSED), (0.6, 0.15), (0.7, JAW_CLOSED), (0.8, 0.15), (0.9, JAW_CLOSED),
                     (1.2, 0.48), (1.9, 0.44), (2.3, JAW_CLOSED), (2.8, JAW_CLOSED)]
    c[("spine_03", 0)] = [(0, 0), (0.5, 0.10), (1.2, -0.08), (1.9, -0.06), (2.8, 0)]
    c[("pelvis", 0)] = [(0, 0), (0.5, 0.05), (1.2, -0.04), (2.8, 0)]
    c[("tail_02", 0)] = [(0, 0), (0.5, -0.06), (1.2, 0.06), (2.8, 0)]
    c[("tail_05", 2)] = [(0, 0), (1.2, 0)] + osc(1.2, 2.4, 0.15, 1.5) + [(2.8, 0)]
    planted_clip("Rex4_Taunt", 2.8, c, ploc_keys={2: [(0, 0), (0.5, -0.20), (1.2, 0.0), (2.8, 0)]})


def make_head_swing():
    c = {}
    neck(c, 2, [(0, 0), (0.35, -0.55), (0.70, 0.50), (0.85, 0.45), (1.4, 0)])
    neck(c, 0, [(0, 0), (0.35, -0.12), (0.62, 0.22), (0.85, 0.18), (1.4, 0)])
    c[("head", 1)] = [(0, 0), (0.35, -0.15), (0.70, 0.20), (1.4, 0)]
    c[("jaw", 0)] = [(0, JAW_CLOSED), (0.35, 0.40), (0.62, 0.45), (0.72, JAW_CLOSED - 0.02), (1.4, JAW_CLOSED)]
    c[("spine_03", 2)] = [(0, 0), (0.35, -0.12), (0.70, 0.14), (1.4, 0)]
    c[("spine_01", 2)] = [(0, 0), (0.35, -0.05), (0.70, 0.06), (1.4, 0)]
    c[("tail_03", 2)] = [(0, 0), (0.40, 0.12), (0.75, -0.15), (1.4, 0)]
    c[("tail_05", 2)] = [(0, 0), (0.45, 0.18), (0.80, -0.22), (1.4, 0)]
    planted_clip("Rex4_HeadSwing", 1.4, c, ploc_keys={0: [(0, 0), (0.35, -0.20), (0.70, 0.50), (1.4, 0)], 2: [(0, 0), (0.70, -0.20), (1.4, 0)]})


def make_hit_head():
    c = {}
    neck(c, 2, [(0, 0), (0.10, 0.50), (0.30, 0.30), (0.55, -0.08), (0.9, 0)], split=(0.30, 0.35, 0.35))
    neck(c, 0, [(0, 0), (0.10, -0.25), (0.35, -0.05), (0.9, 0)])
    c[("head", 1)] = [(0, 0), (0.10, 0.25), (0.4, 0.05), (0.9, 0)]
    c[("jaw", 0)] = [(0, JAW_CLOSED), (0.10, 0.25), (0.45, JAW_CLOSED), (0.9, JAW_CLOSED)]
    c[("spine_03", 2)] = [(0, 0), (0.12, 0.10), (0.9, 0)]
    c[("tail_04", 2)] = [(0, 0), (0.2, -0.15), (0.55, 0.06), (0.9, 0)]
    planted_clip("Rex4_HitHead", 0.9, c, ploc_keys={0: [(0, 0), (0.12, -0.15), (0.9, 0)]})


ALL = {"IdleLook": make_idle_look, "IdleShake": make_idle_shake, "Alert": make_alert, "Taunt": make_taunt, "HeadSwing": make_head_swing, "HitHead": make_hit_head, "Idle": make_idle, "Walk": make_walk, "Run": make_run, "Roar": make_roar, "Bite": make_bite, "Hit": make_hit, "Death": make_death}
want = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else list(ALL)
for k in want:
    GUESS["l"] = [0.0, 0.0, 0.0]; GUESS["r"] = [0.0, 0.0, 0.0]
    ALL[k]()
arm.animation_data.action = bpy.data.actions.get("Rex4_Idle") or arm.animation_data.action
bpy.context.scene.render.fps = FPS
bpy.ops.wm.save_as_mainfile(filepath=BLEND)
print("[ANIM] saved", [a.name for a in bpy.data.actions])
