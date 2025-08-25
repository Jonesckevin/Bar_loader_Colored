# Check and install pip
if (-not (Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "pip could not be found, installing..."
    python -m ensurepip --upgrade
}
else {
    Write-Host "pip is already installed"
}

# Check, install, and create a virtual environment
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "Python is not installed. Please install Python 3.x and try again."
    exit 1
}

if (-not (Test-Path -Path "./.venv")) {
    Write-Host "Creating virtual environment..."
    python -m venv .venv
}
else {
    Write-Host "Virtual environment already exists"
}

# Activate the virtual environment
Write-Host "Activating virtual environment..."
& .\.venv\Scripts\Activate.ps1

# Check and install requirements
if (-not (Test-Path -Path "./requirements.txt")) {
    Write-Host "requirements.txt not found, please check the directory"
    exit 1
}

Write-Host "Installing requirements..."
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "Failed to install requirements, please check the error messages above."
    exit 1
}
Write-Host "Setup complete!"
