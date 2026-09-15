@echo off
REM Script de build Android pour Elderia avec Flet

echo ========================================
echo Build Android - Les Chroniques d'Elderia
echo ========================================
echo.

REM Vérifier les dépendances
echo Verification des dependances...
pip install flet --upgrade
pip install python-for-android

echo.
echo Lancement du build Android...
echo.

REM Build avec Flet pour Android
flet build android

echo.
echo ========================================
echo Build termine!
echo ========================================
echo.
echo L'APK se trouve dans le dossier: build\android\app\build\outputs\apk\debug\
echo.
pause