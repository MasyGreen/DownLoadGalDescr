import os
import threading
import urllib
from ftplib import FTP
import re
from ftplib import FTP
from queue import Queue
from threading import Thread

from chardet import detect

import config


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# ---------------------------------------------------------
class DownloadFromFTP(threading.Thread):
    """Потоковый загрузчик файлов"""

    def __init__(self, queue):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        """Запуск потока"""
        while True:
            # Получаем url из очереди
            params = self.queue.get()

            # Скачиваем файл
            self.FunDownloadFromFTP(params)

            # Отправляем сигнал о том, что задача завершена
            self.queue.task_done()

    def FunDownloadFromFTP(self, params):
        print(f'{bcolors.OKBLUE}FTP. Download :{params.get("ftp_file_name")}')

        # """Connect to an FTP server and bring down files to a local directory"""
        try:
            ftp = FTP(config.HOST)
            print(f"{bcolors.OKBLUE}FTP. Login to FTP: {config.HOST}, try goto {config.HOSTDir}. {ftp.login()}")
            ftp.cwd(config.HOSTDir)
            try:
                # open a the local file
                with open(f'{config.WorkFolder}\\{params.get("local_file_name")}_win1251', 'wb') as _local_file:
                    ftp.retrbinary('RETR ' + params.get("ftp_file_name"), _local_file.write)
                print(f'{bcolors.OKGREEN}   FTP. {params.get("ftp_file_name")}>>>{params.get("local_file_name")}')
            except:
                print(f"{bcolors.FAIL}  FTP: Connection Error {config.HOST}")
        except:
            print(f"{bcolors.FAIL}  FTP: Couldn't find server {config.HOST}")
        ftp.close()  # Close FTP connection
        ftp = None


# --------------------------------------------------------
class DecodeLocalFile(threading.Thread):
    """Потоковый загрузчик файлов"""

    def __init__(self, queue):
        """Инициализация потока"""
        threading.Thread.__init__(self)
        self.queue = queue

    def run(self):
        """Запуск потока"""
        while True:
            # Получаем url из очереди
            params = self.queue.get()

            # Скачиваем файл
            self.FunDecodeLocalFile(params)

            # Отправляем сигнал о том, что задача завершена
            self.queue.task_done()

    def FunDecodeLocalFile(self, params):
        _codec_page = get_encoding_type(params.get("path_file_from"))  # получаем кодировку
        print(f'{bcolors.OKBLUE}File: {params.get("path_file_from")}, codepage = {_codec_page}')
        try:
            decode_test = ''
            with open(params.get("path_file_from"), 'r', encoding='windows-1251') as fr:
                for code_text in fr.readlines():
                    if code_text[0] != '№':
                        decode_test += code_text[:-1] + '\n'  # \r\n
            with open(params.get("path_file_to"), 'w', encoding='UTF-8') as fw:
                fw.write(decode_test)

            print(f'{bcolors.OKGREEN}   {params.get("path_file_from")}>>>{params.get("path_file_to")}')
        except:
            print(f'{bcolors.FAIL}  Ошибка файла: {params.get("path_file_from")}')


# --------------------------------------------------------
# Получаем список файлов на FTP
def getftplistfile():
    ListFTPFile = []
    ftp = FTP(config.HOST)
    print(f"{bcolors.OKBLUE}Login to FTP: {config.HOST}, try goto {config.HOSTDir}. {ftp.login()}")
    ftp.cwd(config.HOSTDir)
    list_ftp_file = ftp.nlst()
    for ftp_file in list_ftp_file:  # кореневые каталоги
        if ftp_file.find('.txt') != -1:
            # Чтобы свернуть исторю файла убераем из его мени версию
            local_file = re.sub('_(\d)+\.', '.',
                                ftp_file)  # регулярное выражение '_'+ 'несколько цифр' + '.'

            _row = {"ftp_file_path": f'{config.HOST}/{config.HOSTDir}/{ftp_file}', "ftp_file_name": ftp_file,
                    "local_file_name": local_file}
            ListFTPFile.append(_row)
            print(f"{bcolors.OKGREEN}   ftp: {_row}")
            ftp.close()
    return ListFTPFile


# --------------------------------------------------------
# Получаем кодировку файла
def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    try:
        return detect(rawdata)['encoding']
    except:
        return ''


# --------------------------------------------------------


#  ------------------------------------------------------------------------
def main():
    _useConv = {'IBM866', 'windows-1251', 'ascii', 'MacCyrillic'}

    if _useDowloadFTP:
        # удалить все файлы, проще выкачать заново
        print(f'{bcolors.HEADER}Delete old file')
        for path, subdirs, files in os.walk(config.WorkFolder):
            for _local_file in files:
                if _local_file.find(".txt") != -1:
                    print(f'{bcolors.OKBLUE}    Удалить: {path}{_local_file}')
                    os.remove(os.path.join(path, _local_file).lower())

        print(f'{bcolors.HEADER}Starting create download list')
        ListParamsFTP = getftplistfile()  # список файлов с FTP

        # скачиваем FTP
        print(f'{bcolors.HEADER}Starting download FTP file')
        queue_ftpfile = Queue()
        # Запускаем потом и очередь
        for i in range(10):
            t = DownloadFromFTP(queue_ftpfile)
            t.setDaemon(True)
            t.start()
        # Даем очереди нужные нам ссылки для скачивания
        for _el in ListParamsFTP:
            queue_ftpfile.put(_el)

        # Ждем завершения работы очереди
        queue_ftpfile.join()

    if _useDecodeFile:
        print(f'{bcolors.HEADER}Starting get list encode file')
        ListParamsDecodeFile = []  # Файлы для перкодировки
        for path, subdirs, files in os.walk(config.WorkFolder):
            for _local_file in files:
                if _local_file.find("_win1251") != -1:
                    row = {"path": path, "filename": _local_file, "path_file_from": f'{path}{_local_file}',
                           "path_file_to": f'{path}{_local_file.replace("_win1251", "")}'}
                    ListParamsDecodeFile.append(row)
                    print(row)
        print(f'{bcolors.HEADER}Starting encode file')
        queue_decodefile = Queue()
        # Запускаем потом и очередь
        for i in range(10):
            t = DecodeLocalFile(queue_decodefile)
            t.setDaemon(True)
            t.start()
        # Даем очереди нужные нам ссылки для скачивания
        for _el in ListParamsDecodeFile:
            queue_decodefile.put(_el)

        # Ждем завершения работы очереди
        queue_decodefile.join()

        # Удаляем не перекодированные файлы
        if _UseDeleteFileAfter:
            for _el in ListParamsDecodeFile:
                os.remove(os.path.join(_el.get("path"), _el.get("filename")).lower())


#  ------------------------------------------------------------------------
if __name__ == "__main__":
    _useDowloadFTP = True  # скачивать файлы с FTP
    _useDecodeFile = True  # перекодировать файлы
    _UseDeleteFileAfter = True  # удалять файлы
    main()
