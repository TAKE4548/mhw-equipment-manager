# start.ps1
# Automates venv activation and Streamlit app startup.

$Port = 8501
$AppRunning = Get-NetTCPConnection -LocalPort $Port -State Listen -ErrorAction SilentlyContinue

if ($AppRunning) {
    Write-Host "Streamlit is already running on port $Port." -ForegroundColor Cyan
    exit 0
}

if (Test-Path ".venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Green
    . .venv\Scripts\Activate.ps1
    Write-Host "Starting Streamlit..." -ForegroundColor Green
    streamlit run app.py
} else {
    Write-Error "Virtual environment not found in '.venv'. Please run 'python -m venv .venv' and 'pip install -r requirements.txt' first."
}
