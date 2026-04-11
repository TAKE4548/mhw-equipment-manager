@echo off
REM start.bat
REM Wrapper for start.ps1

powershell -ExecutionPolicy Bypass -File "./start.ps1"
if %ERRORLEVEL% NEQ 0 (
    echo An error occurred while starting the application.
    pause
)
