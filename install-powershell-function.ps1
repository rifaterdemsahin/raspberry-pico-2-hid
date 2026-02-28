# install-powershell-function.ps1
# Adds Send-ToPico function to PowerShell profile for global access

$ProfilePath = $PROFILE
$ProjectDir = $PSScriptRoot

# Function definition to add to profile
$FunctionCode = @"

# Raspberry Pi Pico 2 W - Send text via WiFi
function Send-ToPico {
    param(
        [Parameter(Position=0, Mandatory=`$false)]
        [string]`$Text,

        [Parameter(Mandatory=`$false)]
        [switch]`$Clipboard
    )

    `$ProjectDir = "$ProjectDir"
    Push-Location `$ProjectDir

    try {
        if (`$Clipboard) {
            python send_wifi.py --clip
        }
        elseif (`$Text) {
            python send_wifi.py `$Text
        }
        else {
            Write-Host "Usage: Send-ToPico 'text to send'"
            Write-Host "       Send-ToPico -Clipboard"
        }
    }
    finally {
        Pop-Location
    }
}

# Alias for convenience
Set-Alias -Name pico -Value Send-ToPico -Scope Global -Option AllScope

"@

# Create profile directory if it doesn't exist
$ProfileDir = Split-Path -Parent $ProfilePath
if (-not (Test-Path $ProfileDir)) {
    New-Item -ItemType Directory -Path $ProfileDir -Force | Out-Null
    Write-Host "Created profile directory: $ProfileDir"
}

# Check if function already exists in profile
if (Test-Path $ProfilePath) {
    $ProfileContent = Get-Content $ProfilePath -Raw
    if ($ProfileContent -match "function Send-ToPico") {
        Write-Host "Send-ToPico function already exists in profile."
        Write-Host "Profile: $ProfilePath"
        exit 0
    }
}

# Add function to profile
Add-Content -Path $ProfilePath -Value $FunctionCode
Write-Host "Successfully added Send-ToPico function to PowerShell profile!"
Write-Host ""
Write-Host "Profile: $ProfilePath"
Write-Host ""
Write-Host "To use immediately, run: . `$PROFILE"
Write-Host ""
Write-Host "Usage:"
Write-Host "  Send-ToPico 'hello world'"
Write-Host "  Send-ToPico -Clipboard"
Write-Host "  pico 'hello world'          # Using alias"
Write-Host "  pico -Clipboard             # Using alias"
