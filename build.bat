@echo off
setlocal
cd /d "%~dp0"
title Building YT-DLP GUI.exe

echo ==============================================
echo   Building YT-DLP GUI.exe
echo ==============================================
echo.

set PY=python
%PY% --version >nul 2>&1
if errorlevel 1 (
    set PY=py
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Python is not installed.
        echo Get it from https://www.python.org/downloads/
        echo and tick "Add python.exe to PATH" during setup. Then run this again.
        echo.
        pause
        exit /b 1
    )
)

echo [1/2] Installing build tools...
%PY% -m pip install --upgrade pip pyinstaller -r requirements.txt
if errorlevel 1 goto :fail

echo.
echo [2/2] Building the app (this takes a minute)...
%PY% -m PyInstaller --noconfirm --clean --onefile --windowed ^
    --name "YT-DLP GUI" ^
    --icon "yt-dlp-gui.ico" ^
    --add-data "yt-dlp-gui.ico;." ^
    --collect-all customtkinter ^
    yt-dlp-gui.pyw
if errorlevel 1 goto :fail

echo.
echo ==============================================
echo   Done!  Your app is here:  dist\YT-DLP GUI.exe
echo   Put it anywhere and double-click it.
echo   The first launch sets up yt-dlp, ffmpeg and deno for you.
echo ==============================================
pause
exit /b 0

:fail
echo.
echo Something went wrong. Scroll up to see the error.
pause
exit /b 1
