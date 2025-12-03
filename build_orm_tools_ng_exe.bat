@echo off
echo ================================================
echo ORM Maps Tools NG - EXE Builder mit JSON-Support
echo ================================================
echo.

REM Prüfe ob Virtual Environment existiert
if exist ".venv\Scripts\python.exe" (
    echo Virtual Environment gefunden.
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    echo Kein Virtual Environment gefunden, verwende System-Python.
    set PYTHON_CMD=python
)

REM Prüfe ob PyInstaller installiert ist
%PYTHON_CMD% -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo PyInstaller nicht gefunden. Installiere PyInstaller
    %PYTHON_CMD% -m pip install pyinstaller
    echo.
)

REM Prüfe ob Pillow installiert ist
%PYTHON_CMD% -m pip show Pillow >nul 2>&1
if errorlevel 1 (
    echo Pillow nicht gefunden. Installiere Pillow
    %PYTHON_CMD% -m pip install Pillow
    echo.
)

REM Prüfe ob NumPy installiert ist (optional für Histogramme)
%PYTHON_CMD% -m pip show numpy >nul 2>&1
if errorlevel 1 (
    echo NumPy nicht gefunden. Installiere NumPy (optional)
    %PYTHON_CMD% -m pip install numpy
    echo.
)

echo Erstelle EXE-Datei für ORM Maps Tools NG
echo.

REM Erstelle sauberes Build-Verzeichnis
if exist build rmdir /s /q build
if exist dist\ORM-Maps-Tools-NG rmdir /s /q dist\ORM-Maps-Tools-NG

REM Build mit PyInstaller (JSON wird als Daten-Datei hinzugefuegt)
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "ORM-Maps-Tools-NG" --add-data "texture_suffixes.json;." --add-data "orm-maps-tools-ng-64.png;." --add-data "orm-maps-tools-ng-128.png;." --icon "orm-maps-tools-ng-64.png" --clean orm-maps-tools-ng.py

if errorlevel 1 (
    echo.
    echo ================================================
    echo FEHLER: Build fehlgeschlagen!
    echo ================================================
    pause
    exit /b 1
)

echo.
echo Kopiere Dokumentation
mkdir dist\ORM-Maps-Tools-NG 2>nul
move dist\ORM-Maps-Tools-NG.exe dist\ORM-Maps-Tools-NG\ >nul

REM Kopiere JSON und Dokumentation
copy texture_suffixes.json dist\ORM-Maps-Tools-NG\ >nul
copy README.md dist\ORM-Maps-Tools-NG\ >nul
copy FEATURES_NG.md dist\ORM-Maps-Tools-NG\ >nul
copy QUICKSTART_NG.md dist\ORM-Maps-Tools-NG\ >nul
copy CHANGELOG_NG.md dist\ORM-Maps-Tools-NG\ >nul
copy TEXTURE_SUFFIXES_README.md dist\ORM-Maps-Tools-NG\ >nul
copy BUILD_WITH_JSON.md dist\ORM-Maps-Tools-NG\ >nul
copy LICENSE dist\ORM-Maps-Tools-NG\ >nul 2>nul

echo.
echo ================================================
echo Build erfolgreich abgeschlossen!
echo ================================================
echo.
echo Erstellte Dateien:
echo   dist\ORM-Maps-Tools-NG\ORM-Maps-Tools-NG.exe
echo   dist\ORM-Maps-Tools-NG\texture_suffixes.json
echo   dist\ORM-Maps-Tools-NG\*.md (Dokumentation)
echo.
echo WICHTIG:
echo - Die texture_suffixes.json kann nach dem Build bearbeitet werden
echo - Keine Neu-Kompilierung erforderlich bei Suffix-Aenderungen
echo - Siehe TEXTURE_SUFFIXES_README.md fuer Details
echo.
echo Sie koennen den Ordner 'dist\ORM-Maps-Tools-NG' jetzt verteilen.
echo Die EXE benoetigt keine Python-Installation.
echo.
pause
