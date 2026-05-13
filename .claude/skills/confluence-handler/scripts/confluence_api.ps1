# Confluence API PowerShell Script (PowerShell 5.1 compatible)
# Usage: .\confluence_api.ps1 <command> [options]
# Required env vars: CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_TOKEN

param(
    [Parameter(Position=0, Mandatory=$true)][string]$Command,
    [string]$SpaceKey,
    [string]$PageId,
    [string]$Title,
    [string]$Body,
    [string]$Query,
    [string]$Label,
    [string]$Comment,
    [string]$ParentId,
    [int]$Limit = 25,
    [string]$FilePath
)

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
$OutputEncoding = [System.Text.Encoding]::UTF8

if (-not $env:CONFLUENCE_URL -or -not $env:CONFLUENCE_EMAIL -or -not $env:CONFLUENCE_TOKEN) {
    Write-Error "환경변수를 설정해주세요: CONFLUENCE_URL, CONFLUENCE_EMAIL, CONFLUENCE_TOKEN"
    exit 1
}

$base = $env:CONFLUENCE_URL.TrimEnd('/')
$base64Auth = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("$($env:CONFLUENCE_EMAIL):$($env:CONFLUENCE_TOKEN)"))
$Headers = @{
    "Authorization" = "Basic $base64Auth"
    "Accept"        = "application/json"
}

function Invoke-CF {
    param([string]$Uri, [string]$Method = "GET", [string]$BodyContent)
    try {
        $req = [System.Net.HttpWebRequest]::Create($Uri)
        $req.Method = $Method
        $req.Headers.Add("Authorization", $Headers["Authorization"])
        $req.Accept = "application/json"
        $req.Headers.Add("X-Atlassian-Token", "no-check")

        if ($BodyContent) {
            $req.ContentType = "application/json; charset=utf-8"
            $bodyBytes = [System.Text.Encoding]::UTF8.GetBytes($BodyContent)
            $req.ContentLength = $bodyBytes.Length
            $stream = $req.GetRequestStream()
            $stream.Write($bodyBytes, 0, $bodyBytes.Length)
            $stream.Close()
        }

        $resp = $req.GetResponse()
        $reader = New-Object System.IO.StreamReader($resp.GetResponseStream(), [System.Text.Encoding]::UTF8)
        $json = $reader.ReadToEnd() | ConvertFrom-Json
        $reader.Close()
        $resp.Close()
        return $json
    } catch [System.Net.WebException] {
        $errMsg = $_.Exception.Message
        try {
            $errReader = New-Object System.IO.StreamReader($_.Exception.Response.GetResponseStream(), [System.Text.Encoding]::UTF8)
            $errBody = $errReader.ReadToEnd() | ConvertFrom-Json
            if ($errBody.message) { $errMsg = $errBody.message }
        } catch {}
        Write-Error "API 오류: $errMsg"
        exit 1
    }
}

