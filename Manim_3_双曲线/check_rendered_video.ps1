param(
    [string]$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"
)

$ErrorActionPreference = "Stop"

$Ffprobe = "D:\Software\conda\envs\manim\Library\bin\ffprobe.exe"
if (-not (Test-Path -LiteralPath $Ffprobe)) {
    $Ffprobe = "ffprobe"
}

& $Ffprobe -v error -show_entries format=duration:stream=index,codec_type,codec_name,width,height,r_frame_rate,duration -of default=noprint_wrappers=1 $Video
