@echo off
setlocal
py -m pip install -r requirements.txt pyinstaller
if errorlevel 1 exit /b 1
py -m PyInstaller --noconfirm --clean --onefile --windowed --name PDFOrganizer main.py
if errorlevel 1 exit /b 1
echo Finished: dist\PDFOrganizer.exe
