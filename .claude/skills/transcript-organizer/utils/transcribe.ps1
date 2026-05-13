# Audio Transcription via OpenAI Whisper API
# Usage: .\transcribe.ps1 -FilePath "C:\path\to\audio.m4a" [-Language "ko"] [-OutputPath "C:\path\to\output.txt"]
# Required env var: OPENAI_API_KEY

param(
    [Parameter(Mandatory=$true)][string]$FilePath,
    [string]$Language = "ko",
    [string]$OutputPath = ""
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8

# 환경변수 확인
if (-not $env:OPENAI_API_KEY) {
    Write-Error "OPENAI_API_KEY 환경변수가 설정되지 않았습니다."
    Write-Output "설정 방법: `$env:OPENAI_API_KEY = 'sk-...'"
    exit 1
}

# 파일 확인
if (-not (Test-Path $FilePath)) {
    Write-Error "파일을 찾을 수 없습니다: $FilePath"
    exit 1
}

$fileInfo = Get-Item $FilePath
$supportedFormats = @(".mp3", ".mp4", ".m4a", ".wav", ".webm", ".ogg", ".flac", ".mpeg", ".mpga")
if ($supportedFormats -notcontains $fileInfo.Extension.ToLower()) {
    Write-Error "지원하지 않는 형식입니다: $($fileInfo.Extension)"
    Write-Output "지원 형식: $($supportedFormats -join ', ')"
    exit 1
}

# 파일 크기 확인 (Whisper API 제한: 25MB)
$fileSizeMB = [Math]::Round($fileInfo.Length / 1MB, 1)
Write-Output "파일: $($fileInfo.Name) ($fileSizeMB MB)"

if ($fileInfo.Length -gt 25MB) {
    Write-Error "파일이 25MB를 초과합니다 ($fileSizeMB MB). 파일을 분할 후 다시 시도해주세요."
    exit 1
}

Write-Output "Whisper API로 변환 중... (언어: $Language)"

# Multipart form-data 구성
$boundary = [System.Guid]::NewGuid().ToString()
$fileBytes = [System.IO.File]::ReadAllBytes($FilePath)
$fileName  = $fileInfo.Name

# MIME 타입 매핑
$mimeMap = @{
    ".mp3"  = "audio/mpeg"
    ".mp4"  = "audio/mp4"
    ".m4a"  = "audio/mp4"
    ".wav"  = "audio/wav"
    ".webm" = "audio/webm"
    ".ogg"  = "audio/ogg"
    ".flac" = "audio/flac"
    ".mpeg" = "audio/mpeg"
    ".mpga" = "audio/mpeg"
}
$mimeType = $mimeMap[$fileInfo.Extension.ToLower()]

# Body 조립
$bodyParts = [System.Collections.Generic.List[byte]]::new()

function Add-TextPart($name, $value) {
    $part = "--$boundary`r`nContent-Disposition: form-data; name=`"$name`"`r`n`r`n$value`r`n"
    $bytes = [System.Text.Encoding]::UTF8.GetBytes($part)
    $bodyParts.AddRange($bytes)
}

function Add-FilePart($name, $fname, $mime, $data) {
    $header = "--$boundary`r`nContent-Disposition: form-data; name=`"$name`"; filename=`"$fname`"`r`nContent-Type: $mime`r`n`r`n"
    $bodyParts.AddRange([System.Text.Encoding]::UTF8.GetBytes($header))
    $bodyParts.AddRange($data)
    $bodyParts.AddRange([System.Text.Encoding]::UTF8.GetBytes("`r`n"))
}

Add-TextPart "model"    "whisper-1"
Add-TextPart "language" $Language
Add-TextPart "response_format" "text"
Add-FilePart "file" $fileName $mimeType $fileBytes
$bodyParts.AddRange([System.Text.Encoding]::UTF8.GetBytes("--$boundary--`r`n"))

# API 호출
try {
    $req = [System.Net.HttpWebRequest]::Create("https://api.openai.com/v1/audio/transcriptions")
    $req.Method = "POST"
    $req.Headers.Add("Authorization", "Bearer $env:OPENAI_API_KEY")
    $req.ContentType = "multipart/form-data; boundary=$boundary"
    $req.ContentLength = $bodyParts.Count
    $req.Timeout = 300000  # 5분

    $bodyArray = $bodyParts.ToArray()
    $stream = $req.GetRequestStream()
    $stream.Write($bodyArray, 0, $bodyArray.Length)
    $stream.Close()

    $resp   = $req.GetResponse()
    $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $transcript = $reader.ReadToEnd()
    $reader.Close(); $resp.Close()

} catch [System.Net.WebException] {
    $errReader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream(), [System.Text.Encoding]::UTF8)
    $errBody = $errReader.ReadToEnd()
    Write-Error "API 오류: $errBody"
    exit 1
}

# 결과 저장
if ($OutputPath -eq "") {
    $OutputPath = [System.IO.Path]::ChangeExtension($FilePath, ".txt")
}

[System.IO.File]::WriteAllText($OutputPath, $transcript, [System.Text.Encoding]::UTF8)

$lineCount = ($transcript -split "`n").Count
Write-Output "변환 완료!"
Write-Output "저장 경로: $OutputPath"
Write-Output "글자 수: $($transcript.Length)자 / $lineCount 줄"
Write-Output ""
Write-Output "--- 미리보기 (첫 200자) ---"
Write-Output $transcript.Substring(0, [Math]::Min(200, $transcript.Length))
