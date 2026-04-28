# 📑 Индекс фронтенда E-Commerce

## 📁 Структура файлов

```
frontend/
├── index.html           # ✅ Основной HTML файл
├── styles.css           # ✅ Минималистичные CSS стили
├── main.js              # ✅ JavaScript логика приложения
├── Dockerfile           # ✅ Docker контейнер для фронтенда
├── nginx.conf           # ✅ Nginx конфигурация
├── README.md            # 📖 Документация фронтенда
├── FEATURES.md          # 🎯 Список всех функций
└── INDEX.md             # 📑 Этот файл
```

## 📊 Содержание HTML

### Страницы (Sections)

| ID | Название | Функция | Статус |
|----|---------|---------|----|
| `homePage` | Главная | Приветствие и ссылка на товары | ✅ |
| `productsPage` | Товары | Каталог с фильтрацией и пагинацией | ✅ |
| `cartPage` | Корзина | Управление товарами в корзине | ✅ |
| `wishlistPage` | Избранное | Сохраненные товары | ✅ |
| `ordersPage` | Заказы | История заказов | ✅ |

### Модальные окна (Modals)

| ID | Название | Назначение | Функция |
|----|---------|-----------|---------|
| `authModal` | Аутентификация | Вход, регистрация, профиль | ✅ |
| `productModal` | Деталь товара | Полная информация о товаре | ✅ |
| `checkoutModal` | Оформление | Завершение покупки | ✅ |

### Основные компоненты

#### Header
```html
<header class="header">
  <h1 class="logo">Store</h1>
  <nav class="nav">
    - Главная
    - Товары
    - Избранное
    - Корзина
    - Заказы
    - 👤 Вход
  </nav>
</header>
```

#### Filters
```html
<div class="filters">
  - Поиск
  - Категория
  - Пол
  - Размер
  - Диапазон цены
</div>
```

#### Product Grid
```html
<div class="products-grid">
  - Карточки товаров в сетке
  - Адаптивное количество колонок
  - Изображение, название, цена
  - Быстрые действия
</div>
```

#### Cart
```html
<div class="cart-content">
  - Список товаров
  - Управление количеством
  - Итоговая стоимость
  - Кнопка оформления
</div>
```

#### Wishlist
```html
<div class="wishlist-content">
  - Сетка избранных товаров
  - Быстрое добавление в корзину
  - Удаление из избранного
</div>
```

#### Orders
```html
<div class="orders-content">
  - История заказов
  - Статус каждого заказа
  - Детали товаров в заказе
  - Итоговая сумма и дата
</div>
```

## 🎨 CSS структура

### Селекторы

| Класс | Тип | Назначение |
|-------|-----|-----------|
| `.page` | section | Основные страницы |
| `.modal` | div | Модальные окна |
| `.container` | div | Контейнер с максимальной шириной |
| `.header` | header | Верхняя навигация |
| `.nav` | nav | Навигационные ссылки |
| `.main` | main | Основной контент |
| `.footer` | footer | Подвал страницы |

### Компоненты

| Класс | Примеры | Использование |
|-------|---------|-------------|
| `.btn` | `.btn-secondary`, `.btn-danger`, `.btn-small` | Кнопки |
| `.product-*` | `.product-card`, `.product-image`, `.product-title` | Карточки товаров |
| `.cart-*` | `.cart-item`, `.cart-summary`, `.cart-actions` | Корзина |
| `.wishlist-*` | `.wishlist-grid`, `.wishlist-item` | Избранное |
| `.order-*` | `.order-card`, `.order-status` | Заказы |
| `.modal-*` | `.modal-content`, `.modal-close`, `.modal-sm` | Модали |
| `.message` | `.message.success`, `.message.error` | Уведомления |

### Переменные CSS

