#!/bin/bash
# E-Commerce Project - Quick Start Script

echo "🚀 E-Commerce Project - Быстрый запуск"
echo "======================================"
echo ""

# Проверка Python
if ! command -v python &> /dev/null; then
    echo "❌ Python не установлен"
    exit 1
fi

echo "✅ Python найден: $(python --version)"
echo ""

# Проверка структуры проекта
echo "📁 Проверка файлов проекта..."
files_ok=0
files_total=0

check_file() {
    files_total=$((files_total + 1))
    if [ -f "$1" ]; then
        echo "  ✅ $1"
        files_ok=$((files_ok + 1))
    else
        echo "  ❌ $1"
    fi
}

check_file "frontend/index.html"
check_file "frontend/styles.css"
check_file "frontend/main.js"
check_file "backend/app/main.py"
check_file "docker-compose.yml"

echo ""
echo "✅ Проверено: $files_ok/$files_total файлов"
echo ""

# Выбор действия
echo "Что вы хотите сделать?"
echo "1) Запустить фронтенд локально (Python)"
echo "2) Запустить через Docker Compose"
echo "3) Только посмотреть документацию"
echo "4) Выход"
echo ""
read -p "Выберите опцию (1-4): " choice

case $choice in
    1)
        echo ""
        echo "🌐 Запуск фронтенда на http://localhost:8001"
        echo ""
        cd frontend
        python -m http.server 8001
        ;;
    2)
        echo ""
        echo "🐳 Запуск Docker Compose..."
        echo "Backend: http://localhost:8000"
        echo "Frontend: http://localhost:8001"
        echo "API Docs: http://localhost:8000/docs"
        echo ""
        docker-compose up -d
        echo ""
        echo "✅ Контейнеры запущены"
        echo "Логи: docker-compose logs -f"
        echo "Остановка: docker-compose down"
        ;;
    3)
        echo ""
        echo "📚 Документация:"
        echo ""
        echo "🔹 START_HERE.md - С чего начать"
        echo "🔹 QUICKSTART.md - Быстрый старт (5 минут)"
        echo "🔹 PROJECT_OVERVIEW.md - Полная информация"
        echo "🔹 FINAL_CHECKLIST.md - Контрольный список"
        echo ""
        echo "🔹 frontend/README.md - Документация фронтенда"
        echo "🔹 frontend/FEATURES.md - Список всех функций"
        echo "🔹 frontend/INDEX.md - Индекс компонентов"
        echo ""
        ;;
    4)
        echo "До свидания! 👋"
        exit 0
        ;;
    *)
        echo "❌ Неверный выбор"
        exit 1
        ;;
esac
