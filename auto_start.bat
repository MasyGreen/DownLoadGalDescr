%~d0
cd "%~p0"
@call cls
@ECHO OFF

python.exe "SendEmailGalDescr.py"

rem Проверяем необходимость обработки
@ECHO START %~d0
SET download_start=True
if exist SET.BAT (
@ECHO EXIST SET.BAT
@call SET.BAT
)

@ECHO download_start = %download_start%

if %download_start% == TRUE (
ECHO START DOWNLOAD

python.exe "DownLoadGalDescr.py"
cd /D %cd%\Download\
@ECHO %cd%

set DD=%date:~0,2%
set MM=%date:~3,2%
set YYYY=%date:~6,4%
set DT=_%YYYY%%MM%%DD%

SET DEBUGDATE=%DT%

git add .
git commit -m "%DT%"
git push origin master
) else (
@ECHO NO DOWNLOAD
)                                                       	
rem pause