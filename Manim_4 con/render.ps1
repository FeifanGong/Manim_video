param(
    [ValidateSet("l", "m", "h", "p", "k")]
    [string]$Quality = "m",

    [switch]$Preview
)

$ErrorActionPreference = "Stop"

$Python = "D:\Software\conda\envs\manim\python.exe"
$Scene = "SymmetricSubstitutionMax"
$Script = "symmetric_substitution_max.py"

if (-not (Test-Path -LiteralPath $Python)) {
    throw "Manim Python not found: $Python"
}

$manimArgs = @("-m", "manim", "-q$Quality")
if ($Preview) {
    $manimArgs += "-p"
}
$manimArgs += @($Script, $Scene)

& $Python @manimArgs
