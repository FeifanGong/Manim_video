param(
    [ValidateSet("low", "medium", "high", "production")]
    [string]$Quality = "medium"
)

$ErrorActionPreference = "Stop"

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$StageDir = "D:\manim_render_reciprocal"

$Python = "D:\Software\conda\envs\manim\python.exe"
if (-not (Test-Path $Python)) {
    $Python = "python"
}

$TexLiveBin = "d:\texlive\texlive\2026\bin\windows"
if (Test-Path $TexLiveBin) {
    $env:PATH = "$TexLiveBin;$env:PATH"
}
$env:PYTHONIOENCODING = "utf-8"

$QualityFlag = @{
    low = "-ql"
    medium = "-qm"
    high = "-qh"
    production = "-qp"
}[$Quality]

New-Item -ItemType Directory -Force -Path $StageDir | Out-Null

Copy-Item -Force (Join-Path $SourceDir "reciprocal_polar_hyperbola.py") $StageDir
Copy-Item -Force (Join-Path $SourceDir "manim.cfg") $StageDir

$VoiceFolderName = [string]([char]0x914D) + [string]([char]0x97F3)
$VoiceSource = Join-Path $SourceDir $VoiceFolderName
if (Test-Path -LiteralPath $VoiceSource) {
    Copy-Item -Force -Recurse -LiteralPath $VoiceSource -Destination $StageDir
}

Push-Location $StageDir
try {
    & $Python -m manim $QualityFlag reciprocal_polar_hyperbola.py ReciprocalPolarHyperbola
}
finally {
    Pop-Location
}

$RenderedRoot = Join-Path $StageDir "media\videos\reciprocal_polar_hyperbola"
$Rendered = Get-ChildItem -Path $RenderedRoot -Recurse -Filter "ReciprocalPolarHyperbola.mp4" |
    Sort-Object LastWriteTime -Descending |
    Select-Object -First 1

if (-not $Rendered) {
    throw "Manim finished, but no rendered mp4 was found."
}

$RelativePath = $Rendered.FullName.Substring($StageDir.Length + 1)
$Destination = Join-Path $SourceDir $RelativePath
$DestinationDir = Split-Path -Parent $Destination
New-Item -ItemType Directory -Force -Path $DestinationDir | Out-Null
Copy-Item -Force $Rendered.FullName $Destination

$MuxScript = Join-Path $SourceDir "mux_voiceover.ps1"
if (Test-Path -LiteralPath $MuxScript) {
    & powershell -ExecutionPolicy Bypass -File $MuxScript -VideoPath $Destination
}

Write-Host "Copied video to $Destination"
