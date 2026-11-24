@echo off
title Toko Sparepart Laptop
cd /d "%~dp0"

:: Cek apakah python terpasang dan jalankan tanpa jendela konsol (pythonw)
where pythonw >nul 2>nul
if %ERRORLEVEL% EQU 0 (
    start "" pythonw main.py
) else (
    where python >nul 2>nul
    if %ERRORLEVEL% EQU 0 (
        start "" python main.py
    ) else (
        echo [ERROR] Python tidak ditemukan di sistem PATH!
        pause
    )
)
exit
