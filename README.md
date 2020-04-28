# Назначение
Выкачиваем описание патчей с ftp.galaktika.ru

# Настройки config.py

* WorkFolder - путь к каталогу загрзуки
* HOST(ftp.galaktika.ru) - параметры FTP
* HOSTDir(pub/support/galaktika/bug_fix/GAL910/DESCRIPTIONS) - каталог с TXT файлами описаний

# Алгоритм
* Составляем список файлов на FTP
* Удаляются все файлы с '.txt' из WorkFolder
* Скачиваем все файлы с FTP, убирая из имени числа и добавляя к расширению '_win1251'
* Перекодируем все файлы с '_win1251' из WorkFolder из win1251 в UTF-8, в новом имени файла убираем '_win1251'
* Удаляем не перекодированные файлы

# Установка
git clone https://github.com/MasyGreen/DownLoadGalDescr.git
