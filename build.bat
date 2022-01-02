@echo off
rmdir build /s /q
rmdir dist /s

python.exe -OO -m PyInstaller ^
    --windowed ^
    --exclude-module=tkinter ^
    --exclude-module=tk ^
    --exclude-module=FixTk ^
    --exclude-module=_tkinter ^
    --exclude-module=Tkinter ^
    --exclude-module=tcl ^
    --add-data book-3-fill.ico;. ^
    --add-data add-circle-fill.svg;. ^
    --add-data book-3-fill.svg;. ^
    --add-data delete-bin-2-fill.svg;. ^
    --add-data information-fill.svg;. ^
    --add-data pencil-fill.svg;. ^
    --add-data search-fill.svg;. ^
    --add-data settings-5-fill.svg;. ^
    --add-data LICENSE;. ^
    schoolLibrarian.py

cd dist
powershell sleep 10
powershell Compress-Archive schoolLibrarian\* schoolLibrarian.zip