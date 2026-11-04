param(
    [string]$VideoPath = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"
)

$ErrorActionPreference = "Stop"

$SourceDir = Split-Path -Parent $MyInvocation.MyCommand.Path
if (-not [System.IO.Path]::IsPathRooted($VideoPath)) {
    $VideoPath = Join-Path $SourceDir $VideoPath
}

$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path -LiteralPath $Ffmpeg)) { $Ffmpeg = "ffmpeg" }

$Ffprobe = "D:\Software\conda\envs\manim\Library\bin\ffprobe.exe"
if (-not (Test-Path -LiteralPath $Ffprobe)) { $Ffprobe = "ffprobe" }

$VoiceFolderName = [string]([char]0x914D) + [string]([char]0x97F3)
$VoiceDir = Join-Path $SourceDir $VoiceFolderName
if (-not (Test-Path -LiteralPath $VoiceDir)) {
    throw "Voice folder not found: $VoiceDir"
}

$VideoDurationText = & $Ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 $VideoPath
$VideoDuration = [double]::Parse(($VideoDurationText | Select-Object -First 1), [System.Globalization.CultureInfo]::InvariantCulture)

# Start times in seconds, matched to the current Manim animation timeline.
$Starts = @(
    0.000,
    1.352,
    6.968,
    16.282,
    20.446,
    29.246,
    37.688,
    42.512,
    46.056,
    55.588,
    62.466,
    67.356,
    74.320,
    79.752,
    83.664
)

$Inputs = @()
$Filters = @()
$Labels = @("[sil]")

for ($i = 1; $i -le 15; $i++) {
    $File = Get-ChildItem -LiteralPath $VoiceDir -File -Filter ("{0:D4}_*.mp3" -f $i) |
        Sort-Object Name |
        Select-Object -First 1
    if (-not $File) {
        throw ("Missing voice file {0:D4}_*.mp3" -f $i)
    }

    $Inputs += @("-i", $File.FullName)
    $DelayMs = [int][Math]::Round($Starts[$i - 1] * 1000)
    $Label = "[v$i]"
    $Filters += "[{0}:a]adelay=delays={1}:all=1,aresample=48000{2}" -f ($i - 1), $DelayMs, $Label
    $Labels += $Label
}

$FilterComplex = "anullsrc=r=48000:cl=stereo:d=$VideoDuration[sil];" +
    (($Filters -join ";") + ";") +
    (($Labels -join "") + "amix=inputs=16:duration=first:normalize=0[aout]")

$MixedAudio = Join-Path $SourceDir "voiceover_mix.wav"
$TempOutput = Join-Path $SourceDir "voiceover_muxed_tmp.mp4"

& $Ffmpeg -y @Inputs -filter_complex $FilterComplex -map "[aout]" -c:a pcm_s16le $MixedAudio
& $Ffmpeg -y -i $VideoPath -i $MixedAudio -map 0:v:0 -map 1:a:0 -c:v copy -c:a aac -b:a 192k -movflags +faststart $TempOutput
Move-Item -Force -LiteralPath $TempOutput -Destination $VideoPath

Write-Host "Muxed 15 voice clips into $VideoPath"
