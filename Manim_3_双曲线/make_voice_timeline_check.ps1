$Ffmpeg = "D:\Software\conda\envs\manim\Library\bin\ffmpeg.exe"
if (-not (Test-Path -LiteralPath $Ffmpeg)) { $Ffmpeg = "ffmpeg" }

$Video = "media\videos\reciprocal_polar_hyperbola\720p30\ReciprocalPolarHyperbola.mp4"

$Frames = @(
    @("00:00:02.0", "qa_voice_02_headline.png"),
    @("00:00:09.5", "qa_voice_09_intro_graph.png"),
    @("00:00:18.5", "qa_voice_18_xy.png"),
    @("00:00:22.0", "qa_voice_22_polar_point.png"),
    @("00:00:31.8", "qa_voice_31_polar_formula.png"),
    @("00:00:40.5", "qa_voice_40_rotate.png"),
    @("00:00:48.0", "qa_voice_48_angle_relation.png"),
    @("00:00:57.5", "qa_voice_57_cos_formula.png"),
    @("00:01:07.5", "qa_voice_67_coordinates.png"),
    @("00:01:14.5", "qa_voice_74_standard.png"),
    @("00:01:20.5", "qa_voice_80_equal_axis.png"),
    @("00:01:27.0", "qa_voice_87_final.png")
)

foreach ($Frame in $Frames) {
    & $Ffmpeg -y -ss $Frame[0] -i $Video -frames:v 1 -update 1 $Frame[1]
}
