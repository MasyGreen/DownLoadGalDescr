set DD=%date:~0,2%
set MM=%date:~3,2%
set YYYY=%date:~6,4%
set Hour=%time:~0,2%
set Min=%time:~3,2%
set DT=%YYYY%%MM%%DD%_%Hour%%Min%
SET DEBUGDATE=%DT%
SET PVERSION=Edit_BAT_File

git add .
git commit -m "%PVERSION%_%DT%"
git tag -a %PVERSION%_%DT% -m "%PVERSION%_%DT%"
git push origin master
git push --tags
pause