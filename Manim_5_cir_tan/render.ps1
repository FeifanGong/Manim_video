param(
    [ValidateSet('l', 'm', 'h', 'k')]
    [string]$Quality = 'h',
    [switch]$Preview
)
$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$manimEnv = 'D:\Software\conda\envs\manim'
$env:PATH = "$manimEnv;$manimEnv\Scripts;$manimEnv\Library\bin;$env:PATH"
Push-Location $PSScriptRoot
try {
    $renderArgs = @('-m', 'manim', "-q$Quality", 'Circle_Tangent_manim.py', 'CircleTangentProjection')
    if ($Preview) { $renderArgs += '-p' }
    & "$manimEnv\python.exe" @renderArgs
    if ($LASTEXITCODE -ne 0) { throw "Manim failed with exit code $LASTEXITCODE" }
} finally {
    Pop-Location
}
