pyinstaller ^
--onefile ^
--clean ^
--noconfirm ^
--console ^
--name RerateDataLoader ^
--add-data "config.ini;." ^
--dispatch . ^
--paths . ^
fetch_main.py 

ren bin\bin/exe RerateDataLoader.exe

rmdir /s /q build
