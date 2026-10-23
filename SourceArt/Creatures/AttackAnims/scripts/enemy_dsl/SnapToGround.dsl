(fn SnapToGround ()
  ; Keeps a ground enemy on the ground (rewritten 2026-10-21, user: "some are ending up on top of a tree").
  ; The old version stepped up onto ANY surface up to 150 cm a tick (so it climbed tree hulls), and when its trace
  ; started inside a trunk it rose 60 cm a tick until it found the canopy. Now:
  ;  - surface under the feet (traced from +90 cm): taken if it is the landscape, or a prop no more than 60 cm up
  ;    (rocks, logs, ledges the creature already stands on);
  ;  - otherwise (inside a mesh / no hit / a tall step): drop to the LANDSCAPE below, skipping up to two props / canopies.
  (bind loc (Transformation|GetActorLocation self))
  (bind (hs oks) (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (.x loc) (.y loc) (+ (.z loc) 90.0)) :End (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z loc) 4000.0))))
  (bind (sb sio st sd sl sip sn sin spm sha shc) (Collision|BreakHitResult hs))
  (if (and (and oks (not sio)) (or (Utilities|String|Contains (Utilities|GetDisplayName shc) "Landscape") (< (- (.z sip) (.z loc)) 60.0)))
    (Transformation|SetActorLocation self (Math|Vector|MakeVector (.x loc) (.y loc) (.z sip)) false false)
    (else
      (bind (h1 ok1) (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (.x loc) (.y loc) (+ (.z loc) 3000.0)) :End (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z loc) 4000.0))))
      (bind (b1 io1 t1 d1 l1 ip1 n1 in1 pm1 ha1 hc1) (Collision|BreakHitResult h1))
      (if (and ok1 (Utilities|String|Contains (Utilities|GetDisplayName hc1) "Landscape"))
        (Transformation|SetActorLocation self (Math|Vector|MakeVector (.x loc) (.y loc) (.z ip1)) false false)
        (elif ok1
          (bind (h2 ok2) (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z ip1) 5.0)) :End (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z loc) 4000.0))))
          (bind (b2 io2 t2 d2 l2 ip2 n2 in2 pm2 ha2 hc2) (Collision|BreakHitResult h2))
          (if (and ok2 (Utilities|String|Contains (Utilities|GetDisplayName hc2) "Landscape"))
            (Transformation|SetActorLocation self (Math|Vector|MakeVector (.x loc) (.y loc) (.z ip2)) false false)
            (elif ok2
              (bind (h3 ok3) (Collision|LineTraceByChannel :Start (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z ip2) 5.0)) :End (Math|Vector|MakeVector (.x loc) (.y loc) (- (.z loc) 4000.0))))
              (bind (b3 io3 t3 d3 l3 ip3 n3 in3 pm3 ha3 hc3) (Collision|BreakHitResult h3))
              (if (and ok3 (Utilities|String|Contains (Utilities|GetDisplayName hc3) "Landscape"))
                (Transformation|SetActorLocation self (Math|Vector|MakeVector (.x loc) (.y loc) (.z ip3)) false false))))))))
  ; kept from the old version: while flinching, flash and slide a little away from the player
  (bind pl (Game|GetPlayerCharacter 0))
  (Utilities|IsValid pl
    (:"Is Valid"
      (bind me (Transformation|GetActorLocation self))
      (bind pp (Transformation|GetActorLocation pl))
      (bind ax (- (.x me) (.x pp)))
      (bind ay (- (.y me) (.y pp)))
      (bind away (Math|Vector|VectorLengthXY (Math|Vector|MakeVector ax ay 0.0)))
      (if (and (== (Variables|Default|GetAnimState) 4) (> (Variables|Default|GetAttackEndTime) (Utilities|Time|GetGameTimeinSeconds)))
        (Rendering|Material|SetOverlayMaterial :self (Variables|Default|GetBody) :NewOverlayMaterial "/Game/Timeshift/Materials/M_HitFlash.M_HitFlash")
        (if (> away 1.0)
          (Transformation|SetActorLocation self (Math|Vector|MakeVector (+ (.x me) (* ax (/ (* 150.0 (Utilities|Time|GetWorldDeltaSeconds)) away))) (+ (.y me) (* ay (/ (* 150.0 (Utilities|Time|GetWorldDeltaSeconds)) away))) (.z me)) false false))
        (else
          (Rendering|Material|SetOverlayMaterial :self (Variables|Default|GetBody)))))))
