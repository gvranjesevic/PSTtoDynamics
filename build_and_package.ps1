# PowerShell Build & Package Script for PSTtoDynamics
# Cleans, builds with PyInstaller, and launches NSIS installer

# 1. Clean previous builds
Write-Host "Cleaning previous build artifacts..."
Remove-Item -Recurse -Force build, dist, main_window.spec -ErrorAction SilentlyContinue

# 2. Run PyInstaller
Write-Host "Building executable with PyInstaller..."
pyinstaller --noconfirm --onefile --windowed --icon=gui/resources/app_icon.ico --add-data "gui/themes;gui/themes" --add-data "gui/resources;gui/resources" gui/main_window.py

if (!(Test-Path dist/main_window.exe)) {
    Write-Error "Build failed: main_window.exe not found."
    exit 1
}

# 3. Launch NSIS to create installer
Write-Host "Launching NSIS to create Windows installer..."
$nsisScript = "installer.nsi"
if (!(Test-Path $nsisScript)) {
    Write-Error "NSIS script not found: $nsisScript"
    exit 1
}

# Assumes makensis.exe is in PATH
$makensis = "makensis.exe"
$makensisPath = Get-Command $makensis -ErrorAction SilentlyContinue
if (!$makensisPath) {
    Write-Error "makensis.exe (NSIS) not found in PATH. Please install NSIS and add to PATH."
    exit 1
}

& $makensis $nsisScript

if ($LASTEXITCODE -eq 0) {
    Write-Host "Installer created successfully!"
} else {
    Write-Error "NSIS installer creation failed."
    exit 1
} 