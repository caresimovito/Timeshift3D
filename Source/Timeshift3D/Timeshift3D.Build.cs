// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class Timeshift3D : ModuleRules
{
	public Timeshift3D(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"AIModule",
			"StateTreeModule",
			"GameplayStateTreeModule",
			"UMG",
			"Slate"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });

		PublicIncludePaths.AddRange(new string[] {
			"Timeshift3D",
			"Timeshift3D/Variant_Platforming",
			"Timeshift3D/Variant_Platforming/Animation",
			"Timeshift3D/Variant_Combat",
			"Timeshift3D/Variant_Combat/AI",
			"Timeshift3D/Variant_Combat/Animation",
			"Timeshift3D/Variant_Combat/Gameplay",
			"Timeshift3D/Variant_Combat/Interfaces",
			"Timeshift3D/Variant_Combat/UI",
			"Timeshift3D/Variant_SideScrolling",
			"Timeshift3D/Variant_SideScrolling/AI",
			"Timeshift3D/Variant_SideScrolling/Gameplay",
			"Timeshift3D/Variant_SideScrolling/Interfaces",
			"Timeshift3D/Variant_SideScrolling/UI"
		});

		// Uncomment if you are using Slate UI
		// PrivateDependencyModuleNames.AddRange(new string[] { "Slate", "SlateCore" });

		// Uncomment if you are using online features
		// PrivateDependencyModuleNames.Add("OnlineSubsystem");

		// To include OnlineSubsystemSteam, add it to the plugins section in your uproject file with the Enabled attribute set to true
	}
}
