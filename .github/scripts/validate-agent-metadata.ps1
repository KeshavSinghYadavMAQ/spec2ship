$ErrorActionPreference = 'Stop'

$repositoryRoot = Resolve-Path (Join-Path $PSScriptRoot '..\..')
$agentsDirectory = Join-Path $repositoryRoot '.github\agents'
$agentFiles = Get-ChildItem -Path $agentsDirectory -Filter '*.agent.md' -File
$agentNames = @{}
$errors = [System.Collections.Generic.List[string]]::new()

foreach ($file in $agentFiles) {
    $agentNames[$file.BaseName -replace '\.agent$', ''] = $true
    $content = Get-Content -Raw -Path $file.FullName
    if ($content -notmatch '(?ms)^---\r?\n.*?^description:\s*\S.*?\r?\n---\r?\n') {
        $errors.Add("$($file.Name): missing valid frontmatter description")
    }
}

$promptFiles = Get-ChildItem -Path (Join-Path $repositoryRoot '.github\prompts') -Filter '*.prompt.md' -File
foreach ($file in $promptFiles) {
    $content = Get-Content -Raw -Path $file.FullName
    $target = [regex]::Match($content, '(?m)^agent:\s*([^\s#]+)')
    if (-not $target.Success) {
        $errors.Add("$($file.Name): missing agent target")
    } elseif (-not $agentNames.ContainsKey($target.Groups[1].Value)) {
        $errors.Add("$($file.Name): target '$($target.Groups[1].Value)' does not have a matching agent file")
    }
}

$skillFiles = Get-ChildItem -Path (Join-Path $repositoryRoot '.github\skills') -Filter '*.SKILL.md' -File -Recurse
foreach ($file in $skillFiles) {
    $content = Get-Content -Raw -Path $file.FullName
    if ($content -notmatch 'Governance Gate|Readiness Gate') {
        $errors.Add("$($file.FullName): missing governance/readiness gate")
    }
}

$extensionsFile = Join-Path $repositoryRoot '.specify\extensions.yml'
if (Test-Path $extensionsFile) {
    $extensionsContent = Get-Content -Raw -Path $extensionsFile
    $commands = [regex]::Matches($extensionsContent, '(?m)^\s+command:\s*([^\s#]+)')
    foreach ($command in $commands) {
        $commandName = $command.Groups[1].Value
        if (-not $agentNames.ContainsKey($commandName)) {
            $errors.Add(".specify/extensions.yml: hook target '$commandName' does not have a matching agent file")
        }
    }
}

foreach ($file in $agentFiles) {
    $content = Get-Content -Raw -Path $file.FullName
    $targets = [regex]::Matches($content, '(?m)^\s+agent:\s*([^\s#]+)')
    foreach ($target in $targets) {
        $agentName = $target.Groups[1].Value
        if (-not $agentNames.ContainsKey($agentName)) {
            $errors.Add("$($file.Name): handoff target '$agentName' does not have a matching agent file")
        }
    }
}

if ($errors.Count -gt 0) {
    $errors | ForEach-Object { Write-Error $_ }
    exit 1
}

Write-Output "Validated $($agentFiles.Count) agent files, $($promptFiles.Count) prompt targets, $($skillFiles.Count) skills, hook targets, and handoffs."
