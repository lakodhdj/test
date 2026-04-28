#!/usr/bin/env python3
"""
Скрипт для проверки структуры и готовности фронтенда
"""

import os
import sys
from pathlib import Path

class FrontendChecker:
    def __init__(self):
        self.root = Path(__file__).parent.resolve()
        self.frontend = self.root / 'frontend'
        self.results = []

    def check_file_exists(self, path, description):
        """Проверить существование файла"""
        exists = path.exists()
        status = "✅" if exists else "❌"
        size = f" ({path.stat().st_size / 1024:.1f} KB)" if exists else ""
        print(f"{status} {description}{size}")
        self.results.append(exists)
        return exists

    def check_content(self, path, keyword, description):
        """Проверить наличие содержимого в файле"""
        if not path.exists():
            print(f"❌ {description} - файл не найден")
            self.results.append(False)
            return False
        
        with open(path, 'r', encoding='utf-8') as f:
            content = f.read()
            found = keyword in content
        
        status = "✅" if found else "❌"
        print(f"{status} {description}")
        self.results.append(found)
        return found

    def check_lines(self, path, min_lines, description):
        """Проверить количество строк в файле"""
        if not path.exists():
            print(f"❌ {description} - файл не найден")
            self.results.append(False)
            return False
        
        with open(path, 'r', encoding='utf-8') as f:
            lines = len(f.readlines())
        
        ok = lines >= min_lines
        status = "✅" if ok else "❌"
        print(f"{status} {description} ({lines} строк)")
        self.results.append(ok)
        return ok

    def run_checks(self):
        """Запустить все проверки"""
        print("=" * 60)
        print("🔍 ПРОВЕРКА ФРОНТЕНДА E-COMMERCE")
        print("=" * 60)

        # Frontend файлы
        print("\n📁 Frontend файлы:")
        self.check_file_exists(self.frontend / 'index.html', 'index.html')
        self.check_file_exists(self.frontend / 'styles.css', 'styles.css')
        self.check_file_exists(self.frontend / 'main.js', 'main.js')
        self.check_file_exists(self.frontend / 'Dockerfile', 'Dockerfile')
        self.check_file_exists(self.frontend / 'nginx.conf', 'nginx.conf')

        # Документация фронтенда
        print("\n📖 Документация фронтенда:")
        self.check_file_exists(self.frontend / 'README.md', 'README.md')
        self.check_file_exists(self.frontend / 'FEATURES.md', 'FEATURES.md')
        self.check_file_exists(self.frontend / 'INDEX.md', 'INDEX.md')

        # Документация проекта
        print("\n📚 Документация проекта:")
        self.check_file_exists(self.root / 'START_HERE.md', 'START_HERE.md')
        self.check_file_exists(self.root / 'QUICKSTART.md', 'QUICKSTART.md')
        self.check_file_exists(self.root / 'PROJECT_OVERVIEW.md', 'PROJECT_OVERVIEW.md')
        self.check_file_exists(self.root / 'FRONTEND_COMPLETE.md', 'FRONTEND_COMPLETE.md')

        # Backend обновления
        print("\n⚙️ Backend обновления:")
        self.check_file_exists(self.root / 'docker-compose.yml', 'docker-compose.yml')
        self.check_file_exists(self.root / 'backend' / 'admin_api_client.py', 'admin_api_client.py')

        # Содержимое HTML
        print("\n🏗️ HTML компоненты:")
        self.check_content(self.frontend / 'index.html', '<header', 'Header компонент')
        self.check_content(self.frontend / 'index.html', 'id="homePage"', 'Home страница')
        self.check_content(self.frontend / 'index.html', 'id="productsPage"', 'Products страница')
        self.check_content(self.frontend / 'index.html', 'id="cartPage"', 'Cart страница')
        self.check_content(self.frontend / 'index.html', 'id="wishlistPage"', 'Wishlist страница')
        self.check_content(self.frontend / 'index.html', 'id="ordersPage"', 'Orders страница')
        self.check_content(self.frontend / 'index.html', 'id="authModal"', 'Auth modal')
        self.check_content(self.frontend / 'index.html', 'id="productModal"', 'Product modal')
        self.check_content(self.frontend / 'index.html', 'id="checkoutModal"', 'Checkout modal')

        # Содержимое CSS
        print("\n🎨 CSS стили:")
        self.check_content(self.frontend / 'styles.css', ':root', 'CSS переменные')
        self.check_content(self.frontend / 'styles.css', '.products-grid', 'Grid стили')
        self.check_content(self.frontend / 'styles.css', '@media', 'Media queries')
        self.check_content(self.frontend / 'styles.css', 'animation', 'Анимации')

        # Содержимое JavaScript
        print("\n⚡ JavaScript функции:")
        self.check_content(self.frontend / 'main.js', 'const app = {', 'App объект')
        self.check_content(self.frontend / 'main.js', 'async login()', 'Login функция')
        self.check_content(self.frontend / 'main.js', 'async register()', 'Register функция')
        self.check_content(self.frontend / 'main.js', 'async loadProducts()', 'LoadProducts функция')
        self.check_content(self.frontend / 'main.js', 'async addToCart()', 'AddToCart функция')
        self.check_content(self.frontend / 'main.js', 'async createOrder()', 'CreateOrder функция')
        self.check_content(self.frontend / 'main.js', 'async toggleWishlist()', 'ToggleWishlist функция')

        # API интеграция
        print("\n🔗 API интеграция:")
        self.check_content(self.frontend / 'main.js', '/account/register', 'Register API')
        self.check_content(self.frontend / 'main.js', '/account/login', 'Login API')
        self.check_content(self.frontend / 'main.js', '/product', 'Product API')
        self.check_content(self.frontend / 'main.js', '/cart', 'Cart API')
        self.check_content(self.frontend / 'main.js', '/orders', 'Orders API')
        self.check_content(self.frontend / 'main.js', '/wishlist', 'Wishlist API')

        # Размер файлов
        print("\n📊 Размер файлов:")
        self.check_lines(self.frontend / 'index.html', 600, 'index.html (мин 600 строк)')
        self.check_lines(self.frontend / 'styles.css', 400, 'styles.css (мин 400 строк)')
        self.check_lines(self.frontend / 'main.js', 700, 'main.js (мин 700 строк)')

        # Backend интеграция
        print("\n🔌 Backend интеграция:")
        self.check_content(self.root / 'backend' / 'app' / 'main.py', 'CORSMiddleware', 'CORS middleware')
        self.check_content(self.root / 'docker-compose.yml', 'frontend:', 'Frontend в docker-compose')

        # Результаты
        print("\n" + "=" * 60)
        passed = sum(self.results)
        total = len(self.results)
        percentage = (passed / total * 100) if total > 0 else 0
        
        print(f"✅ РЕЗУЛЬТАТЫ: {passed}/{total} проверок пройдено ({percentage:.1f}%)")
        print("=" * 60)

        if percentage == 100:
            print("🎉 ВСЕ ПРОВЕРКИ ПРОЙДЕНЫ УСПЕШНО!")
            print("Фронтенд полностью готов к использованию!")
            return True
        else:
            print("⚠️ Некоторые проверки не пройдены. Проверьте вывод выше.")
            return False

def main():
    checker = FrontendChecker()
    success = checker.run_checks()
    
    print("\n📖 ДОКУМЕНТАЦИЯ:")
    print("1. START_HERE.md - Начните отсюда")
    print("2. QUICKSTART.md - Быстрый старт (5 минут)")
    print("3. PROJECT_OVERVIEW.md - Полная документация")
    print("4. frontend/README.md - Документация фронтенда")
    print("5. frontend/FEATURES.md - Все функции")
    
    print("\n🚀 ЗАПУСК:")
    print("1. cd frontend")
    print("2. python -m http.server 8001")
    print("3. Откройте http://localhost:8001")
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
