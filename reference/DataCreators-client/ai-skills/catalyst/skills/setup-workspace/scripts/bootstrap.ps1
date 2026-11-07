<#
bootstrap.ps1 — Windows counterpart to bootstrap.sh.  Ensures Python 3.10+ is
available for AI Catalyst using no Python itself.  Installs Python 3.13 via
winget or choco when present, or guides the user to the Capital Group app store
/ Company Portal (IT self-service).  Never runs an elevated or unsanctioned
remote installer script.

Once this exits 0, run scripts/setup_workspace.py for the pip and dependency
steps (those genuinely need Python).

Exit codes (match bootstrap.sh):
  0  Python 3.10+ is present and ready
  3  Python missing/old and could not be provisioned here (no installer, or the
     install did not produce a usable Python); guidance printed
#>

$MinMajor = 3
$MinMinor = 10
$Recommended = '3.13'

# Print "MAJOR MINOR" for the first usable interpreter, or $null.
function Get-PythonVersion {
    foreach ($exe in @('python', 'python3', 'py')) {
        if (Get-Command $exe -ErrorAction SilentlyContinue) {
            $out = & $exe -c 'import sys; print("%d %d" % sys.version_info[:2])' 2>$null
            if ($LASTEXITCODE -eq 0 -and $out -match '^\d+ \d+$') { return $out }
        }
    }
    return $null
}

function Test-VersionOk([string]$ver) {
    if (-not $ver) { return $false }
    $p = $ver.Split(' ')
    $maj = [int]$p[0]; $min = [int]$p[1]
    if ($maj -gt $MinMajor) { return $true }
    if ($maj -eq $MinMajor -and $min -ge $MinMinor) { return $true }
    return $false
}

# Returns $true (and prints) if Python 3.10+ is present.  Uses Write-Host so the
# boolean is the only value on the output stream.
function Report-Python {
    $ver = Get-PythonVersion
    if ($ver) {
        $p = $ver.Split(' ')
        if (Test-VersionOk $ver) {
            Write-Host "Python $($p[0]).$($p[1]) is present (>= $MinMajor.$MinMinor)."
            return $true
        }
        Write-Host "Python $($p[0]).$($p[1]) is present but older than $MinMajor.$MinMinor."
        return $false
    }
    Write-Host "Python is not installed."
    return $false
}

function Invoke-Guide {
    Write-Host ""
    Write-Host "Cannot install Python here without a package manager."
    Write-Host "Install Python $Recommended through the Capital Group app store or Company Portal (IT self-service), then re-run this script."
    exit 3
}

# 1) Already good?
if (Report-Python) { exit 0 }

# 2) Try the package managers, best-effort: winget, then choco, then uv.  Any
# failure falls through to the guidance step below.
if (Get-Command winget -ErrorAction SilentlyContinue) {
    Write-Host "Installing Python $Recommended via winget..."
    winget install -e --id "Python.Python.$Recommended" --accept-source-agreements --accept-package-agreements
    if (Report-Python) { exit 0 }
    Write-Host "winget did not yield a usable Python; trying other options."
}
if (Get-Command choco -ErrorAction SilentlyContinue) {
    Write-Host "Installing Python $Recommended via choco..."
    choco install python --version=$Recommended -y
    if (Report-Python) { exit 0 }
    Write-Host "choco did not yield a usable Python; trying other options."
}
if (Get-Command uv -ErrorAction SilentlyContinue) {
    Write-Host "Installing Python $Recommended via uv..."
    uv python install --default $Recommended
    if (Report-Python) { exit 0 }
    Write-Host "uv did not yield a usable Python on PATH; falling back to guidance."
}

# 3) Nothing produced a usable Python -> guide.
Invoke-Guide
