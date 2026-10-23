(fn GetLevel ()
  ; another instance's variable cannot be read from inside this blueprint's own graphs - a function call can target it
  (return (Variables|Default|GetDifficulty)))
