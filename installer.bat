@echo off
title niko
color 0B
cls
echo.
echo  ========================================================
echo   @holy.niko // PlayFab Spammer Installer
echo   https://discord.gg/MYa937g4wq
echo  ========================================================
echo.

where python >nul 2>nul
if %errorlevel% neq 0 (
    echo [!] Python not found. Install Python 3.10+ from https://www.python.org/downloads/
    echo     Make sure to check "Add python.exe to PATH".
    echo     @holy.niko - https://discord.gg/MYa937g4wq
    pause
    exit /b 1
)

echo [*] Python found:
python --version
py --version 2>nul
echo.
echo [*] Upgrading pip...
python -m pip install --upgrade pip
py -m pip install --upgrade pip 2>nul

echo.
echo [*] Installing requirements for both launchers (python + py)...
python -m pip install requests rich colorama pillow
py -m pip install requests rich colorama pillow 2>nul

if exist niko.png (
    if not exist niko.ico (
        echo [*] Building niko.ico from niko.png for the window icon...
        python -c "from PIL import Image; im=Image.open('niko.png'); im.save('niko.ico', sizes=[(16,16),(32,32),(48,48),(64,64),(128,128),(256,256)])"
    )
) else (
    echo [*] Tip: save your cat pic as niko.png in this folder, re-run installer for the window icon.
)

if not exist proxies.txt (
    echo [*] Creating proxies.txt (optional - auto-fetch is built-in^)...
    echo # optional: paste your own proxies here, one per line ip:port> proxies.txt
)

if %errorlevel% neq 0 (
    echo.
    echo [!] Install failed. Try running as administrator.
    echo     @holy.niko - https://discord.gg/MYa937g4wq
    pause
    exit /b 1
)

echo.
echo  ========================================================
echo   Done! Run with: python playfab_spammer.py
echo   (or: py playfab_spammer.py - both work now)
echo   @holy.niko - https://discord.gg/MYa937g4wq
echo  ========================================================
echo.
pause
