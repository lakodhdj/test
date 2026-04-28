const API_URL = 'http://localhost:8000';

const app = {
    // State
    currentUser: null,
    selectedProduct: null,
    cart: [],
    wishlist: [],
    currentPage: 1,
    currentPageId: 'homePage',
    requestedPageAfterAuth: null,
    filters: {
        search: '',
        category: '',
        gender: '',
        size: '',
        minPrice: 0,
        maxPrice: 10000,
    },
    products: [],
    categories: [],
    adminProducts: [],

    // Initialization
    async init() {
        await this.checkAuth();
        await this.loadCategories();
        this.attachEventListeners();
        await this.loadCart();
        await this.loadWishlist();
        await this.handleEmailVerification();
        await this.loadHomeProducts();
        this.handleHash();
    },

    attachEventListeners() {
        window.addEventListener('hashchange', () => this.handleHash());
        window.addEventListener('click', (e) => {
            const authModal = document.getElementById('authModal');
            if (e.target === authModal) {
                this.closeAuthModal();
            }

            const productModal = document.getElementById('productModal');
            if (e.target === productModal) {
                this.closeProductModal();
            }

            const checkoutModal = document.getElementById('checkoutModal');
            if (e.target === checkoutModal) {
                this.closeCheckoutModal();
            }
        });
    },

    // Auth
    async checkAuth() {
        try {
            const response = await fetch(`${API_URL}/account/me`, {
                credentials: 'include',
            });
            if (response.ok) {
                this.currentUser = await response.json();
            } else {
                this.currentUser = null;
            }
        } catch (error) {
            this.currentUser = null;
            console.log('Not authenticated');
        }
        this.updateAuthUI();
    },

    toggleAuth() {
        if (this.currentUser) {
            this.openAccountFromNav();
        } else {
            this.showAuthModal();
        }
    },

    openAccountFromNav() {
        window.location.hash = '#account';
        this.showAccountPage();
    },

    showAuthModal() {
        const modal = document.getElementById('authModal');
        modal.classList.add('active');
        this.switchToLogin();
    },

    closeAuthModal() {
        const modal = document.getElementById('authModal');
        modal.classList.remove('active');
    },

    showTerms() {
        const modal = document.getElementById('termsModal');
        modal.classList.add('active');
    },

    closeTermsModal() {
        const modal = document.getElementById('termsModal');
        modal.classList.remove('active');
    },

    async resendVerificationEmail() {
        if (!this.currentUser) {
            this.showMessage('Сначала войдите в аккаунт', 'info');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/account/send-verification-email`, {
                method: 'POST',
                credentials: 'include',
            });
            if (response.ok) {
                this.showMessage('Письмо подтверждения отправлено', 'success');
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка отправки', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    switchToLogin() {
        document.getElementById('loginForm').classList.add('active');
        document.getElementById('registerForm').classList.remove('active');
    },

    switchToRegister() {
        document.getElementById('loginForm').classList.remove('active');
        document.getElementById('registerForm').classList.add('active');
    },

    async login() {
        const email = document.getElementById('loginEmail').value;
        const password = document.getElementById('loginPassword').value;

        if (!email || !password) {
            this.showMessage('Заполните все поля', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/account/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ email, password }),
            });

            if (response.ok) {
                this.showMessage('Успешный вход', 'success');
                await this.checkAuth();
                if (this.requestedPageAfterAuth) {
                    await this.redirectAfterLogin();
                } else {
                    await this.refreshCurrentPage();
                }
                this.closeAuthModal();
                this.requestedPageAfterAuth = null;
                document.getElementById('loginEmail').value = '';
                document.getElementById('loginPassword').value = '';
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка входа', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    async loginAdminDemo() {
        const email = 'admin@example.com';
        const password = 'Admin1234';
        document.getElementById('loginEmail').value = email;
        document.getElementById('loginPassword').value = password;
        await this.login();
    },

    async register() {
        const email = document.getElementById('registerEmail').value;
        const password = document.getElementById('registerPassword').value;
        const password2 = document.getElementById('registerPassword2').value;
        const termsAccepted = document.getElementById('termsCheckbox').checked;

        if (!email || !password || !password2) {
            this.showMessage('Заполните все поля', 'error');
            return;
        }

        if (!termsAccepted) {
            this.showMessage('Примите Пользовательское соглашение', 'error');
            return;
        }

        if (password !== password2) {
            this.showMessage('Пароли не совпадают', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/account/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password, accepted_terms: termsAccepted }),
            });

            if (response.ok) {
                this.showMessage('Аккаунт создан. Проверьте почту для подтверждения', 'success');
                this.switchToLogin();
                document.getElementById('registerEmail').value = '';
                document.getElementById('registerPassword').value = '';
                document.getElementById('registerPassword2').value = '';
                document.getElementById('termsCheckbox').checked = false;
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка регистрации', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    async changePassword() {
        if (!this.currentUser) return;

        const current = document.getElementById('currentPassword').value;
        const newPass = document.getElementById('newPassword').value;
        const newPass2 = document.getElementById('newPassword2').value;

        if (!current || !newPass || !newPass2) {
            this.showMessage('Заполните все поля', 'error');
            return;
        }

        if (newPass !== newPass2) {
            this.showMessage('Новые пароли не совпадают', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/account/change-password`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({
                    current_password: current,
                    new_password: newPass,
                }),
            });

            if (response.ok) {
                this.showMessage('Пароль изменен', 'success');
                document.getElementById('currentPassword').value = '';
                document.getElementById('newPassword').value = '';
                document.getElementById('newPassword2').value = '';
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    async logout() {
        try {
            await fetch(`${API_URL}/account/logout`, {
                method: 'POST',
                credentials: 'include',
            });
        } catch (error) {
            console.warn('Logout error', error);
        }

        this.currentUser = null;
        this.cart = [];
        this.wishlist = [];
        this.updateAuthUI();
        this.closeAuthModal();
        this.showHome();
        this.showMessage('Вы вышли', 'success');
    },

    updateAuthUI() {
        const authBtn = document.getElementById('authBtn');
        const adminNav = document.getElementById('adminNav');
        if (this.currentUser) {
            authBtn.textContent = '👤 ' + this.currentUser.email.split('@')[0];
            if (this.currentUser.is_admin) {
                adminNav.style.display = 'inline-block';
            } else {
                adminNav.style.display = 'none';
            }
        } else {
            authBtn.textContent = 'Вход';
            adminNav.style.display = 'none';
        }
        this.showAccountState();
    },

    // Navigation
    showPage(pageId) {
        document.querySelectorAll('.page').forEach(page => page.classList.remove('active'));
        document.getElementById(pageId).classList.add('active');
        this.currentPageId = pageId;
        this.setActiveNav(pageId);
    },

    async refreshCurrentPage() {
        if (this.currentPageId === 'cartPage') {
            await this.loadCart();
            this.renderCart();
        } else if (this.currentPageId === 'wishlistPage') {
            await this.loadWishlist();
            this.renderWishlist();
        } else if (this.currentPageId === 'ordersPage') {
            await this.loadOrders();
        } else if (this.currentPageId === 'productsPage') {
            await this.loadProducts();
        } else if (this.currentPageId === 'adminPage') {
            await this.loadAdminStats();
            await this.loadAdminProducts();
        }
    },

    setActiveNav(pageId) {
        const mapping = {
            homePage: 'home',
            productsPage: 'products',
            wishlistPage: 'wishlist',
            cartPage: 'cart',
            ordersPage: 'orders',
            accountPage: 'account',
            adminPage: 'admin',
        };
        const section = mapping[pageId];
        if (section) {
            window.history.replaceState(null, '', `#${section}`);
        }
        document.querySelectorAll('.nav a').forEach(link => {
            link.classList.toggle('active', link.getAttribute('href') === `#${section}`);
        });
    },

    handleHash() {
        const hash = window.location.hash.replace('#', '');
        switch (hash) {
            case 'products':
                this.showProducts();
                break;
            case 'wishlist':
                this.showWishlist();
                break;
            case 'cart':
                this.showCart();
                break;
            case 'orders':
                this.showOrders();
                break;
            case 'account':
                this.showAccountPage();
                break;
            case 'admin':
                this.showAdmin();
                break;
            case 'home':
            default:
                this.showHome();
                break;
        }
    },

    showHome() {
        this.showPage('homePage');
        this.loadHomeProducts();
    },

    async showProducts() {
        this.showPage('productsPage');
        await this.loadProducts();
    },

    async showCart() {
        if (!this.currentUser) {
            this.requestedPageAfterAuth = 'cart';
            this.showMessage('Войдите в аккаунт', 'info');
            this.toggleAuth();
            return;
        }
        this.showPage('cartPage');
        await this.loadCart();
        this.renderCart();
    },

    async showWishlist() {
        if (!this.currentUser) {
            this.requestedPageAfterAuth = 'wishlist';
            this.showMessage('Войдите в аккаунт', 'info');
            this.toggleAuth();
            return;
        }
        this.showPage('wishlistPage');
        await this.loadWishlist();
        this.renderWishlist();
    },

    async showOrders() {
        if (!this.currentUser) {
            this.requestedPageAfterAuth = 'orders';
            this.showMessage('Войдите в аккаунт', 'info');
            this.toggleAuth();
            return;
        }
        this.showPage('ordersPage');
        await this.loadOrders();
    },

    applyQuickFilter(category = '', gender = '') {
        this.filters.category = category;
        this.filters.gender = gender;
        this.filters.search = '';
        this.filters.size = '';
        this.currentPage = 1;

        const searchInput = document.getElementById('searchInput');
        const categoryFilter = document.getElementById('categoryFilter');
        const genderFilter = document.getElementById('genderFilter');
        const sizeFilter = document.getElementById('sizeFilter');
        if (searchInput) searchInput.value = '';
        if (categoryFilter) categoryFilter.value = category;
        if (genderFilter) genderFilter.value = gender;
        if (sizeFilter) sizeFilter.value = '';

        this.showProducts();
    },

    showAccountState() {
        const guest = document.getElementById('accountPageGuest');
        const content = document.getElementById('accountPageContent');
        if (!guest || !content) return;

        if (this.currentUser) {
            guest.style.display = 'none';
            content.style.display = 'block';
            document.getElementById('accountEmail').textContent = this.currentUser.email;
            document.getElementById('accountStatus').textContent = this.currentUser.is_verified ? 'Верифицирован' : 'Не верифицирован';
        } else {
            guest.style.display = 'block';
            content.style.display = 'none';
        }
    },

    async showAccountPage() {
        this.showPage('accountPage');
        if (this.currentUser) {
            await this.checkAuth();
        }
        this.showAccountState();
    },

    async showAdmin() {
        if (!this.currentUser) {
            this.requestedPageAfterAuth = 'admin';
            this.showMessage('Войдите как админ', 'info');
            this.showAuthModal();
            return;
        }
        if (!this.currentUser.is_admin) {
            this.showMessage('Доступ администратора требуется', 'error');
            return;
        }
        this.showPage('adminPage');
        await this.loadAdminStats();
        await this.loadAdminProducts();
    },

    async loadAdminStats() {
        try {
            const response = await fetch(`${API_URL}/account/admin/stats`, {
                credentials: 'include',
            });
            if (response.ok) {
                const stats = await response.json();
                document.getElementById('adminStats').textContent = `Товаров: ${stats.products_count} · Заказов: ${stats.orders_count}`;
            } else {
                document.getElementById('adminStats').textContent = 'Не удалось загрузить статистику';
            }
        } catch (error) {
            console.error('Admin stats error:', error);
            document.getElementById('adminStats').textContent = 'Ошибка загрузки статистики';
        }
    },

    async loadAdminProducts() {
        try {
            const response = await fetch(`${API_URL}/product?limit=100`, {
                credentials: 'include',
            });
            if (response.ok) {
                const data = await response.json();
                this.renderAdminProducts(data.items || []);
            }
        } catch (error) {
            console.error('Error loading admin products:', error);
            document.getElementById('adminProducts').innerHTML = '<p class="empty-message">Не удалось загрузить товары</p>';
        }
    },

    openAdminProductForm(product = null) {
        document.getElementById('adminProductModalTitle').textContent = product ? 'Редактировать товар' : 'Добавить товар';
        document.getElementById('adminProductId').value = product?.id || '';
        document.getElementById('adminProductTitle').value = product?.title || '';
        document.getElementById('adminProductDescription').value = product?.description || '';
        document.getElementById('adminProductPrice').value = product?.price || '';
        document.getElementById('adminProductStock').value = product?.stock_quantity || '';
        document.getElementById('adminProductGender').value = product?.gender || 'unisex';
        document.getElementById('adminProductSize').value = product?.size || 'M';
        document.getElementById('adminProductImageUrl').value = product?.image_url || '';

        const checkboxes = document.querySelectorAll('#adminCategoryList input[type="checkbox"]');
        checkboxes.forEach(box => {
            box.checked = product?.categories?.some(cat => String(cat.id) === box.value) || false;
        });

        document.getElementById('adminProductModal').classList.add('active');
    },

    closeAdminProductModal() {
        document.getElementById('adminProductModal').classList.remove('active');
    },

    async saveAdminProduct() {
        const productId = document.getElementById('adminProductId').value;
        const title = document.getElementById('adminProductTitle').value.trim();
        const description = document.getElementById('adminProductDescription').value.trim();
        const price = parseFloat(document.getElementById('adminProductPrice').value);
        const stock_quantity = parseInt(document.getElementById('adminProductStock').value, 10);
        const gender = document.getElementById('adminProductGender').value;
        const size = document.getElementById('adminProductSize').value;
        const image_url = document.getElementById('adminProductImageUrl').value.trim();
        const categories = Array.from(document.querySelectorAll('#adminCategoryList input[type="checkbox"]:checked')).map(
            input => parseInt(input.value, 10)
        );

        if (!title || !price || isNaN(price) || isNaN(stock_quantity) || !image_url) {
            this.showMessage('Заполните название, цену, количество и ссылку на изображение', 'error');
            return;
        }

        try {
            let response;
            if (productId) {
                response = await fetch(`${API_URL}/product/${productId}`, {
                    method: 'PATCH',
                    headers: { 'Content-Type': 'application/json' },
                    credentials: 'include',
                    body: JSON.stringify({
                        title,
                        description,
                        price,
                        stock_quantity,
                        gender,
                        size,
                        image_url,
                        category_ids: categories,
                    }),
                });
            } else {
                const formData = new FormData();
                formData.append('title', title);
                formData.append('description', description);
                formData.append('price', String(price));
                formData.append('stock_quantity', String(stock_quantity));
                formData.append('gender', gender);
                formData.append('size', size);
                formData.append('image_url', image_url);
                categories.forEach(id => formData.append('category_ids', String(id)));

                response = await fetch(`${API_URL}/product/`, {
                    method: 'POST',
                    credentials: 'include',
                    body: formData,
                });
            }

            if (response.ok) {
                this.showMessage(`Товар ${productId ? 'обновлен' : 'добавлен'}`, 'success');
                await this.loadAdminProducts();
                await this.loadAdminStats();
                this.closeAdminProductModal();
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка сохранения товара', 'error');
            }
        } catch (error) {
            console.error('Admin product error:', error);
            this.showMessage('Ошибка сохранения товара', 'error');
        }
    },

    renderAdminProducts(products) {
        this.adminProducts = products;
        const container = document.getElementById('adminProducts');
        if (!products || products.length === 0) {
            container.innerHTML = '<p class="empty-message">Товары не найдены</p>';
            return;
        }

        container.innerHTML = products
            .map(product => `
                <div class="admin-product-card">
                    <div class="admin-product-row">
                        <div class="admin-product-title">${product.title}</div>
                        <div class="admin-product-actions">
                            <button class="btn btn-small" onclick="event.stopPropagation(); app.openAdminProductFormById(${product.id})">Редактировать</button>
                        </div>
                    </div>
                    <div class="admin-product-meta">
                        <span>${product.gender}</span>
                        <span>${product.size}</span>
                        <span>${product.price}₽</span>
                        <span>${product.stock_quantity} шт.</span>
                    </div>
                    <div class="admin-product-description">${product.description || ''}</div>
                </div>
            `)
            .join('');
    },

    openAdminProductFormById(productId) {
        const product = this.adminProducts.find(item => item.id === productId);
        if (!product) {
            this.showMessage('Товар не найден', 'error');
            return;
        }
        this.openAdminProductForm(product);
    },

    // Categories
    async loadCategories() {
        try {
            const response = await fetch(`${API_URL}/product/categories/`, {
                credentials: 'include',
            });
            if (response.ok) {
                this.categories = await response.json();
                this.updateCategoryFilter();
            }
        } catch (error) {
            console.error('Error loading categories:', error);
        }
    },

    updateCategoryFilter() {
        const select = document.getElementById('categoryFilter');
        this.categories.forEach(cat => {
            const option = document.createElement('option');
            option.value = cat.name;
            option.textContent = cat.name;
            select.appendChild(option);
        });
        this.renderAdminCategoryList();
    },

    renderAdminCategoryList() {
        const container = document.getElementById('adminCategoryList');
        if (!container) return;

        container.innerHTML = this.categories
            .map(category => `
                <label class="admin-category-item">
                    <input type="checkbox" value="${category.id}">
                    ${category.name}
                </label>
            `)
            .join('');
    },

    // Products
    async loadProducts() {
        try {
            const { search, category, gender, size, minPrice, maxPrice } = this.filters;
            const page = this.currentPage;

            const params = new URLSearchParams({
                page: page,
                limit: 20,
            });

            if (search) params.append('search', search);
            if (category) params.append('categories', category);
            if (gender) params.append('gender', gender);
            if (size) params.append('size', size);
            if (minPrice) params.append('min_price', minPrice);
            if (maxPrice) params.append('max_price', maxPrice);

            const response = await fetch(`${API_URL}/product?${params}`, {
                credentials: 'include',
            });

            if (response.ok) {
                const data = await response.json();
                this.products = data.items;
                this.renderProducts();
                this.renderPagination(data.total, data.limit);
            }
        } catch (error) {
            console.error('Error loading products:', error);
            this.showMessage('Ошибка загрузки товаров', 'error');
        }
    },

    async loadHomeProducts() {
        const grid = document.getElementById('homeProductsGrid');
        if (!grid) return;

        try {
            const response = await fetch(`${API_URL}/product?limit=8&page=1`, {
                credentials: 'include',
            });

            if (!response.ok) {
                throw new Error('Failed to load products');
            }

            const data = await response.json();
            const items = data.items || [];
            if (!items.length) {
                grid.innerHTML = '<p class="empty-message">Пока нет товаров</p>';
                return;
            }

            grid.innerHTML = items.map(product => `
                <div class="product-card" onclick="app.showProductDetail('${product.slug}')">
                    <div class="product-image">
                        ${product.image_url ? `<img src="${product.image_url}" alt="${product.title}">` : '📦'}
                    </div>
                    <div class="product-body">
                        <div class="product-title">${product.title}</div>
                        <div class="product-price">${product.price}₽</div>
                        <div class="product-actions">
                            <button class="btn btn-small" onclick="event.stopPropagation(); app.addToCart(${product.id})">В корзину</button>
                            <button class="btn btn-small btn-secondary" onclick="event.stopPropagation(); app.toggleWishlist(${product.id})">♡</button>
                        </div>
                    </div>
                </div>
            `).join('');
        } catch (error) {
            console.error('Error loading home products:', error);
            grid.innerHTML = '<p class="empty-message">Не удалось загрузить товары</p>';
        }
    },

    async handleEmailVerification() {
        const params = new URLSearchParams(window.location.search);
        const token = params.get('token');
        if (!token) return;

        try {
            const response = await fetch(`${API_URL}/account/verify-email?token=${encodeURIComponent(token)}`, {
                credentials: 'include',
            });
            const data = await response.json().catch(() => ({}));

            if (response.ok) {
                this.showMessage(data.msg || 'Email успешно подтвержден', 'success');
                await this.checkAuth();
            } else {
                this.showMessage(data.detail || data.msg || 'Не удалось подтвердить email', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка подтверждения email', 'error');
        } finally {
            params.delete('token');
            const next = `${window.location.pathname}${params.toString() ? `?${params.toString()}` : ''}${window.location.hash}`;
            window.history.replaceState({}, document.title, next);
        }
    },

    filterProducts() {
        this.filters.search = document.getElementById('searchInput').value;
        this.filters.category = document.getElementById('categoryFilter').value;
        this.filters.gender = document.getElementById('genderFilter').value;
        this.filters.size = document.getElementById('sizeFilter').value;
        this.filters.minPrice = document.getElementById('minPrice').value;
        this.filters.maxPrice = document.getElementById('maxPrice').value;

        document.getElementById('priceValue').textContent = `${this.filters.minPrice}-${this.filters.maxPrice}`;

        this.currentPage = 1;
        this.loadProducts();
    },

    renderProducts() {
        const grid = document.getElementById('productsGrid');
        if (this.products.length === 0) {
            grid.innerHTML = '<p class="empty-message">Товаров не найдено</p>';
            return;
        }

        grid.innerHTML = this.products.map(product => `
            <div class="product-card" onclick="app.showProductDetail('${product.slug}')">
                <div class="product-image">
                    ${product.image_url ? `<img src="${product.image_url}" alt="${product.title}">` : '📦'}
                </div>
                <div class="product-body">
                    <div class="product-title">${product.title}</div>
                    <div class="product-price">${product.price}₽</div>
                    <div class="product-meta">
                        <span>${product.stock_quantity > 0 ? '✓ В наличии' : '✗ Нет в наличии'}</span>
                        <span>${product.gender}</span>
                        <span>${product.size}</span>
                    </div>
                    <div class="product-actions">
                        <button class="btn btn-small" onclick="event.stopPropagation(); app.addToCart(${product.id})">В корзину</button>
                        <button class="btn btn-small btn-secondary" onclick="event.stopPropagation(); app.toggleWishlist(${product.id})">♡</button>
                    </div>
                </div>
            </div>
        `).join('');
    },

    async showProductDetail(productSlug) {
        try {
            // productSlug может быть как slug, так и id
            const response = await fetch(`${API_URL}/product/${productSlug}`, {
                credentials: 'include',
            });
            if (response.ok) {
                this.selectedProduct = await response.json();
                this.renderProductDetail();
                document.getElementById('productModal').classList.add('active');
                this.updateWishlistButton();
            } else {
                this.showMessage('Товар не найден', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка загрузки товара', 'error');
        }
    },

    renderProductDetail() {
        const product = this.selectedProduct;
        document.getElementById('modalImage').src = product.image_url || '';
        document.getElementById('modalImage').style.display = product.image_url ? 'block' : 'none';
        document.getElementById('modalTitle').textContent = product.title;
        document.getElementById('modalDescription').textContent = product.description || 'Описание отсутствует';
        document.getElementById('modalPrice').textContent = `${product.price}₽`;
        document.getElementById('modalStock').textContent = product.stock_quantity > 0 ? '✓ В наличии' : '✗ Нет в наличии';
        document.getElementById('modalGender').textContent = product.gender;
        document.getElementById('modalSize').textContent = product.size;
        document.getElementById('quantityInput').value = 1;
    },

    closeProductModal() {
        document.getElementById('productModal').classList.remove('active');
    },

    renderPagination(total, limit) {
        const pages = Math.ceil(total / limit);
        const pagination = document.getElementById('pagination');

        if (pages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        let html = '';
        for (let i = 1; i <= pages; i++) {
            html += `<button class="${i === this.currentPage ? 'active' : ''}" onclick="app.goToPage(${i})">${i}</button>`;
        }
        pagination.innerHTML = html;
    },

    goToPage(page) {
        this.currentPage = page;
        this.loadProducts();
        window.scrollTo(0, 0);
    },

    // Cart
    async loadCart() {
        if (!this.currentUser) {
            this.cart = [];
            return;
        }

        try {
            const response = await fetch(`${API_URL}/cart/`, {
                credentials: 'include',
            });

            if (response.ok) {
                const data = await response.json();
                this.cart = data.items || [];
            } else {
                this.cart = [];
            }
        } catch (error) {
            this.cart = [];
            console.warn('Error loading cart:', error);
        }
    },

    async addToCart(productId) {
        if (!this.currentUser) {
            this.showMessage('Войдите в аккаунт', 'info');
            this.toggleAuth();
            return;
        }

        try {
            const quantityInput = document.getElementById('quantityInput');
            const quantity = quantityInput ? parseInt(quantityInput.value) || 1 : 1;
            const response = await fetch(`${API_URL}/cart/${productId}?quantity=${quantity}`, {
                method: 'POST',
                credentials: 'include',
            });

            if (response.ok) {
                this.showMessage('Товар добавлен в корзину', 'success');
                await this.loadCart();
                if (this.currentPageId === 'cartPage') {
                    this.renderCart();
                }
                this.closeProductModal();
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка добавления', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    async removeFromCart(productId) {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`${API_URL}/cart/${productId}`, {
                method: 'DELETE',
                credentials: 'include',
            });

            if (response.ok) {
                await this.loadCart();
                if (this.currentPageId === 'cartPage') {
                    this.renderCart();
                }
                this.showMessage('Товар удален', 'success');
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка удаления', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка удаления', 'error');
        }
    },

    renderCart() {
        const container = document.getElementById('cartContent');

        if (!this.cart || this.cart.length === 0) {
            container.innerHTML = '<p class="empty-message">Корзина пуста</p>';
            return;
        }

        const total = this.cart.reduce((sum, item) => sum + item.subtotal, 0);
        const itemCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);

        const html = `
            <div>
                ${this.cart.map(item => `
                    <div class="cart-item">
                        <div class="cart-item-image">
                            ${item.product.image_url ? `<img src="${item.product.image_url}" alt="${item.product.title}">` : '📦'}
                        </div>
                        <div class="cart-item-info">
                            <div class="cart-item-title">${item.product.title}</div>
                            <div class="cart-item-price">${item.product.price}₽ × ${item.quantity}</div>
                        </div>
                        <div class="cart-item-controls">
                            <input type="number" value="${item.quantity}" min="1" onchange="app.updateCartQuantity(${item.product.id}, this.value)">
                            <button class="btn btn-small btn-danger" onclick="app.removeFromCart(${item.product.id})">✕</button>
                        </div>
                    </div>
                `).join('')}
            </div>
            <div class="cart-summary">
                <div class="cart-summary-details">
                    <div>Товаров: ${itemCount}</div>
                    <div class="cart-summary-total">Итого: ${total}₽</div>
                </div>
                <div class="cart-summary-actions">
                    <button class="btn" onclick="app.showCheckout()">Оформить заказ</button>
                    <button class="btn btn-secondary" onclick="app.clearCart()">Очистить корзину</button>
                </div>
            </div>
        `;

        container.innerHTML = html;
    },

    async updateCartQuantity(productId, newQuantity) {
        const quantity = Math.max(1, parseInt(newQuantity));
        if (!this.currentUser) return;

        try {
            const response = await fetch(`${API_URL}/cart/${productId}?quantity=${quantity}`, {
                method: 'PUT',
                credentials: 'include',
            });
            if (response.ok) {
                await this.loadCart();
                if (this.currentPageId === 'cartPage') {
                    this.renderCart();
                }
                this.showMessage('Количество обновлено', 'success');
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка обновления', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    async clearCart() {
        if (!this.currentUser) return;
        try {
            const response = await fetch(`${API_URL}/cart/clear`, {
                method: 'POST',
                credentials: 'include',
            });
            if (response.ok) {
                await this.loadCart();
                if (this.currentPageId === 'cartPage') {
                    this.renderCart();
                }
                this.showMessage('Корзина очищена', 'success');
            }
        } catch (error) {
            this.showMessage('Ошибка очистки', 'error');
        }
    },

    showCheckout() {
        const itemCount = this.cart.reduce((sum, item) => sum + item.quantity, 0);
        const total = this.cart.reduce((sum, item) => sum + item.subtotal, 0);
        document.getElementById('checkoutItems').textContent = itemCount;
        document.getElementById('checkoutTotal').textContent = total + '₽';
        document.getElementById('checkoutModal').classList.add('active');
    },

    closeCheckoutModal() {
        document.getElementById('checkoutModal').classList.remove('active');
    },

    async createOrder() {
        if (!this.currentUser) return;

        const address = document.getElementById('shippingAddress').value;
        if (!address) {
            this.showMessage('Укажите адрес доставки', 'error');
            return;
        }

        try {
            const response = await fetch(`${API_URL}/orders/`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                credentials: 'include',
                body: JSON.stringify({ shipping_address: address }),
            });

            if (response.ok) {
                this.showMessage('Заказ создан успешно', 'success');
                await this.loadCart();
                await this.loadOrders();
                this.closeCheckoutModal();
                document.getElementById('shippingAddress').value = '';
                this.showOrders();
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка создания заказа', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка сети', 'error');
        }
    },

    // Wishlist
    async loadWishlist() {
        if (!this.currentUser) {
            this.wishlist = [];
            return;
        }

        try {
            const response = await fetch(`${API_URL}/wishlist/`, {
                credentials: 'include',
            });

            if (response.ok) {
                const data = await response.json();
                this.wishlist = data.items || [];
            } else {
                this.wishlist = [];
            }
        } catch (error) {
            this.wishlist = [];
            console.warn('Error loading wishlist:', error);
        }
    },

    async toggleWishlist(productId) {
        if (!this.currentUser) {
            this.showMessage('Войдите в аккаунт', 'info');
            this.toggleAuth();
            return;
        }

        const isInWishlist = this.wishlist.some(item => item.id === productId);

        try {
            const method = isInWishlist ? 'DELETE' : 'POST';
            const response = await fetch(`${API_URL}/wishlist/${productId}`, {
                method: method,
                credentials: 'include',
            });

            if (response.ok) {
                await this.loadWishlist();
                if (this.currentPageId === 'wishlistPage') {
                    this.renderWishlist();
                }
                this.updateWishlistButton();
                this.showMessage(isInWishlist ? 'Удалено из избранного' : 'Добавлено в избранное', 'success');
            } else {
                const data = await response.json();
                this.showMessage(data.detail || 'Ошибка', 'error');
            }
        } catch (error) {
            this.showMessage('Ошибка', 'error');
        }
    },

    updateWishlistButton() {
        if (!this.selectedProduct) return;
        const btn = document.getElementById('wishlistBtn');
        if (this.wishlist.some(item => item.id === this.selectedProduct.id)) {
            btn.textContent = '♥ В избранном';
            btn.style.opacity = '0.8';
        } else {
            btn.textContent = '♡ Избранное';
            btn.style.opacity = '1';
        }
    },

    async renderWishlist() {
        if (!this.wishlist || this.wishlist.length === 0) {
            document.getElementById('wishlistContent').innerHTML = '<p class="empty-message">Избранное пусто</p>';
            return;
        }

        const html = `
            <div class="wishlist-grid">
                ${this.wishlist.map(product => `
                    <div class="wishlist-item">
                        <div class="wishlist-item-image">
                            ${product.image_url ? `<img src="${product.image_url}" alt="${product.title}">` : '📦'}
                        </div>
                        <div class="wishlist-item-title">${product.title}</div>
                        <div class="wishlist-item-price">${product.price}₽</div>
                        <div class="wishlist-item-actions">
                            <button class="btn btn-small" onclick="app.addToCart(${product.id})">В корзину</button>
                            <button class="btn btn-small btn-danger" onclick="app.toggleWishlist(${product.id})">✕</button>
                        </div>
                    </div>
                `).join('')}
            </div>
        `;

        document.getElementById('wishlistContent').innerHTML = html;
    },

    // Orders
    async loadOrders() {
        if (!this.currentUser) return;

        try {
            const response = await fetch(`${API_URL}/orders/`, {
                credentials: 'include',
            });

            if (response.ok) {
                const data = await response.json();
                this.renderOrders(data.orders || []);
            }
        } catch (error) {
            this.showMessage('Ошибка загрузки заказов', 'error');
        }
    },

    renderOrders(orders) {
        const container = document.getElementById('ordersContent');

        if (!orders || orders.length === 0) {
            container.innerHTML = '<p class="empty-message">Заказов нет</p>';
            return;
        }

        const html = orders.map(order => `
            <div class="order-card">
                <div class="order-header">
                    <span class="order-number">Заказ #${order.id}</span>
                    <span class="order-status ${order.status.toLowerCase()}">${this.translateStatus(order.status)}</span>
                </div>
                <div class="order-items">
                    ${order.items.map(item => `
                        <div class="order-item-simple">
                            <span>${item.product?.title || 'Товар'} × ${item.quantity}</span>
                            <span>${(item.price_at_purchase || item.product?.price || 0) * item.quantity}₽</span>
                        </div>
                    `).join('')}
                </div>
                <div class="order-total">
                    <span>Итого:</span>
                    <span>${order.total_amount}₽</span>
                </div>
                <div style="font-size: 12px; opacity: 0.7;">
                    <p>Адрес: ${order.shipping_address}</p>
                    <p>Дата: ${new Date(order.created_at).toLocaleDateString('ru-RU')}</p>
                </div>
            </div>
        `).join('');

        container.innerHTML = html;
    },

    async redirectAfterLogin() {
        const target = this.requestedPageAfterAuth;
        this.requestedPageAfterAuth = null;

        if (target === 'cart') {
            await this.showCart();
        } else if (target === 'wishlist') {
            await this.showWishlist();
        } else if (target === 'orders') {
            await this.showOrders();
        } else if (target === 'admin') {
            await this.showAdmin();
        } else {
            await this.refreshCurrentPage();
        }
    },

    translateStatus(status) {
        const translations = {
            'pending': 'Ожидание',
            'processing': 'Обработка',
            'delivered': 'Доставлено',
            'cancelled': 'Отменено',
        };
        return translations[status.toLowerCase()] || status;
    },

    // Messages
    showMessage(text, type = 'info') {
        const container = document.getElementById('messages');
        const message = document.createElement('div');
        message.className = `message ${type}`;
        message.textContent = text;
        container.appendChild(message);

        setTimeout(() => {
            message.style.animation = 'slideInRight 0.3s reverse';
            setTimeout(() => message.remove(), 300);
        }, 3000);
    },
};

// Initialize app
document.addEventListener('DOMContentLoaded', () => app.init());
