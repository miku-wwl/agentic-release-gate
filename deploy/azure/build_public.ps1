param([string]$Repository = 'docker.io/minglai/releasegate-demo')
$ErrorActionPreference = 'Stop'
Set-StrictMode -Version Latest
$repositoryRoot = (Resolve-Path (Join-Path $PSScriptRoot '../..')).Path
Push-Location $repositoryRoot
try {
    $changes = git status --porcelain=v1 --untracked-files=all
    if ($LASTEXITCODE -ne 0 -or $changes) { throw 'A clean committed checkout is required' }
    $sourceSha = git rev-parse HEAD
    if ($LASTEXITCODE -ne 0 -or $sourceSha -notmatch '^[0-9a-f]{40}$') { throw 'Commit identity unavailable' }
    $entries = git ls-tree -r HEAD
    if ($entries | Where-Object { $_ -notmatch '^(100644|100755) blob ' }) { throw 'Only regular tracked source files are supported' }
    $buildId = $sourceSha + '-' + [guid]::NewGuid().ToString('N')
    $artifactRoot = Join-Path $repositoryRoot '.artifacts/public-live'
    $buildContext = Join-Path $artifactRoot ('build-' + $buildId)
    New-Item -ItemType Directory -Path $buildContext | Out-Null
    $archivePath = Join-Path $artifactRoot ('source-' + $buildId + '.tar')
    git archive --format=tar --output=$archivePath $sourceSha
    if ($LASTEXITCODE -ne 0) { throw 'Source export failed' }
    tar -xf $archivePath -C $buildContext
    if ($LASTEXITCODE -ne 0) { throw 'Source extraction failed' }
    $image = $Repository + ':' + $sourceSha
    docker build --platform linux/amd64 --progress=plain --file (Join-Path $buildContext 'deploy/azure/Dockerfile.public') --build-arg SOURCE_SHA=$sourceSha --tag $image $buildContext 2>&1 | Tee-Object -FilePath (Join-Path $artifactRoot ('build-' + $sourceSha + '.log'))
    if ($LASTEXITCODE -ne 0) { throw 'Docker build failed' }
    Write-Output "BUILT_IMAGE=$image"
}
finally { Pop-Location }
