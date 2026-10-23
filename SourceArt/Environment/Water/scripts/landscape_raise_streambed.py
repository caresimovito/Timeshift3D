"""Raise the old stream bed behind the swamp's boulder bank (user 2026-10-21: "water looks way too angular").

The swamp water was cut off along x = 23800 where the user removed the old stream channel, but the channel bed there is
4-71 cm BELOW the water level, so the water ends as a straight floating slab edge visible between the bank boulders. Raise
the ground in that strip to WATER + RAISE_CM, blending back to the original terrain over BLEND_CM, so the cut edge sinks
under the terrain like every other shore. Only raises (never lowers); everything outside the strip is untouched.

Reuses landscape_despike.py's export / calibrate / paint / import / verify machinery (byte-exact write-back, verifies that
untouched vertices did not move). Run in the editor (not PIE):  exec(open(r'C:/agentpy/landscape_raise_streambed.py').read())
Globals: DRY=True only reports.
"""
_src = open(r"C:/agentpy/landscape_despike.py").read()
_src = _src[:_src.rindex("_start()")]          # load the helpers without starting the despike pass
_src = _src.replace("canvas.k2_draw_texture(", "canvas.draw_texture(")   # Python drops the K2_ prefix
exec(_src)

REPORT = OUT_DIR + "/raise_streambed_report.json"
WATER_Z = -5.0                 # Swamp_Pond_Water surface
RAISE_CM = 15.0
CORE = (23300.0, 23850.0, -1000.0, 3100.0)   # x0, x1, y0, y1 of the strip behind the bank
BLEND_CM = 300.0
DRY_RUN = globals().get("DRY", False)


def _raise(heights, width, height, min_x, min_y, scale, report):
    cm_per_unit = scale.z / UNITS_PER_128
    target = int(round(UINT16_MID + (WATER_Z + RAISE_CM) / cm_per_unit))
    x0, x1, y0, y1 = CORE
    ix0 = max(0, int((x0 - BLEND_CM - min_x) / scale.x) - 1)
    ix1 = min(width - 1, int((x1 + BLEND_CM - min_x) / scale.x) + 1)
    iy0 = max(0, int((y0 - BLEND_CM - min_y) / scale.y) - 1)
    iy1 = min(height - 1, int((y1 + BLEND_CM - min_y) / scale.y) + 1)
    edits = {}
    raised = []
    for iy in range(iy0, iy1 + 1):
        wy = min_y + iy * scale.y
        for ix in range(ix0, ix1 + 1):
            wx = min_x + ix * scale.x
            dx = max(x0 - wx, 0.0, wx - x1)
            dy = max(y0 - wy, 0.0, wy - y1)
            dist = (dx * dx + dy * dy) ** 0.5
            if dist >= BLEND_CM:
                continue
            t = 1.0 - dist / BLEND_CM
            w = t * t * (3 - 2 * t)
            i = iy * width + ix
            h = heights[i]
            if h >= target:
                continue
            nh = int(round(h + w * (target - h)))
            if nh > h:
                edits[i] = nh
                raised.append((nh - h) * cm_per_unit)
    report["target_units"] = target
    report["edit_count"] = len(edits)
    if raised:
        raised.sort()
        report["raise_cm"] = {"min": raised[0], "median": raised[len(raised) // 2], "max": raised[-1]}
    return edits


def main(heights, rt, world, parent, layers, width, height, scale, report, cfg):
    started = time.time()
    min_x, min_y, _mx, _my, _s = _extent([p for p in _actors() if isinstance(p, unreal.LandscapeProxy)])
    original = array.array("H", heights)
    edits = _raise(heights, width, height, min_x, min_y, scale, report)
    report["applied"] = False
    if not edits:
        report["note"] = "nothing below the target in the strip"
    elif DRY_RUN:
        report["note"] = "dry run"
    elif len(layers) > 1:
        report["note"] = "landscape has %d edit layers; not writing" % len(layers)
    else:
        inverse = _calibrate(world, report)
        _paint(world, rt, edits, width, inverse, report)
        check_hi, check_lo = _read_bytes(world, rt)
        mismatch = sum(1 for i, v in edits.items() if ((check_hi[i] << 8) | check_lo[i]) != v)
        report["rt_mismatch_before_import"] = mismatch
        if mismatch:
            report["note"] = "render target write-back was not byte exact; nothing imported"
        else:
            report["import_ok"] = bool(parent.landscape_import_heightmap_from_render_target(rt, True, 0))
            verify_rt = _make_rt(world, width, height)
            parent.landscape_export_heightmap_to_render_target(verify_rt, True, True)
            v_hi, v_lo = _read_bytes(world, verify_rt)
            report["verify_edits_wrong"] = sum(1 for i, v in edits.items() if ((v_hi[i] << 8) | v_lo[i]) != v)
            report["verify_untouched_changed"] = sum(1 for i in range(len(original))
                                                     if i not in edits and ((v_hi[i] << 8) | v_lo[i]) != original[i])
            report["applied"] = True
            try:
                unreal.EditorLoadingAndSavingUtils.save_dirty_packages(True, True)
                report["saved"] = True
            except Exception as exc:
                report["saved"] = "ERR " + repr(exc)[:200]
    report["seconds"] = time.time() - started
    os.makedirs(OUT_DIR, exist_ok=True)
    with open(REPORT, "w", encoding="utf-8") as handle:
        json.dump(report, handle, indent=1, default=str)
    unreal.log_warning("[RSB] done: %s" % json.dumps({k: report.get(k) for k in ("edit_count", "raise_cm", "applied", "verify_edits_wrong",
                                                                                 "verify_untouched_changed", "note", "saved")}, default=str))


_start()
