(fn AddMorphCharge ()
  (Variables|Default|SetMorphCharges (+ (Variables|Default|GetMorphCharges) 1))
  (Development|PrintString :InString "Morph Amber - press M to transform into a dinosaur" :bPrintToScreen true :bPrintToLog true :TextColor "(R=1.000000,G=0.650000,B=0.100000,A=1.000000)" :Duration 4.0))
