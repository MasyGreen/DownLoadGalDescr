%~d0
cd "%~p0"
@call cls
@ECHO OFF

python.exe "SendEmailGalDescr.py"

rem Проверяем необходимость обработки
@ECHO ***1N START PATH %~d0%~p0
SET download_start=True
if exist SET.BAT (
@ECHO ***2N EXIST SET.BAT
@call SET.BAT
)

@ECHO ***3N download_start = %download_start%

SET download_path=%~d0%~p0\Download\
@ECHO ***4N %download_path%

set DD=%date:~0,2%
set MM=%date:~3,2%
set YYYY=%date:~6,4%
set DT=_%YYYY%%MM%%DD%

SET DEBUGDATE=%DT%
@ECHO ***5N %DEBUGDATE%

if %download_start% == TRUE (
@ECHO ***6N START DOWNLOAD
python.exe "DownLoadGalDescr.py"
cd /D "%download_path%"
@ECHO ***7N START GIT

git add .
git commit -m "%DT%"
git push origin master
) else (
@ECHO ***8N NO DOWNLOAD
)                                                       	
rem pause