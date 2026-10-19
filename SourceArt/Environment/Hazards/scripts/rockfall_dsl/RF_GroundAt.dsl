(fn GroundAt (X Y)
  ; landscape height under (X,Y) from the grid sampled in the editor (rockfall_grid.py) - the cycad canopies over the
  ; path have solid convex collision, so runtime traces can't be trusted here
  (bind i (Math|Integer|Clamp(Integer) (Math|Float|Round (/ (- X (Variables|Default|GetGX0)) (Variables|Default|GetGStep))) 0 (- (Variables|Default|GetGNX) 1)))
  (bind j (Math|Integer|Clamp(Integer) (Math|Float|Round (/ (- Y (Variables|Default|GetGY0)) (Variables|Default|GetGStep))) 0 (- (Variables|Default|GetGNY) 1)))
  (return (Utilities|Array|Get(acopy) (Variables|Default|GetHeights) (+ i (* j (Variables|Default|GetGNX))))))
