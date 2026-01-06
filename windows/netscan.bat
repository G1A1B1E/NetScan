@echo off
:: NetScan Windows Launcher
:: This batch file launches the PowerShell version of NetScan

setlocal enabledelayedexpansion

:: Get the directory where this script is located
set "SCRIPT_DIR=%~dp0"

:: Check if PowerShell is available
where powershell >nul 2>&1
if %errorlevel% neq 0 (
    echo Error: PowerShell is not installed or not in PATH
    echo Please install PowerShell or use the PowerShell script directly.
    pause
    exit /b 1
)

:: Pass all arguments to PowerShell script
powershell -ExecutionPolicy Bypass -File "%SCRIPT_DIR%netscan.ps1" %*
