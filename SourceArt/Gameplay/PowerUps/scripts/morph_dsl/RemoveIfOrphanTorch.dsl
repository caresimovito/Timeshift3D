(fn RemoveIfOrphanTorch (Comp)
  (if (and (Utilities|String|EqualExactly(String) (Utilities|GetDisplayName (Class|StaticMeshComponent|GetStaticMesh Comp)) "SM_Torch") (!= Comp (Variables|Default|GetTorchMeshComponent)))
    (bind kids (Components|GetChildrenComponents Comp true))
    (for k kids
      (Components|DestroyComponent k))
    (Components|DestroyComponent Comp)))
