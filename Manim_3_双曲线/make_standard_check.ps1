$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path $Ffmpeg)) { $Ffmpeg = "ffmpeg" }

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"

& $Ffmpeg -y -ss 00:00:29.6 -i $Video -frames:v 1 -update 1 "qa_standard_29_6s.png"
& $Ffmpeg -y -ss 00:00:30.2 -i $Video -frames:v 1 -update 1 "qa_standard_30_2s.png"
& $Ffmpeg -y -ss 00:00:31.0 -i $Video -frames:v 1 -update 1 "qa_standard_31_0s.png"
