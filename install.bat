@echo off
setlocal

REM Supprimer l'ancien venv s'il existe
if exist "venv\" (
    echo Suppression de l'ancien environnement...
    rmdir /s /q venv
)

echo Creation de l'environnement virtuel...
python -m venv venv

echo Installation des dépendances...
call venv\Scripts\activate.bat
python.exe -m pip install --upgrade pip
pip install requests beautifulsoup4 lxml
pip install tqdm

echo Lancement de l'application...
call launch.bat

endlocal
pause