set DD=%date:~0,2%
set MM=%date:~3,2%
set YYYY=%date:~6,4%
set DT=_%YYYY%%MM%%DD%

SET DEBUGDATE=%DT%

git add .
git commit -m "%DT%"
git push origin master                                                        	
pause