switch ($Command) {

    "list-spaces" {
        $r = Invoke-CF "$base/wiki/rest/api/space?limit=$Limit&expand=description.plain"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Key=$_.key; Name=$_.name; Type=$_.type }
        } | Format-Table -AutoSize
    }

    "get-space" {
        if (-not $SpaceKey) { Write-Error "-SpaceKey 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/space/$SpaceKey`?expand=description.plain,homepage"
        Write-Output "Key : $($r.key)"
        Write-Output "Name: $($r.name)"
        Write-Output "Type: $($r.type)"
        Write-Output "Home: $($r.homepage.title)"
        Write-Output "Desc: $($r.description.plain.value)"
    }

    "list-pages" {
        if (-not $SpaceKey) { Write-Error "-SpaceKey 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/space/$SpaceKey/content/page?limit=$Limit&expand=version"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Title=$_.title; Version=$_.version.number }
        } | Format-Table -AutoSize
    }

    "get-page" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId`?expand=body.storage,version,space"
        Write-Output "제목  : $($r.title)"
        Write-Output "스페이스: $($r.space.name) [$($r.space.key)]"
        Write-Output "버전  : $($r.version.number)"
        Write-Output "URL   : $base/wiki$($r._links.webui)"
        Write-Output "---"
        $text = $r.body.storage.value -replace '<[^>]+>', ''
        Write-Output $text
    }

    "get-page-by-title" {
        if (-not $SpaceKey -or -not $Title) { Write-Error "-SpaceKey, -Title 필요"; exit 1 }
        $enc = [Uri]::EscapeDataString($Title)
        $r = Invoke-CF "$base/wiki/rest/api/content?spaceKey=$SpaceKey&title=$enc&expand=version"
        if ($r.results.Count -eq 0) { Write-Output "페이지 없음"; exit 0 }
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Title=$_.title; Version=$_.version.number }
        } | Format-Table -AutoSize
    }

    "create-page" {
        if (-not $SpaceKey -or -not $Title -or -not $Body) { Write-Error "-SpaceKey, -Title, -Body 필요"; exit 1 }
        $payload = @{
            type  = "page"
            title = $Title
            space = @{ key = $SpaceKey }
            body  = @{ storage = @{ value = $Body; representation = "storage" } }
        }
        if ($ParentId) { $payload.ancestors = @(@{ id = $ParentId }) }
        $r = Invoke-CF "$base/wiki/rest/api/content" "POST" ($payload | ConvertTo-Json -Depth 10)
        Write-Output "페이지 생성 완료!"
        Write-Output "ID : $($r.id)"
        Write-Output "URL: $base/wiki$($r._links.webui)"
    }

    "update-page" {
        if (-not $PageId -or -not $Title -or -not $Body) { Write-Error "-PageId, -Title, -Body 필요"; exit 1 }
        $current = Invoke-CF "$base/wiki/rest/api/content/$PageId`?expand=version"
        $newVer = $current.version.number + 1
        $payload = @{
            type    = "page"
            title   = $Title
            version = @{ number = $newVer }
            body    = @{ storage = @{ value = $Body; representation = "storage" } }
        } | ConvertTo-Json -Depth 10
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId" "PUT" $payload
        Write-Output "페이지 업데이트 완료! 버전: $($r.version.number)"
    }

    "delete-page" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        Invoke-CF "$base/wiki/rest/api/content/$PageId" "DELETE" | Out-Null
        Write-Output "페이지 삭제 완료 (ID: $PageId)"
    }

    "get-children" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId/child/page?limit=$Limit"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Title=$_.title }
        } | Format-Table -AutoSize
    }

    "list-blogs" {
        if (-not $SpaceKey) { Write-Error "-SpaceKey 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/space/$SpaceKey/content/blogpost?limit=$Limit&expand=version"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Title=$_.title; Author=$_.version.by.displayName }
        } | Format-Table -AutoSize
    }

    "create-blog" {
        if (-not $SpaceKey -or -not $Title -or -not $Body) { Write-Error "-SpaceKey, -Title, -Body 필요"; exit 1 }
        $payload = @{
            type  = "blogpost"
            title = $Title
            space = @{ key = $SpaceKey }
            body  = @{ storage = @{ value = $Body; representation = "storage" } }
        } | ConvertTo-Json -Depth 10
        $r = Invoke-CF "$base/wiki/rest/api/content" "POST" $payload
        Write-Output "블로그 포스트 생성 완료!"
        Write-Output "ID : $($r.id)"
        Write-Output "URL: $base/wiki$($r._links.webui)"
    }

    "search" {
        if (-not $Query) { Write-Error "-Query 필요 (CQL 쿼리)"; exit 1 }
        $enc = [Uri]::EscapeDataString($Query)
        $r = Invoke-CF "$base/wiki/rest/api/content/search?cql=$enc&limit=$Limit&expand=space,version"
        Write-Output "검색 결과: $($r.totalSize)건"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Type=$_.type; Space=$_.space.key; Title=$_.title }
        } | Format-Table -AutoSize
    }

    "list-comments" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId/child/comment?expand=body.view,version"
        $r.results | ForEach-Object {
            $author = $_.version.by.displayName
            $when = $_.version.when
            $text = $_.body.view.value -replace '<[^>]+>', ''
            Write-Output "[$author / $when]"
            Write-Output $text
            Write-Output "---"
        }
    }

    "add-comment" {
        if (-not $PageId -or -not $Comment) { Write-Error "-PageId, -Comment 필요"; exit 1 }
        $payload = @{
            type      = "comment"
            container = @{ id = $PageId; type = "page" }
            body      = @{ storage = @{ value = "<p>$Comment</p>"; representation = "storage" } }
        } | ConvertTo-Json -Depth 10
        $r = Invoke-CF "$base/wiki/rest/api/content" "POST" $payload
        Write-Output "댓글 추가 완료! (ID: $($r.id))"
    }

    "get-labels" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId/label"
        $names = $r.results | ForEach-Object { $_.name }
        Write-Output ($names -join ", ")
    }

    "add-label" {
        if (-not $PageId -or -not $Label) { Write-Error "-PageId, -Label 필요"; exit 1 }
        $payload = '[{"prefix":"global","name":"' + $Label + '"}]'
        Invoke-CF "$base/wiki/rest/api/content/$PageId/label" "POST" $payload | Out-Null
        Write-Output "레이블 추가 완료: $Label"
    }

    "remove-label" {
        if (-not $PageId -or -not $Label) { Write-Error "-PageId, -Label 필요"; exit 1 }
        Invoke-CF "$base/wiki/rest/api/content/$PageId/label/$Label" "DELETE" | Out-Null
        Write-Output "레이블 삭제 완료: $Label"
    }

    "list-attachments" {
        if (-not $PageId) { Write-Error "-PageId 필요"; exit 1 }
        $r = Invoke-CF "$base/wiki/rest/api/content/$PageId/child/attachment"
        $r.results | ForEach-Object {
            [PSCustomObject]@{ Id=$_.id; Title=$_.title; Size=$_.extensions.fileSize; Type=$_.extensions.mediaType }
        } | Format-Table -AutoSize
    }

    default {
        Write-Output "사용 가능한 명령어:"
        Write-Output "  list-spaces / get-space -SpaceKey KEY"
        Write-Output "  list-pages -SpaceKey KEY / get-page -PageId ID"
        Write-Output "  get-page-by-title -SpaceKey KEY -Title 제목"
        Write-Output "  create-page -SpaceKey KEY -Title 제목 -Body HTML [-ParentId ID]"
        Write-Output "  update-page -PageId ID -Title 제목 -Body HTML"
        Write-Output "  delete-page -PageId ID / get-children -PageId ID"
        Write-Output "  list-blogs -SpaceKey KEY / create-blog -SpaceKey KEY -Title 제목 -Body HTML"
        Write-Output "  search -Query CQL문"
        Write-Output "  list-comments -PageId ID / add-comment -PageId ID -Comment 내용"
        Write-Output "  get-labels -PageId ID / add-label -PageId ID -Label 이름 / remove-label -PageId ID -Label 이름"
        Write-Output "  list-attachments -PageId ID"
    }
}
