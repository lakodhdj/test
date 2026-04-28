#!/usr/bin/env python3
"""
Скрипт для управления e-commerce проектом через API
Позволяет создавать товары, категории и других действия администратором
"""

import requests
import json
from typing import Optional

API_URL = "http://localhost:8000"

class APIClient:
    def __init__(self, base_url: str = API_URL):
        self.base_url = base_url
        self.session = requests.Session()
        self.token = None

    def register(self, email: str, password: str) -> dict:
        """Регистрация нового пользователя"""
        response = self.session.post(
            f"{self.base_url}/account/register",
            json={"email": email, "password": password}
        )
        return response.json()

    def login(self, email: str, password: str) -> dict:
        """Вход в аккаунт"""
        response = self.session.post(
            f"{self.base_url}/account/login",
            json={"email": email, "password": password}
        )
        if response.ok:
            print("✓ Успешный вход")
        return response.json()

    def get_me(self) -> dict:
        """Получить информацию о текущем пользователе"""
        response = self.session.get(f"{self.base_url}/account/me")
        return response.json()

    def create_category(self, name: str) -> dict:
        """Создать категорию"""
        response = self.session.post(
            f"{self.base_url}/product/categories/",
            json={"name": name}
        )
        return response.json()

    def get_categories(self) -> list:
        """Получить все категории"""
        response = self.session.get(f"{self.base_url}/product/categories/")
        return response.json()

    def create_product(
        self,
        title: str,
        description: str,
        price: float,
        stock_quantity: int,
        gender: str,  # "male", "female", "unisex"
        size: str,  # "XS", "S", "M", "L", "XL", "XXL"
        category_ids: Optional[list] = None,
        image_url: Optional[str] = None
    ) -> dict:
        """Создать товар"""
        data = {
            "title": title,
            "description": description,
            "price": price,
            "stock_quantity": stock_quantity,
            "gender": gender,
            "size": size,
            "category_ids": category_ids or [],
        }
        
        files = {}
        if image_url:
            data["image_url"] = image_url

        response = self.session.post(
            f"{self.base_url}/product/",
            json=data
        )
        return response.json()

    def get_products(self, page: int = 1, limit: int = 20, **filters) -> dict:
        """Получить список товаров"""
        params = {
            "page": page,
            "limit": limit,
            **filters
        }
        response = self.session.get(
            f"{self.base_url}/product",
            params=params
        )
        return response.json()

    def get_product_by_slug(self, slug: str) -> dict:
        """Получить товар по slug"""
        response = self.session.get(f"{self.base_url}/product/{slug}")
        return response.json()

    def get_orders(self) -> list:
        """Получить все заказы пользователя"""
        response = self.session.get(f"{self.base_url}/orders/")
        return response.json()

    def create_order(self, shipping_address: str) -> dict:
        """Создать заказ"""
        response = self.session.post(
            f"{self.base_url}/orders/",
            json={"shipping_address": shipping_address}
        )
        return response.json()

    def add_to_cart(self, product_id: int, quantity: int = 1) -> dict:
        """Добавить товар в корзину"""
        response = self.session.post(
            f"{self.base_url}/cart/{product_id}?quantity={quantity}"
        )
        return response.json()

    def remove_from_cart(self, product_id: int) -> dict:
        """Удалить товар из корзины"""
        response = self.session.delete(f"{self.base_url}/cart/{product_id}")
        return response.json()

    def add_to_wishlist(self, product_id: int) -> dict:
        """Добавить товар в избранное"""
        response = self.session.post(f"{self.base_url}/wishlist/{product_id}")
        return response.json()

    def remove_from_wishlist(self, product_id: int) -> dict:
        """Удалить товар из избранного"""
        response = self.session.delete(f"{self.base_url}/wishlist/{product_id}")
        return response.json()


