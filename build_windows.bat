@echo off
setlocal
python -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1
python -m PyInstaller --noconfirm --clean --onedir --windowed --name PDF_Organizer main.py
if errorlevel 1 exit /b 1
echo Finished: dist\PDF_Organizer.exe
