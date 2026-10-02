"""Create the BP_ChronoshiftSave SaveGame blueprint.

The MCP toolset can edit blueprints but cannot create them, so this one asset
has to be made from the editor's Python console:

    exec(open("C:/repos/Unreal Projects/Timeshift3D/Tools/make_savegame.py").read())

Safe to re-run: it does nothing if the asset already exists. The DiscoveredIds
variable and all graph wiring are applied separately over MCP.
"""

import unreal

PKG_PATH = "/Game/Timeshift/Save"
ASSET_NAME = "BP_ChronoshiftSave"
FULL = "%s/%s" % (PKG_PATH, ASSET_NAME)


def main():
    if unreal.EditorAssetLibrary.does_asset_exist(FULL):
        print("already exists: %s" % FULL)
        return

    factory = unreal.BlueprintFactory()
    factory.set_editor_property("parent_class", unreal.SaveGame)

    tools = unreal.AssetToolsHelpers.get_asset_tools()
    bp = tools.create_asset(
        asset_name=ASSET_NAME,
        package_path=PKG_PATH,
        asset_class=unreal.Blueprint,
        factory=factory,
    )
    if not bp:
        print("FAILED to create %s" % FULL)
        return

    unreal.EditorAssetLibrary.save_loaded_asset(bp)
    print("created %s (parent: SaveGame)" % FULL)


main()
