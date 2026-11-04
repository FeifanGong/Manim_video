$ErrorActionPreference = "Stop"

$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path $Ffmpeg)) {
    $Ffmpeg = "ffmpeg"
}

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"

& $Ffmpeg -y -ss 00:00:03.8 -i $Video -frames:v 1 -update 1 "qa_intro_3_8s.png"
& $Ffmpeg -y -ss 00:00:04.4 -i $Video -frames:v 1 -update 1 "qa_intro_4_4s.png"