```css
:root {
  --bg: #fff;           /* Фон */
  --text: #000;         /* Текст */
  --border: #e0e0e0;    /* Границы */
  --primary: #000;      /* Основной цвет */
  --hover: #f5f5f5;     /* Наведение */
  --success: #22c55e;   /* Успех */
  --danger: #ef4444;    /* Ошибка */
  --warning: #f59e0b;   /* Предупреждение */
  --info: #3b82f6;      /* Информация */
}
```

### Brakepoints

| Размер | Ширина | Колонки | Использование |
|--------|--------|--------|---------------|
| Desktop | 1200px+ | 4 | Большие экраны |
| Tablet | 768-1199px | 3 | Планшеты |
| Mobile | <768px | 1 | Мобильные |

## 🔧 JavaScript структура

### Объект app

```javascript
const app = {
  // Состояние
  currentUser: null,
  selectedProduct: null,
  cart: [],
  wishlist: [],
  currentPage: 1,
  filters: {},
  products: [],
  categories: [],
  
  // Методы инициализации
  init()
  attachEventListeners()
  
  // Аутентификация
  checkAuth()
  login()
  register()
  logout()
  changePassword()
  toggleAuth()
  
  // Навигация
  showPage(pageId)
  showHome()
  showProducts()
  showCart()
  showWishlist()
  showOrders()
  
  // Товары
  loadCategories()
  loadProducts()
  filterProducts()
  showProductDetail(productSlug)
  renderProducts()
  renderPagination()
  goToPage(page)
  
  // Корзина
  loadCart()
  saveCart()
  addToCart(productId)
  removeFromCart(productId)
  updateCartQuantity(productId, quantity)
  renderCart()
  showCheckout()
  createOrder()
  
  // Избранное
  loadWishlist()
  saveWishlist()
  toggleWishlist(productId)
  renderWishlist()
  updateWishlistButton()
  
  // Заказы
  loadOrders()
  renderOrders(orders)
  translateStatus(status)
  
  // Утилиты
  showMessage(text, type)
}
```

### Event Listeners

```javascript
// Кликеры
onclick="app.showHome()"
onclick="app.showProducts()"
onclick="app.showCart()"
onclick="app.addToCart(productId)"
onclick="app.toggleWishlist(productId)"
onclick="app.login()"

// Изменения
onchange="app.filterProducts()"
onchange="app.updateCartQuantity(productId, this.value)"

// Ввод
onkeyup="app.filterProducts()"
```

## 📡 API вызовы

### Аутентификация

```javascript
// Регистрация
POST /account/register
Body: { email, password }
Response: { id, email, is_verified }

// Вход
POST /account/login
Body: { email, password }
Response: { message: "Login successful" }
Cookies: access_token, refresh_token

// Профиль
GET /account/me
Response: { id, email, is_verified }

// Смена пароля
POST /account/change-password
Body: { current_password, new_password }
Response: { msg: "Password changed successfully" }
```

### Товары

```javascript
// Список
GET /product?page=1&limit=20&category=...&gender=...&size=...&min_price=...&max_price=...
Response: { total, page, limit, items: [...] }

// Деталь
GET /product/{slug}
Response: { id, title, description, price, stock_quantity, gender, size, image_url, ... }

// Категории
GET /product/categories/
Response: [{ id, name }, ...]
```

### Корзина

```javascript
// Добавить
POST /cart/{product_id}?quantity=1
Response: { message: "Product added to cart" }

// Удалить
DELETE /cart/{product_id}
Response: { message: "Product removed from cart" }
```

### Заказы

```javascript
// Создать
POST /orders/
Body: { shipping_address }
Response: { id, total_amount, status, ... }

// Получить
GET /orders/
Response: [{ id, total_amount, status, items, shipping_address, created_at }, ...]
```

### Избранное

```javascript
// Добавить
POST /wishlist/{product_id}
Response: { msg: "Product added to wishlist" }

// Удалить
DELETE /wishlist/{product_id}
Response: { message: "Product removed from wishlist" }
```

## 💾 Хранение данных
Корзина и избранное сохраняются на сервере в базе данных и доступны после входа в систему.

