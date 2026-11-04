param(
    [ValidateSet("low", "medium", "high", "4k")]
    [string]$Quality = "medium",
    [switch]$Preview
)

$ErrorActionPreference = "Stop"

$sceneFile = "angle_bisector_area_proof.py"
$sceneName = "AngleBisectorAreaProof"
$condaPython = "D:\Software\conda\envs\manim\python.exe"
$projectRoot = (Get-Location).Path

$qualityFlag = switch ($Quality) {
    "low" { "-ql" }
    "medium" { "-qm" }
    "high" { "-qh" }
    "4k" { "-qk" }
}

if ($Preview) {
    $qualityFlag = "-p" + $qualityFlag.Substring(1)
}

$pythonExe = $null

if (Test-Path $condaPython) {
    $pythonExe = $condaPython
} elseif (Get-Command py -ErrorAction SilentlyContinue) {
    $pythonExe = "py"
} else {
    $pythonExe = "python"
}

$mountedDrive = $null
$renderRoot = $projectRoot

foreach ($letter in @("W", "V", "U", "T", "S", "R", "Q", "P")) {
    $drive = "${letter}:"
    if (-not (Test-Path $drive)) {
        subst $drive $projectRoot
        $mountedDrive = $drive
        $renderRoot = "$drive\"
        break
    }
}

try {
    Push-Location $renderRoot

    if ($pythonExe -eq "py") {
        py -m manim $qualityFlag $sceneFile $sceneName
    } else {
        & $pythonExe -m manim $qualityFlag $sceneFile $sceneName
    }

    $output = Get-ChildItem -Path "media\videos" -Filter "$sceneName.mp4" -Recurse |
        Sort-Object LastWriteTime -Descending |
        Select-Object -First 1

    if ($output) {
        $rootForRelative = (Resolve-Path $renderRoot).Path
        if (-not $rootForRelative.EndsWith("\")) {
            $rootForRelative += "\"
        }
        $relativeOutput = $output.FullName.Substring($rootForRelative.Length)
        $actualOutput = Join-Path $projectRoot $relativeOutput
        Write-Host "Rendered video:"
        Write-Host $actualOutput
    }
} finally {
    Pop-Location
    if ($mountedDrive) {
        subst $mountedDrive /D
    }
}
