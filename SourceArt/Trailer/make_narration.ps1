Add-Type -AssemblyName System.Speech
$lines = @(
  @{ t = "Chronoshift."; f = "vo_01.wav" },
  @{ t = "You are stranded a hundred million years before your own time."; f = "vo_02.wav" },
  @{ t = "Era One. The prehistoric age."; f = "vo_03.wav" },
  @{ t = "No rifle. No radio. Only what you can cut, carve and sharpen."; f = "vo_04.wav" },
  @{ t = "Cross the jungle. Survive the nesting grounds. Cross the ash and the lava fields."; f = "vo_05.wav" },
  @{ t = "Something older than you is already hunting."; f = "vo_06.wav" },
  @{ t = "Find the key. Open the portal. Move on."; f = "vo_07.wav" }
)
foreach ($l in $lines) {
  $s = New-Object System.Speech.Synthesis.SpeechSynthesizer
  $s.SelectVoice("Microsoft David Desktop")
  $s.Rate = -2
  $s.SetOutputToWaveFile((Join-Path $PSScriptRoot $l.f))
  $s.Speak($l.t)
  $s.Dispose()
  Write-Output ("wrote " + $l.f)
}