## 🔒 Cookies

```javascript
// Установка (сервером)
Set-Cookie: access_token=...; HttpOnly; Secure; SameSite=Lax; Max-Age=604800
Set-Cookie: refresh_token=...; HttpOnly; Secure; SameSite=Lax; Max-Age=604800

// Использование (автоматически)
// credentials: 'include' в fetch запросах
```

## 🎯 Workflow основных функций

### Регистрация
```
1. Пользователь кликает "Вход" → "Создать"
2. Заполняет email и пароль
3. Нажимает "Создать аккаунт"
4. POST /account/register
5. Успешное сообщение
6. Форма переключается на вход
```

### Добавление в корзину
```
1. Пользователь кликает товар
2. Открывается модал с деталями
3. Указывает количество
4. Нажимает "Добавить в корзину"
5. POST /cart/{productId}
6. Товар сохраняется на сервере в корзине пользователя
7. Успешное уведомление
8. Модал закрывается (опционально)
```

### Оформление заказа
```
1. Пользователь переходит в корзину
2. Проверяет товары
3. Нажимает "Оформить заказ"
4. Открывается модал оформления
5. Вводит адрес доставки
6. Нажимает "Создать заказ"
7. POST /orders/
8. Заказ создается
9. Корзина очищается
10. Переходит в историю заказов
11. Успешное сообщение
```

### Фильтрация товаров
```
1. Пользователь вводит значение в фильтр
2. onchange → app.filterProducts()
3. Обновляются this.filters
4. currentPage = 1
5. await app.loadProducts()
6. GET /product?filter=value
7. Результаты обновляются
8. renderProducts()
9. Сетка обновляется
10. renderPagination() обновляет навигацию
```

## 🐛 Debug режим

### Включение логирования
```javascript
// В main.js
const DEBUG = true;

if (DEBUG) {
  console.log('State:', app);
  console.log('Cart:', app.cart);
  console.log('User:', app.currentUser);
}
```

### Проверка в DevTools
```javascript
// Console tab
app.currentUser           // Текущий пользователь
app.cart                  // Содержимое корзины
// Карточка корзины и избранное хранятся на сервере
document.cookies          // Cookies (будут пусты из-за HttpOnly)
```

## 📚 Расширение функционала

### Добавить новую страницу
```javascript
// 1. HTML в index.html
<section id="myPage" class="page">...</section>

// 2. Кнопка в навигации
<a href="#mypage" onclick="app.showMyPage()">Моя страница</a>

// 3. Функция в main.js
showMyPage() {
  this.showPage('myPage');
  // загрузка данных
}
```

### Добавить новый фильтр
```javascript
// 1. HTML в index.html
<select id="newFilter" onchange="app.filterProducts()">
  <option value="">Все</option>
  <option value="val1">Значение 1</option>
</select>

// 2. В filterProducts()
this.filters.newFilter = document.getElementById('newFilter').value;

// 3. В loadProducts() параметры
params.append('new_filter', this.filters.newFilter);
```

### Добавить новый modal
```javascript
// 1. HTML в index.html
<div id="myModal" class="modal">
  <div class="modal-content">
    <!-- Содержимое -->
  </div>
</div>

// 2. Функции в main.js
showMyModal() {
  document.getElementById('myModal').classList.add('active');
}

closeMyModal() {
  document.getElementById('myModal').classList.remove('active');
}
```

## 📊 Производительность

### Оптимизации
- ✅ CSS Grid вместо floats
- ✅ Lazy loading изображений
- ✅ Минимизация DOM манипуляций
- ✅ Event delegation где возможно
- ✅ Серверное хранение корзины, избранного и заказов

### Метрики
- **LCP**: <2.5s
- **FID**: <100ms
- **CLS**: <0.1
- **Size**: ~48KB
- **Gzip**: ~15KB

---

**Полное руководство по структуре и функциям фронтенда завершено! 🎉**
