$ErrorActionPreference = "Stop"

$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path $Ffmpeg)) {
    $Ffmpeg = "ffmpeg"
}

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"
$Output = "qa_reciprocal_hyperbola.png"

& $Ffmpeg -y -i $Video -vf "fps=1/4,scale=320:180,tile=4x3" -frames:v 1 -update 1 $Output
