(fn RegenFXOff ()
  ; undo RegenFXOn: remove the coils and the motes
  (for c (Variables|Default|GetRegenCoils)
    (Components|DestroyComponent :self c))
  (Utilities|Array|Clear :TargetArray (Variables|Default|GetRegenCoils))
  (Utilities|IsValid (Variables|Default|GetRegenFX)
    (:"Is Valid"
      (Components|DestroyComponent :self (Variables|Default|GetRegenFX)))))
