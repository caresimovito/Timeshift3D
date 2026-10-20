(fn ApplyDamage (DamageAmount)
  ; armour absorbs first, the rest comes off health. Both results are worked out ONCE into member vars before anything
  ; is changed: the old version used pure expressions that re-evaluated after SetArmour, so a hit that broke the armour
  ; saw armour 0, absorbed nothing and took the FULL hit off health (2026-10-20, found while building the morph).
  (if (and (not (Variables|Default|GetIsDead)) (not (Variables|Default|GetIsInvulnerable)))
    (Variables|Default|SetPendingAbsorb (Math|Float|Min(Float) (Variables|Default|GetArmour) DamageAmount))
    (Variables|Default|SetPendingHealth (Math|Float|Clamp(Float) (- (Variables|Default|GetCurrentHealth) (- DamageAmount (Variables|Default|GetPendingAbsorb))) 0.0 (Variables|Default|GetMaxHealth)))
    (Development|PrintString :InString (Utilities|String|Append (Utilities|String|Append (Utilities|String|Append (Utilities|GetDisplayName (Components|GetOwner self)) " DMG ") (Utilities|String|ToString(Float) DamageAmount)) (Utilities|String|Append "  left=" (Utilities|String|ToString(Float) (Variables|Default|GetPendingHealth)))) :bPrintToScreen false :bPrintToLog true :TextColor "(R=1.000000,G=0.900000,B=0.000000,A=1.000000)" :Duration 6.0)
    (Variables|Default|SetArmour (- (Variables|Default|GetArmour) (Variables|Default|GetPendingAbsorb)))
    (Variables|Default|SetCurrentHealth (Variables|Default|GetPendingHealth))
    (Default|CallOnHealthChanged self (Variables|Default|GetPendingHealth) (Variables|Default|GetMaxHealth))
    (if (<= (Variables|Default|GetPendingHealth) 0.0)
      (CallFunction|MarkDeath self))))
