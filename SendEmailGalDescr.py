import configparser
import datetime
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from ftplib import FTP

import config
import password


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'


# Получаем максимальную дату файлов на FTP
def getdateftp():
    print(f'{bcolors.HEADER}Start getdateftp')
    ftp = FTP(config.HOST)
    print(f"{bcolors.OKBLUE}Login to FTP: {config.HOST}, try goto {config.HOSTDir}. {ftp.login()}")

    files = ftp.mlsd(config.HOSTDir)  # Получаем файлы с датами с FTP
    _maxintdate = 0  # максимальная дата файла int в формате YYYYMMDD
    for file in files:
        _file_name = file[0]
        _file_type = file[1]['type']
        if _file_type == 'file':  # смотрим только файлы
            _timestamp = file[1]['modify']  # дата модификации файла
            _curdate = int(_timestamp[:8])  # int в формате YYYYMMDD
            if _maxintdate < _curdate:
                _maxintdate = _curdate
                print(f'{bcolors.OKBLUE}FileName = {_file_name}, FileType =  {_file_type}, {_curdate}')
    print(f'{bcolors.OKGREEN}getdateftp = {_maxintdate}')
    return _maxintdate

# Получаем дату файлов FTP последней обработки
def getdatelocal():
    print(f'{bcolors.HEADER}Start getdatelocal')
    if not os.path.exists(_file_locald_ini):
        create_config(20000101)

    if os.path.exists(_file_locald_ini):
        config = configparser.ConfigParser()
        config.read(_file_locald_ini)
        result = config.get("Settings", "LastUpdateDate")
    else:
        result = 20000101
    print(f'{bcolors.OKGREEN}getdatelocal = {result}')
    return int(result)

# Формируем текст сообщения e-mail
def CreateMsg(subject, message):
    print(f'{bcolors.HEADER}Start CreateMsg')
    e_mail_msg["From"] = _e_mail
    e_mail_msg["To"] = _e_mail
    e_mail_msg["Subject"] = subject
    e_mail_msg.attach(MIMEText(message, 'plain'))
    print(f'{bcolors.OKGREEN}CreateMsg = {e_mail_msg}')

# Отправляем письмо
def SendEMail():
    print(f'{bcolors.HEADER}Start SendEMail')
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(_e_mail, password.password)

    text = e_mail_msg.as_string()
    server.sendmail(_e_mail, _e_mail, text)
    server.quit()
    print(f'{bcolors.OKGREEN}SendEMail = to {_e_mail}')

# Создаем файл с поледней датой обработки locald.ini
def create_config(LastUpdateDate):
    print(f'{bcolors.HEADER}Start create_config')
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "LastUpdateDate", str(LastUpdateDate))
    with open(_file_locald_ini, "w") as config_file:
        config.write(config_file)
    print(f'{bcolors.OKGREEN}create_config = {_file_locald_ini},{config_file}')

# Обновляем файл с поледней датой обработки locald.ini
def update_config(LastUpdateDate):
    print(f'{bcolors.HEADER}Start update_config')
    config = configparser.ConfigParser()
    config.read(_file_locald_ini)
    config.set("Settings", "LastUpdateDate", str(LastUpdateDate))
    with open(_file_locald_ini, "w") as config_file:
        config.write(config_file)
    print(f'{bcolors.OKGREEN}update_config = {_file_locald_ini},{config_file}')

# Создаем set.bat для контроля загрузки описания патчей
def CreateSetBat(_value):
    print(f'{bcolors.HEADER}Start CreateSetBat Created\\update a configuration file: {_file_set_bat},to {_value}')
    with open(_file_set_bat, 'w', encoding='UTF8') as _file:
        _file.write(f'set download_start={str(_value).upper()}')


def main():
    _ftp_date = getdateftp()  # максимальная дата файла на FTP
    dt = datetime.datetime.strptime(str(_ftp_date), '%Y%m%d')
    _sftpdt = dt.strftime('%d %b %Y')

    _local_date = getdatelocal()  # получаем предыдущую дату из файла
    dt = datetime.datetime.strptime(str(_local_date), '%Y%m%d')
    _slocaldt = dt.strftime('%d %b %Y')

    _subject_email = "Update ftp.galaktika.ru"
    _message_email = f"Processed at {datetime.datetime.now().strftime('%d %b %Y, %H:%M')}.\nLast FTP date file update is {_sftpdt}.\nLocal file at {_slocaldt}.\n" \
                     f"Git: http://192.168.177.30/projects/id2600001/repository"
    if _ftp_date > _local_date:
        CreateSetBat(True)
        CreateMsg(_subject_email, _message_email)
        SendEMail()
        update_config(_ftp_date)
    else:
        CreateSetBat(False)


if __name__ == '__main__':
    _e_mail = "masygreen@gmail.com"  # the email where you sent the email
    _cur_dir = os.getcwd()
    _file_locald_ini = f'{_cur_dir}\\locald.ini'
    _file_set_bat = f'{_cur_dir}\\set.bat'
    e_mail_msg = MIMEMultipart()
    main()