def main():
    """Пример использования API"""
    client = APIClient()

    print("=" * 50)
    print("E-Commerce API Client")
    print("=" * 50)

    # Создаем клиента
    print("\n1. Регистрация пользователя...")
    try:
        reg = client.register("admin@test.com", "password123")
        print(f"   Результат: {reg.get('email', 'Error')}")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Вход
    print("\n2. Вход в аккаунт...")
    try:
        login = client.login("admin@test.com", "password123")
        print(f"   ✓ Вход успешен")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Получаем информацию о пользователе
    print("\n3. Информация о пользователе...")
    try:
        me = client.get_me()
        print(f"   Email: {me.get('email')}")
        print(f"   Верифицирован: {me.get('is_verified')}")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Создаем категории
    print("\n4. Создание категорий...")
    categories = ["Рубашки", "Брюки", "Платья", "Обувь"]
    category_ids = []
    for cat in categories:
        try:
            result = client.create_category(cat)
            category_ids.append(result.get('id'))
            print(f"   ✓ {cat} создана (ID: {result.get('id')})")
        except Exception as e:
            print(f"   ✗ Ошибка создания {cat}: {e}")

    # Получаем все категории
    print("\n5. Получение всех категорий...")
    try:
        cats = client.get_categories()
        for cat in cats:
            print(f"   - {cat['name']} (ID: {cat['id']})")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Создаем товары
    print("\n6. Создание товаров...")
    products = [
        {
            "title": "Классическая рубашка мужская",
            "description": "Удобная рубашка из хлопка",
            "price": 2999,
            "stock_quantity": 10,
            "gender": "male",
            "size": "M",
        },
        {
            "title": "Платье женское",
            "description": "Элегантное платье для особых случаев",
            "price": 4999,
            "stock_quantity": 5,
            "gender": "female",
            "size": "S",
        },
        {
            "title": "Джинсы унисекс",
            "description": "Удобные классические джинсы",
            "price": 3499,
            "stock_quantity": 20,
            "gender": "unisex",
            "size": "L",
        },
    ]

    for product in products:
        try:
            result = client.create_product(
                **product,
                category_ids=category_ids[:1]
            )
            print(f"   ✓ {product['title']} создан (ID: {result.get('id')})")
        except Exception as e:
            print(f"   ✗ Ошибка создания {product['title']}: {e}")

    # Получаем товары
    print("\n7. Получение товаров...")
    try:
        products = client.get_products(limit=10)
        print(f"   Всего товаров: {products.get('total')}")
        for item in products.get('items', [])[:3]:
            print(f"   - {item['title']} ({item['price']}₽)")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Добавляем в корзину
    if products.get('items'):
        print("\n8. Добавление в корзину...")
        try:
            product_id = products['items'][0]['id']
            cart = client.add_to_cart(product_id, quantity=2)
            print(f"   ✓ Товар добавлен в корзину")
        except Exception as e:
            print(f"   Ошибка: {e}")

    # Добавляем в избранное
    if products.get('items'):
        print("\n9. Добавление в избранное...")
        try:
            product_id = products['items'][0]['id']
            wish = client.add_to_wishlist(product_id)
            print(f"   ✓ Товар добавлен в избранное")
        except Exception as e:
            print(f"   Ошибка: {e}")

    # Создаем заказ
    print("\n10. Создание заказа...")
    try:
        order = client.create_order("ул. Примерная, дом 1")
        print(f"   ✓ Заказ создан (ID: {order.get('id')})")
    except Exception as e:
        print(f"   Ошибка: {e}")

    # Получаем заказы
    print("\n11. Получение заказов...")
    try:
        orders = client.get_orders()
        print(f"   Всего заказов: {len(orders)}")
        for order in orders[:3]:
            print(f"   - Заказ #{order['id']}: {order['total_amount']}₽ ({order['status']})")
    except Exception as e:
        print(f"   Ошибка: {e}")

    print("\n" + "=" * 50)
    print("Скрипт завершен")
    print("=" * 50)


if __name__ == "__main__":
    main()
