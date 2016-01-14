@echo OFF&setlocal
REM Update resource file
for %%i in ("%~dp0") do set "folder=%%~fi"
set RES="%folder%"
echo Updating resource file: %res%\res\res.qrc...
set COMPILER=pyrcc4
%COMPILER% "%RES%\res\res.qrc" -o "%RES%\res_rc.py"
echo Updated 'res_rc.py'
pause