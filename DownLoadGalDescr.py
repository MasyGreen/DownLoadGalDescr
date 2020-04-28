import os
from ftplib import FTP
import re
from ftplib import FTP

from chardet import detect

import config


# Получаем список файлов на FTP
def getftplistfile():
    ftp = FTP(config.HOST)
    print(f"Login to FTP: {config.HOST}, try goto {config.HOSTDir}")
    print(ftp.login())
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
            print(f"  ftp: {_row}")
            ftp.close()

def get_encoding_type(file):
    with open(file, 'rb') as f:
        rawdata = f.read()
    try:
        return detect(rawdata)['encoding']
    except:
        return ''


# преобразовать кодировку файла
def correctSubtitleEncoding(file_from, file_to, encoding_from, encoding_to='UTF-8'):
    with open(file_from, 'r', encoding=encoding_from) as fr:
        with open(file_to, 'w', encoding=encoding_to) as fw:
            for line in fr:
                fw.write(line[:-1] + '\n')  # \r\n


def DownloadFTPFile(params):
    print(f'Download :{params.get("ftp_file_name")}')

    # """Connect to an FTP server and bring down files to a local directory"""
    try:
        ftp = FTP(config.HOST)
        print(f"Login to FTP: {config.HOST}, try goto {config.HOSTDir}")
        print(ftp.login())
        ftp.cwd(config.HOSTDir)
        try:
            # open a the local file
            with open(f'{config.WorkFolder}\\{params.get("local_file_name")}_win1251', 'wb') as _local_file:
                ftp.retrbinary('RETR ' + params.get("ftp_file_name"), _local_file.write)
        except:
            print(f"Connection Error")
    except:
        print("Couldn't find server")
    ftp.close()  # Close FTP connection
    ftp = None


#  ------------------------------------------------------------------------
def main():
    _useConv = {'IBM866', 'windows-1251', 'ascii', 'MacCyrillic'}

    print('*Starting create download list')
    getftplistfile()

    # удалить все файлы, проще выкачать заново
    print('*Delete unused file')
    for path, subdirs, files in os.walk(config.WorkFolder):
        for _local_file in files:
            if _local_file.find(".txt") != -1:
                print(f'Удалить: {path}{_local_file}')
                os.remove(os.path.join(path, _local_file).lower())
    # скачиваем FTP
    print('*Starting download FTP file')
    for ftp_el in ListFTPFile:
        DownloadFTPFile(ftp_el)
    print('*Starting get list encode file')
    LocalFile = []
    for path, subdirs, files in os.walk(config.WorkFolder):
        for _local_file in files:
            if _local_file.find("_win1251") != -1:
                row = {"path": path, "filename": _local_file, "file_code": f'{path}{_local_file}',
                       "file_decode": f'{path}{_local_file.replace("_win1251", "")}'}
                LocalFile.append(row)
                print(row)
    print('*Starting encode file')
    for _file in LocalFile:
        _codec_page = get_encoding_type(_file.get("file_code"))  # получаем кодировку
        print(f'------ File: {_file.get("file_code")}, codepage = {_codec_page} --------')
        correctSubtitleEncoding(_file.get("file_code"), _file.get("file_decode"),
                                'windows-1251')  # конвертируем в UTF-8 'cp866'
        os.remove(os.path.join(_file.get("path"), _file.get("filename")).lower())

#  ------------------------------------------------------------------------
if __name__ == "__main__":
    ListFTPFile = []  # список файлов с FTP
    main()
