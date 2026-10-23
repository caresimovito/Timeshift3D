(fn SetPush (Attacker Target Mode)
  ; PushDir = which way a hit shoves: 0 straight away from the attacker, 1 out to the side the target is on, 2 along its facing
  (bind a (Transformation|GetActorLocation Attacker))
  (bind t (Transformation|GetActorLocation Target))
  (bind d (Math|Vector|MakeVector (- (.x t) (.x a)) (- (.y t) (.y a)) 0.0))
  (if (== Mode 1)
    (bind r (Transformation|GetActorRightVector Attacker))
    (bind sg (select (>= (Math|Vector|DotProduct r d) 0.0) 1.0 -1.0))
    (Variables|Default|SetPushDir (Math|Vector|MakeVector (* (.x r) sg) (* (.y r) sg) 0.0))
    (elif (== Mode 2)
      (Variables|Default|SetPushDir (Transformation|GetActorForwardVector Attacker))
      (else
        (Variables|Default|SetPushDir (Math|Vector|Normalize d))))))
