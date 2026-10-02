"""Import the generated UI frame PNGs and bind them to the Temporal Log panels.

Run inside the Unreal editor's Python console:

    exec(open("C:/repos/Unreal Projects/Timeshift3D/Tools/import_ui_frames.py").read())

Regenerate the PNGs first with Tools/gen_ui_frames.py. Importing is idempotent -
re-running replaces the existing textures and re-applies the brushes, so this is
the way to iterate on the frame art.

SLICES maps each texture to (pixel size, slice margin in px). The margin must
match the one gen_ui_frames.py authored, or the corners stretch.
"""

import unreal

SRC = "C:/repos/Unreal Projects/Timeshift3D/SourceArt/UI/"
DST = "/Game/Timeshift/UI/Frames"

SLICES = {
    "T_UI_FrameOuter": (72, 28),
    "T_UI_PanelDark": (40, 16),
    "T_UI_PanelAnalyzer": (40, 16),
    "T_UI_PanelParchment": (40, 16),
    "T_UI_MetaBar": (24, 10),
    "T_UI_RowIdle": (24, 10),
    "T_UI_RowSelected": (24, 10),
    "T_UI_TabActive": (40, 16),
    "T_UI_TabIdle": (40, 16),
    "T_UI_Rail": (32, 12),
}

# Border widget -> texture. Buttons are skinned via WidgetStyle, not here.
PANELS = {
    "Backdrop": "T_UI_FrameOuter",
    "LeftPanel": "T_UI_PanelDark",
    "AnalyzerBox": "T_UI_PanelAnalyzer",
    "RecordBox": "T_UI_PanelParchment",
    "MetaBar": "T_UI_MetaBar",
    "FooterBar": "T_UI_MetaBar",
    "IndexContextBox": "T_UI_MetaBar",
    "EraMarkerBox": "T_UI_RowSelected",
    "TimelineRail": "T_UI_Rail",
}


def import_textures():
    tasks = []
    for name in SLICES:
        t = unreal.AssetImportTask()
        t.filename = SRC + name + ".png"
        t.destination_path = DST
        t.destination_name = name
        t.automated = True
        t.replace_existing = True
        t.save = True
        tasks.append(t)
    unreal.AssetToolsHelpers.get_asset_tools().import_asset_tasks(tasks)

    for name in SLICES:
        tex = unreal.load_asset("%s/%s" % (DST, name))
        if not tex:
            unreal.log_warning("missing after import: %s" % name)
            continue
        tex.set_editor_property("lod_group", unreal.TextureGroup.TEXTUREGROUP_UI)
        tex.set_editor_property("mip_gen_settings",
                                unreal.TextureMipGenSettings.TMGS_NO_MIPMAPS)
        tex.set_editor_property("compression_settings",
                                unreal.TextureCompressionSettings.TC_EDITOR_ICON)
        tex.set_editor_property("srgb", True)
        tex.set_editor_property("never_stream", True)
        unreal.EditorAssetLibrary.save_loaded_asset(tex)
        print("imported %s" % name)


def make_brush(name):
    size, margin = SLICES[name]
    m = float(margin) / float(size)
    b = unreal.SlateBrush()
    b.set_editor_property("resource_object", unreal.load_asset("%s/%s" % (DST, name)))
    b.set_editor_property("image_size", unreal.Vector2D(size, size))
    b.set_editor_property("draw_as", unreal.SlateBrushDrawType.BOX)
    b.set_editor_property("margin", unreal.Margin(m, m, m, m))
    b.set_editor_property("tint_color", unreal.SlateColor(unreal.LinearColor(1, 1, 1, 1)))
    return b


def apply_panels():
    wbp = unreal.load_asset("/Game/Timeshift/UI/WBP_Encyclopedia")
    if not wbp:
        unreal.log_warning("WBP_Encyclopedia not found")
        return
    tree = wbp.get_editor_property("widget_tree")
    for widget_name, tex in PANELS.items():
        w = tree.find_widget(widget_name) if hasattr(tree, "find_widget") else None
        if not w:
            unreal.log_warning("widget not found (apply by hand): %s" % widget_name)
            continue
        w.set_editor_property("background", make_brush(tex))
        print("skinned %s -> %s" % (widget_name, tex))
    unreal.EditorAssetLibrary.save_loaded_asset(wbp)


if __name__ == "__main__" or True:
    import_textures()
    apply_panels()
    print("done - recompile WBP_Encyclopedia if the designer looks stale")
