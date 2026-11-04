param(
    [ValidateSet('l', 'm', 'h', 'k')]
    [string]$Quality = 'h',
    [ValidateSet('OddEvenDecomposition', 'DecompositionProof', 'HyperbolicFunctions')]
    [string]$Scene = 'OddEvenDecomposition',
    [switch]$Preview,
    [switch]$LastFrame,
    [string]$Python = 'D:\Software\conda\envs\manim\python.exe'
)

$ErrorActionPreference = 'Stop'
if (-not (Test-Path -LiteralPath $Python -PathType Leaf)) {
    throw "Manim Python not found: $Python. Pass -Python with your virtual environment's python.exe."
}
$manimEnv = Split-Path -Parent $Python
$originalPath = $env:PATH
$originalEncoding = $env:PYTHONIOENCODING
$env:PYTHONIOENCODING = 'utf-8'
# The scene configures an ASCII temporary TeX cache for Chinese paths.
$env:PATH = "$manimEnv;$manimEnv\Scripts;$manimEnv\Library\bin;$env:PATH"
Push-Location $PSScriptRoot
try {
    $renderArgs = @('-m', 'manim', "-q$Quality")
    if ($Preview) { $renderArgs += '-p' }
    if ($LastFrame) { $renderArgs += '-s' }
    $renderArgs += @('Odd_Even_manim.py', $Scene)
    & $Python @renderArgs
    if ($LASTEXITCODE -ne 0) { throw "Manim failed with exit code $LASTEXITCODE." }
}
finally {
    Pop-Location
    $env:PATH = $originalPath
    $env:PYTHONIOENCODING = $originalEncoding
}
