# Send-ToPico.ps1
# PowerShell wrapper for sending text to Raspberry Pi Pico 2 W via WiFi
# Usage: Send-ToPico "hello world"
#        Send-ToPico -Clipboard

param(
    [Parameter(Position=0, Mandatory=$false)]
    [string]$Text,

    [Parameter(Mandatory=$false)]
    [switch]$Clipboard
)

# Get the project directory where send_wifi.py is located
$ProjectDir = "C:\projects\raspberry-pico-2-hid"

# Change to project directory
Push-Location $ProjectDir

try {
    if ($Clipboard) {
        # Send clipboard contents
        python send_wifi.py --clip
    }
    elseif ($Text) {
        # Send provided text
        python send_wifi.py $Text
    }
    else {
        Write-Host "Usage: Send-ToPico 'text to send'"
        Write-Host "       Send-ToPico -Clipboard"
        exit 1
    }
}
finally {
    Pop-Location
}
