(fn HideIfTorch (Comp Hide)
  (if (Utilities|String|EqualExactly(String) (Utilities|GetDisplayName (Class|StaticMeshComponent|GetStaticMesh Comp)) "SM_Torch")
    (Development|SetHiddeninGame :self Comp :NewHidden Hide :bPropagateToChildren true)))
