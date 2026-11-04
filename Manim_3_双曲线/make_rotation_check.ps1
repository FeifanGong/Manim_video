$ErrorActionPreference = "Stop"

$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path $Ffmpeg)) {
    $Ffmpeg = "ffmpeg"
}

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"

& $Ffmpeg -y -ss 00:00:19.6 -i $Video -frames:v 1 -update 1 "qa_rotation_19_6s.png"
& $Ffmpeg -y -ss 00:00:20.4 -i $Video -frames:v 1 -update 1 "qa_rotation_20_4s.png"
& $Ffmpeg -y -ss 00:00:21.2 -i $Video -frames:v 1 -update 1 "qa_rotation_21_2s.png"
