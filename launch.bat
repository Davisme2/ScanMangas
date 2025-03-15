@echo off
REM === ScanMangas Launcher ===
setlocal

REM 1. Vérifier l'environnement virtuel
if not exist "venv\" (
    echo Environnement virtuel introuvable!
    echo Exécutez d'abord install.bat
    pause
    exit /b 1
)

REM 2. Activer venv et lancer l'application
call venv\Scripts\activate.bat
python -x "%~dp0launch.py" %*

REM 3. Pause si erreur
if errorlevel 1 (
    echo Une erreur est survenue lors de l'exécution
    pause
)