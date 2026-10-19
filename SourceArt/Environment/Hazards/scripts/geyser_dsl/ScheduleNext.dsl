(fn ScheduleNext ()
  (Utilities|Time|SetTimerbyFunctionName :Object self :FunctionName "StartWarning" :Time (Math|Random|RandomFloatinRange (Variables|Default|GetIdleMin) (Variables|Default|GetIdleMax)) :bLooping false))
