param(
    [ValidateSet('l', 'm', 'h', 'k')]
    [string]$Quality = 'h',
    [switch]$Preview,
    [switch]$LastFrame,
    [string]$Python = 'D:\Software\conda\envs\manim\python.exe'
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Manim Python not found: $Python. Pass -Python with your environment's python.exe."
}
$manimEnv = Split-Path -Parent $Python
$savedPath = $env:PATH
$savedEncoding = $env:PYTHONIOENCODING
$env:PATH = "$manimEnv;$manimEnv\Scripts;$manimEnv\Library\bin;$env:PATH"
$env:PYTHONIOENCODING = 'utf-8'
Push-Location $PSScriptRoot
try {
    # Keep 30 fps for all quality presets, including 1080p (-qh).
    $renderArgs = @('-m', 'manim', "-q$Quality", '--fps', '30')
    if ($Preview) { $renderArgs += '-p' }
    if ($LastFrame) { $renderArgs += '-s' }
    $renderArgs += @('Cauchy_Tangent_manim.py', 'CauchyEllipseTangent')
    & $Python @renderArgs
    if ($LASTEXITCODE -ne 0) { throw "Manim render failed with exit code $LASTEXITCODE." }
}
finally {
    Pop-Location
    $env:PATH = $savedPath
    $env:PYTHONIOENCODING = $savedEncoding
}
