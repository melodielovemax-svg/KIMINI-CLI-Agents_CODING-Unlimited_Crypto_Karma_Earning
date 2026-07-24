@echo off
title Melodie-Kimini Ultimate Edition Installer
color 0A
echo.
echo  ================================================
echo   Melodie-Kimini Ultimate Edition - Installer
echo   Version 3.1.0 - Build 2026.07.23
echo  ================================================
echo.
echo  Installing to: %USERPROFILE%\Melodie-Kimini
echo.

set INSTALL_DIR=%USERPROFILE%\Melodie-Kimini
if not exist "%INSTALL_DIR%" mkdir "%INSTALL_DIR%"
if not exist "%INSTALL_DIR%\data" mkdir "%INSTALL_DIR%\data"
if not exist "%INSTALL_DIR%\logs" mkdir "%INSTALL_DIR%\logs"

copy /Y "%~dp0Melodie-Kimini.exe" "%INSTALL_DIR%\" >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Melodie-Kimini.exe not found in installer directory.
    pause
    exit /b 1
)

echo [OK] Melodie-Kimini.exe installed.

(
    echo @echo off
    echo title Melodie-Kimini
    echo "%INSTALL_DIR%\Melodie-Kimini.exe" %%*
    echo pause
) > "%INSTALL_DIR%\Kimini.bat"

echo [OK] Kimini.bat launcher created.

(
    echo @echo off
    echo title Kimini Chat
    echo "%INSTALL_DIR%\Melodie-Kimini.exe" chat
    echo pause
) > "%INSTALL_DIR%\Kimini-Chat.bat"

echo [OK] Kimini-Chat.bat launcher created.

(
    echo @echo off
    echo title Kimini Status
    echo "%INSTALL_DIR%\Melodie-Kimini.exe" status
    echo pause
) > "%INSTALL_DIR%\Kimini-Status.bat"

echo [OK] Kimini-Status.bat launcher created.

setx MELODIE_HOME "%INSTALL_DIR%" >nul 2>&1
echo [OK] MELODIE_HOME environment variable set.

echo.
echo  ================================================
echo   Installation Complete!
echo  ================================================
echo.
echo  Installed to: %INSTALL_DIR%
echo.
echo  Launchers:
echo    Kimini.bat        - Full CLI
echo    Kimini-Chat.bat   - Interactive Chat
echo    Kimini-Status.bat - Platform Status
echo.
echo  Commands:
echo    Melodie-Kimini status
echo    Melodie-Kimini models
echo    Melodie-Kimini chat
echo    Melodie-Kimini karma "teach children"
echo    Melodie-Kimini wallet
echo    Melodie-Kimini mine
echo    Melodie-Kimini benchmark
echo.
echo  Press any key to finish...
pause >nul
