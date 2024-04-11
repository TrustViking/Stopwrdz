@echo off
chcp 65001

@REM Выводим аргумент переданный скрипту
@REM echo Переданный в скрипт путь к файлу: %~1
@REM pause

rem Проверка наличия переданного аргумента (пути к файлу)
if "%~1"=="" (
    echo File path was not passed
    pause
    exit /b
)

@REM Устанавливаем переменную путь к файлу
set "file_path=%~1"
@REM echo Путь к файлу титров (file_path): %file_path%
@REM pause

@REM  Получение пути к директории из переданного пути к файлу
::set "dir_path=%~dp1"
::echo Путь к директории, где хранится файл (dir_path): %dir_path%
::pause

@REM  Добавление пути к папке "title"
::set "output_dir=%dir_path%title"
::echo Путь к папке для вывода (output_dir): %output_dir%
::pause

@REM  Замена обратных слешей в пути к файлу на двойные обратные слеши (экранирование для передачи через командную строку)
set "file_path=%file_path:\=\\%"
@REM echo Путь к файлу после замены обратных слешей (file_path): %file_path%
@REM pause

@REM set "output_dir=%output_dir:\=\\%"
::echo Путь к папке для вывода после замены обратных слешей (output_dir): %output_dir%
::pause

@REM  Формирование команды с подстановкой пути к файлу и папки для вывода в указанный вами шаблон
:: C:\Users\arago\AppData\Local\Programs\Python\Python311\Scripts\whisper.exe --word_timestamps True --max_line_width 30 --max_line_count 1 --model medium --output_dir "%output_dir%" --output_format srt --task transcribe "%file_path%"
@REM set "arguments=--word_timestamps True --max_line_width 30 --max_line_count 1 --model medium --output_dir "%output_dir%" --output_format srt --task transcribe "%file_path%""

::echo Аргументы к whisper.exe: %arguments%
::pause

@REM C:\Users\arago\AppData\Local\Programs\Python\Python311\Scripts\whisper.exe %file_path%
@REM "D:\scripts\swords\swords.py"

cd D:\scripts\swords\
python swords.py %file_path%

pause

