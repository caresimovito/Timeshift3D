(fn ShouldFlee ()
  ; timid species run from the player UNTIL he hits them (bHasBeenProvoked, set when they lose health) - then they turn and
  ; fight (user, 2026-10-21: "make them fight back when hit"). Other passive animals still flee once badly hurt (<35 %).
  (bind sp (Variables|Default|GetSpecies))
  (bind timid (or (or (or (or (Utilities|String|EqualExactly(String) sp "Kulindadromeus") (Utilities|String|EqualExactly(String) sp "Psittacosaurus")) (Utilities|String|EqualExactly(String) sp "Caudipteryx")) (Utilities|String|EqualExactly(String) sp "Archaeoceratops")) (Utilities|String|EqualExactly(String) sp "Parasaurolophus")))
  (bind hc (Variables|Default|GetHealthComponent))
  (return (select timid
    (not (Variables|Default|GetHasBeenProvoked))
    (and (Variables|Default|GetIsPassive) (< (Class|BPHealthComponent|GetCurrentHealth hc) (* 0.35 (Class|BPHealthComponent|GetMaxHealth hc)))))))
