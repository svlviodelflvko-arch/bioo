<#
.SYNOPSIS
Downloads and silently installs the latest Microsoft Visual C++ Redistributable x64.

.DESCRIPTION
This script downloads the latest Visual C++ Redistributable x64 from Microsoft's official release alias
and installs it silently without restarting the machine automatically.

.NOTES
Run from an elevated PowerShell prompt or the script will relaunch itself as administrator.
#>

[CmdletBinding()]
param(
    [switch]$NoCleanup
)

function Test-Administrator {
    $currentIdentity = [Security.Principal.WindowsIdentity]::GetCurrent()
    $principal = New-Object Security.Principal.WindowsPrincipal($currentIdentity)
    if (-not $principal.IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)) {
        Write-Host 'Restarting script with elevated privileges...' -ForegroundColor Yellow
        $psi = New-Object System.Diagnostics.ProcessStartInfo
        $psi.FileName = 'powershell.exe'
        $psi.Arguments = "-NoProfile -ExecutionPolicy Bypass -File `"$PSCommandPath`""
        $psi.Verb = 'runas'
        try {
            [System.Diagnostics.Process]::Start($psi) | Out-Null
            exit 0
        } catch {
            Write-Error 'Elevation is required to install the Visual C++ Redistributable.'
            exit 1
        }
    }
}

function Get-Installer {
    param(
        [string]$Url,
        [string]$DestinationPath
    )
    Write-Host "Downloading Visual C++ Redistributable x64 from official Microsoft source..." -ForegroundColor Cyan
    try {
        [Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12
        if (Test-Path $DestinationPath) {
            Remove-Item -Path $DestinationPath -Force -ErrorAction SilentlyContinue
        }
        Invoke-WebRequest -Uri $Url -OutFile $DestinationPath -UseBasicParsing -ErrorAction Stop
        Write-Host 'Download completed.' -ForegroundColor Green
        return $true
    } catch {
        Write-Error "Failed to download the installer: $_"
        return $false
    }
}

function Install-Redistributable {
    param(
        [string]$InstallerPath
    )
    Write-Host 'Starting silent installation...' -ForegroundColor Cyan
    $arguments = '/install /quiet /norestart'
    $processInfo = New-Object System.Diagnostics.ProcessStartInfo
    $processInfo.FileName = $InstallerPath
    $processInfo.Arguments = $arguments
    $processInfo.UseShellExecute = $false
    $processInfo.RedirectStandardOutput = $true
    $processInfo.RedirectStandardError = $true

    $process = [System.Diagnostics.Process]::Start($processInfo)
    $process.WaitForExit()

    if ($process.ExitCode -eq 0) {
        Write-Host 'Visual C++ Redistributable x64 installed successfully.' -ForegroundColor Green
        return $true
    } else {
        Write-Error "Installer exited with code $($process.ExitCode)."
        return $false
    }
}

# Main
Test-Administrator

$downloadUrl = 'https://aka.ms/vs/17/release/vc_redist.x64.exe'
$installerPath = Join-Path -Path $env:TEMP -ChildPath 'vc_redist.x64.exe'

if (-not (Get-Installer -Url $downloadUrl -DestinationPath $installerPath)) {
    exit 1
}

if (-not (Install-Redistributable -InstallerPath $installerPath)) {
    exit 1
}

if (-not $NoCleanup) {
    try {
        Remove-Item -Path $installerPath -Force -ErrorAction SilentlyContinue
        Write-Host 'Temporary installer file removed.' -ForegroundColor Gray
    } catch {
        Write-Warning 'Could not remove temporary installer file. You may delete it manually.'
    }
}

Write-Host 'Done. Please restart your system if required by your environment.' -ForegroundColor Green
