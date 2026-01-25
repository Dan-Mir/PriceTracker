@echo off
REM Script batch per eseguire lo scraping Eurospin
REM Può essere usato con Windows Task Scheduler

echo ========================================
echo    EUROSPIN PRICE SCRAPER
echo ========================================
echo.

REM Cambia directory al progetto
cd /d "%~dp0.."

REM Attiva virtual environment
echo Attivazione virtual environment...
call .venv\Scripts\activate.bat

REM Cambia nella cartella src
cd src

REM Esegui lo script
echo.
echo Esecuzione scraping...
echo.
python main.py

REM Log risultato
if %ERRORLEVEL% EQU 0 (
    echo.
    echo [%date% %time%] Scraping completato con successo >> ..\scraping.log
    echo ========================================
    echo    COMPLETATO CON SUCCESSO
    echo ========================================
) else (
    echo.
    echo [%date% %time%] Errore durante lo scraping >> ..\scraping.log
    echo ========================================
    echo    ERRORE
    echo ========================================
)

REM Pausa solo se eseguito manualmente (non da Task Scheduler)
if "%1"=="" pause
