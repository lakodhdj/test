@echo off
REM E-Commerce Project - Quick Start Script for Windows

echo.
echo 🚀 E-Commerce Project - Быстрый запуск
echo ======================================
echo.

REM Проверка Python
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python не установлен
    exit /b 1
)

for /f "tokens=*" %%i in ('python --version') do set PYTHON_VER=%%i
echo ✅ Python найден: %PYTHON_VER%
echo.

REM Проверка файлов
echo 📁 Проверка файлов проекта...
set files_ok=0
set files_total=0

if exist "frontend\index.html" (
    echo   ✅ frontend\index.html
    set /a files_ok+=1
) else (
    echo   ❌ frontend\index.html
)
set /a files_total+=1

if exist "frontend\styles.css" (
    echo   ✅ frontend\styles.css
    set /a files_ok+=1
) else (
    echo   ❌ frontend\styles.css
)
set /a files_total+=1

if exist "frontend\main.js" (
    echo   ✅ frontend\main.js
    set /a files_ok+=1
) else (
    echo   ❌ frontend\main.js
)
set /a files_total+=1

if exist "backend\app\main.py" (
    echo   ✅ backend\app\main.py
    set /a files_ok+=1
) else (
    echo   ❌ backend\app\main.py
)
set /a files_total+=1

if exist "docker-compose.yml" (
    echo   ✅ docker-compose.yml
    set /a files_ok+=1
) else (
    echo   ❌ docker-compose.yml
)
set /a files_total+=1

echo.
echo ✅ Проверено: %files_ok%/%files_total% файлов
echo.

REM Меню выбора
:menu
echo Что вы хотите сделать?
echo.
echo   1) Запустить фронтенд локально ^(Python^)
echo   2) Запустить через Docker Compose
echo   3) Только посмотреть документацию
echo   4) Выход
echo.
set /p choice="Выберите опцию (1-4): "

if "%choice%"=="1" goto run_frontend
if "%choice%"=="2" goto run_docker
if "%choice%"=="3" goto show_docs
if "%choice%"=="4" goto exit
echo ❌ Неверный выбор
goto menu

:run_frontend
echo.
echo 🌐 Запуск фронтенда на http://localhost:8001
echo.
echo ⏳ Подождите несколько секунд...
echo.
cd frontend
python -m http.server 8001
cd ..
goto end

:run_docker
echo.
echo 🐳 Запуск Docker Compose...
echo.
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8001
echo API Docs: http://localhost:8000/docs
echo.
docker-compose up -d
echo.
echo ✅ Контейнеры запущены
echo.
echo Команды:
echo   docker-compose logs -f          (просмотр логов)
echo   docker-compose down             (остановка)
echo.
goto end

:show_docs
echo.
echo 📚 Документация:
echo.
echo 🔹 START_HERE.md - С чего начать
echo 🔹 QUICKSTART.md - Быстрый старт (5 минут)
echo 🔹 PROJECT_OVERVIEW.md - Полная информация
echo 🔹 FINAL_CHECKLIST.md - Контрольный список
echo.
echo 🔹 frontend\README.md - Документация фронтенда
echo 🔹 frontend\FEATURES.md - Список всех функций
echo 🔹 frontend\INDEX.md - Индекс компонентов
echo.
echo Все файлы находятся в текущей папке.
echo.
pause
goto end

:exit
echo До свидания! 👋
pause
exit /b 0

:end
pause
