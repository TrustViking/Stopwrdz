
:: This command disables the display of executed commands in the command-line window.
:: The @ symbol before the command means that the 'echo off' command itself will not be displayed.
@REM @echo off

:: This command creates a copy of the current environment variables and
:: sets new local variables for this batch file.
:: Changes made in this batch file will not affect
:: global environment variables.
setlocal


:: Passing environment variables and command-line arguments to the Python script
cd D:\bots\swords_terminal\
python start_swords_terminal.py


:: Pause to view the output
pause

endlocal
