# Helper functions for colored output
function Write-Success($msg) { Write-Host $msg -ForegroundColor Green }
function Write-WarningMsg($msg) { Write-Host $msg -ForegroundColor Yellow }
function Write-ErrorMsg($msg) { Write-Host $msg -ForegroundColor Red }

# Set variables
$signToolName = "signtool.exe"
$signToolUrl = "https://aka.ms/SignTool" # Official Microsoft download link
$pythonScript = "run-gui_Qt6.py" # Change to your script name
$outputExe = "dist\run-gui_Qt6.exe" # Change to your output exe path

# Check for signtool.exe in current directory
if (-not (Test-Path ".\$signToolName")) {
    Write-WarningMsg "signtool.exe not found. Downloading..."
    Invoke-WebRequest -Uri $signToolUrl -OutFile $signToolName
    Write-Success "Downloaded signtool.exe"
} else {
    Write-Success "signtool.exe found."
}

# Build Python executable using PyInstaller
if (-not (Get-Command pyinstaller -ErrorAction SilentlyContinue)) {
    Write-WarningMsg "PyInstaller not found. Installing..."
    pip install pyinstaller
}
Write-WarningMsg "Building Python executable..."
python -m PyInstaller --onefile --windowed --icon "resources/icon.ico" --add-data "resources:resources" --add-data "BarBellWeights:BarBellWeights" $pythonScript

# Sign the executable
if (Test-Path $outputExe) {
    Write-WarningMsg "Signing the executable..."
    try {
        .\signtool.exe sign /a /fd SHA256 /tr http://timestamp.digicert.com /td SHA256 $outputExe
        Write-Success "Signing complete."
    } catch {
        Write-ErrorMsg "Signing failed with error:"
        Write-ErrorMsg $_.Exception.Message
    }
} else {
    Write-ErrorMsg "Executable not found: $outputExe"
}