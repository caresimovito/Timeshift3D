(fn StepSnareFall (Dt)
  (bind t (Variables|Default|GetSnared))
  (Utilities|IsValid t
    (:"Is Valid"
      (Variables|Default|SetSnareFallV (+ (Variables|Default|GetSnareFallV) (* 1800.0 (Math|Float|Min(Float) Dt 0.25))))
      (Variables|Default|SetFallZ (Math|Float|Max(Float) (- (.z (Transformation|GetActorLocation t)) (* (Variables|Default|GetSnareFallV) (Math|Float|Min(Float) Dt 0.25))) (Variables|Default|GetSnareGround)))
      (bind tl (Transformation|GetActorLocation t))
      (Transformation|SetActorLocation t (Math|Vector|MakeVector (.x tl) (.y tl) (Variables|Default|GetFallZ)) false false)
      (if (<= (Variables|Default|GetFallZ) (Variables|Default|GetSnareGround))
        (Variables|Default|SetSnareFalling false)))
    (:"Is Not Valid"
      (Variables|Default|SetSnareFalling false))))
