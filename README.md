# Назначение
Проверка выхода новых патчей, с оповещением по e-mail.
Выкачиваем описание патчей с ftp.galaktika.ru

# Настройки config.py

* HOST(ftp.galaktika.ru) - параметры FTP
* HOSTDir(pub/support/galaktika/bug_fix/GAL910/DESCRIPTIONS) - каталог с TXT файлами описаний
* Пароль к почте password.py (исключен из проекта схема в passwordr.py)


# Алгоритм
## SendEmailGalDescr
* Дата из FTP сохраняется в locald.ini
* При настройке .bat, для планировщика заданий, необходимо переходить в рабочую папку
* Формирует файл **locald.ini** с последей датой из FTP
* Формирует файл **set.bat** с признаком необходимости скачивания обновлений

## DownLoadGalDescr
* Составляем список файлов на FTP
* Файлы переводим в верхний регистр т.к. Галактика постоянно меняет его
* Удаляются все файлы с '.txt' из WorkFolder
* Скачиваем все файлы с FTP, убирая из имени числа и добавляя к расширению '_win1251'
* Перекодируем все файлы с '_win1251' из WorkFolder из win1251 в UTF-8, в новом имени файла убираем '_win1251'
* Удаляем не перекодированные файлы

# Установка
git clone https://github.com/MasyGreen/DownLoadGalDescr.git

## Известные проблемы
* На FTP могут быть 2 файла разных версий, загрузится случайный

# BAT
```
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
```
