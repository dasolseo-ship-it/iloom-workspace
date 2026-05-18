# generate.ps1 — Excel 수주 데이터에서 대시보드 HTML 재생성
# 사용: .\generate.ps1 -ExcelPath "C:\path\to\grd_list_*.xlsx"

param(
    [Parameter(Mandatory=$true)]
    [string]$ExcelPath
)

$MyStores = @("송도5","인천검단","인천중앙2","김포5","부천3","의정부8","신세계시흥2","현대목동","롯데구리","롯데인천2","롯데영등포")

function Get-WeekLabel($dateStr) {
    $day = [int]($dateStr.Substring(8,2))
    $month = $dateStr.Substring(5,2)
    if ($day -le 7)  { return "1주차" }
    elseif ($day -le 14) { return "2주차" }
    elseif ($day -le 21) { return "3주차" }
    elseif ($day -le 28) { return "4주차" }
    else { return "5주차" }
}

Write-Host "Excel 파일 읽는 중: $ExcelPath"
$excel = New-Object -ComObject Excel.Application
$excel.Visible = $false
$wb = $excel.Workbooks.Open($ExcelPath)
$ws = $wb.Sheets.Item(1)
$rowCount = $ws.UsedRange.Rows.Count

$matrix = @{}
$storeTotals = @{}
$storeCount = @{}

for ($r = 2; $r -le $rowCount; $r++) {
    $store = $ws.Cells.Item($r, 6).Text
    if ($store -notin $MyStores) { continue }
    $date = $ws.Cells.Item($r, 11).Text
    if ($date -eq '') { continue }
    $amtText = $ws.Cells.Item($r, 19).Text -replace ',','' -replace '[^0-9]',''
    if ($amtText -eq '') { continue }
    $amt = [long]$amtText
    $week = Get-WeekLabel $date
    $key = "$store|$week"
    if (-not $matrix[$key]) { $matrix[$key] = 0 }
    $matrix[$key] += $amt
    if (-not $storeTotals[$store]) { $storeTotals[$store] = 0; $storeCount[$store] = 0 }
    $storeTotals[$store] += $amt
    $storeCount[$store]++
}

$wb.Close($false)
$excel.Quit()
[System.Runtime.InteropServices.Marshal]::ReleaseComObject($excel) | Out-Null

# JSON 데이터 생성
$stores = $storeTotals.Keys | Sort-Object { -$storeTotals[$_] }
$weeks = @("1주차","2주차","3주차","4주차","5주차")
$today = Get-Date -Format "yyyy-MM-dd"
$monthLabel = Get-Date -Format "yyyy년 M월"

$storesJson = ($stores | ForEach-Object { """$_""" }) -join ","
$totalsJson = ($stores | ForEach-Object { $storeTotals[$_] }) -join ","
$countJson = ($stores | ForEach-Object { $storeCount[$_] }) -join ","

$weeklyJson = @{}
foreach ($w in $weeks) {
    $vals = $stores | ForEach-Object {
        $key = "$_|$w"
        if ($matrix[$key]) { $matrix[$key] } else { 0 }
    }
    $weeklyJson[$w] = $vals -join ","
}

$grandTotal = ($storeTotals.Values | Measure-Object -Sum).Sum
$totalCount = ($storeCount.Values | Measure-Object -Sum).Sum
$topStore = $stores | Select-Object -First 1
$bottomStore = $stores | Select-Object -Last 1

Write-Host "집계 완료 — $($stores.Count)개 매장, 총 $($totalCount)건, $($grandTotal.ToString('N0'))원"
Write-Host "dashboard.html 업데이트 중..."

# HTML 파일 경로
$htmlPath = Join-Path $PSScriptRoot "index.html"
$html = Get-Content $htmlPath -Raw -Encoding UTF8

# 데이터 교체 (스크립트 블록 교체)
$newScript = @"
const STORES = [$storesJson];
const TOTALS = [$totalsJson];
const RED = '#c80a1e';
const WEEKLY = {
  "1주차": [$($weeklyJson["1주차"])],
  "2주차": [$($weeklyJson["2주차"])],
  "3주차": [$($weeklyJson["3주차"])],
  "4주차": [$($weeklyJson["4주차"])],
  "5주차": [$($weeklyJson["5주차"])],
};
"@

# 간단 치환 — STORES/TOTALS/WEEKLY 블록 교체
$html = $html -replace '(?s)const STORES = \[.*?\];.*?const WEEKLY = \{.*?\};', $newScript.Trim()

# 날짜/합계 업데이트
$html = $html -replace '기준일: \d{4}-\d{2}-\d{2}', "기준일: $today"
$html = $html -replace '\d{3},\d{3},\d{3},\d{3}원</div>\s*\s*<div class="kpi-sub">[^<]*</div>', "$($grandTotal.ToString('N0'))원</div>`n      <div class=`"kpi-sub`">$($grandTotal.ToString('N0'))원</div>"

$html | Set-Content $htmlPath -Encoding UTF8
Write-Host "완료: $htmlPath"
Write-Host "브라우저에서 열기: start '$htmlPath'"
