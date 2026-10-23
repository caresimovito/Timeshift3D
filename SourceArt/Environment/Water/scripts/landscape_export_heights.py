"""Export the landscape heightmap (read-only) to C:/agentpy/heights.bin (uint16, row-major) + heights_meta.json
(grid size, world min x / y, scale, cm per unit) - the input for the smooth swamp water mesh. Reuses landscape_despike.py's
export (with its retry-until-not-black loop); no landscape data is written."""
_src = open(r"C:/agentpy/landscape_despike.py").read()
_src = _src[:_src.rindex("_start()")]
exec(_src)


def main(heights, rt, world, parent, layers, width, height, scale, report, cfg):
    min_x, min_y, _mx, _my, _s = _extent([p for p in _actors() if isinstance(p, unreal.LandscapeProxy)])
    with open(OUT_DIR + "/heights.bin", "wb") as handle:
        handle.write(heights.tobytes())
    meta = {"width": width, "height": height, "min_x": min_x, "min_y": min_y, "scale": [scale.x, scale.y, scale.z],
            "cm_per_unit": scale.z / UNITS_PER_128, "mid": UINT16_MID}
    with open(OUT_DIR + "/heights_meta.json", "w") as handle:
        json.dump(meta, handle)
    unreal.log_warning("[LEH] done %s" % json.dumps(meta))


_start()
