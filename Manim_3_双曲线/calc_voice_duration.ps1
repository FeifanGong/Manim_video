$ErrorActionPreference = "Stop"

$VoiceFolderName = [string]([char]0x914D) + [string]([char]0x97F3)
$Folder = Join-Path (Get-Location) $VoiceFolderName
if (-not (Test-Path -LiteralPath $Folder)) {
    throw "Folder not found: $Folder"
}

$Ffprobe = "D:\Software\conda\envs\manim\Library\bin\ffprobe.exe"
if (-not (Test-Path -LiteralPath $Ffprobe)) {
    $Ffprobe = "ffprobe"
}

$Extensions = @(".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg", ".opus", ".wma")
$Files = Get-ChildItem -LiteralPath $Folder -Recurse -File |
    Where-Object { $Extensions -contains $_.Extension.ToLowerInvariant() } |
    Sort-Object FullName

$Total = 0.0
foreach ($File in $Files) {
    $DurationText = & $Ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 -- $File.FullName
    $Duration = [double]::Parse(($DurationText | Select-Object -First 1), [System.Globalization.CultureInfo]::InvariantCulture)
    $Total += $Duration
    "{0}`t{1:N3}`t{2}" -f $File.Name, $Duration, ([TimeSpan]::FromSeconds($Duration)).ToString("hh\:mm\:ss\.fff")
}

"TOTAL_SECONDS={0:N3}" -f $Total
"TOTAL_TIME={0}" -f ([TimeSpan]::FromSeconds($Total)).ToString("hh\:mm\:ss\.fff")
"FILE_COUNT={0}" -f $Files.Count
