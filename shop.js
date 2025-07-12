// Shop Page JavaScript
class ShopPage {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.shopId = null;
        this.shopData = null;
        this.products = [];
        this.cart = [];
        this.filters = {
            category: '',
            priceMin: '',
            priceMax: ''
        };
        this.init();
    }

    init() {
        this.getShopIdFromUrl();
        this.setupEventListeners();
        this.loadShopData();
        this.loadProducts();
        this.loadCartFromStorage();
        this.updateCartDisplay();
    }

    getShopIdFromUrl() {
        const params = new URLSearchParams(window.location.search);
        this.shopId = params.get('shop_id');
        
        if (!this.shopId) {
            this.showError('ID магазина не указан');
            return;
        }
    }

    setupEventListeners() {
        // Cart controls
        document.getElementById('cart-btn')?.addEventListener('click', () => this.toggleCart());
        document.getElementById('close-cart')?.addEventListener('click', () => this.closeCart());
        document.getElementById('cart-overlay')?.addEventListener('click', () => this.closeCart());
        
        // Checkout
        document.getElementById('checkout-btn')?.addEventListener('click', () => this.checkout());
        
        // Filters
        document.getElementById('apply-filters')?.addEventListener('click', () => this.applyFilters());
        
        // Filter inputs
        document.getElementById('category-filter')?.addEventListener('change', (e) => {
            this.filters.category = e.target.value;
        });
        
        document.getElementById('price-min')?.addEventListener('input', (e) => {
            this.filters.priceMin = e.target.value;
        });
        
        document.getElementById('price-max')?.addEventListener('input', (e) => {
            this.filters.priceMax = e.target.value;
        });
    }

    async loadShopData() {
        try {
            // For now, we'll use mock data since we don't have a specific shop endpoint
            // In a real app, you'd fetch: `${this.apiBase}/shops/${this.shopId}`
            this.shopData = {
                id: this.shopId,
                name: `Магазин #${this.shopId}`,
                description: 'Описание магазина будет загружено с сервера',
                category: 'general',
                rating: 4.8
            };
            
            this.updateShopDisplay();
        } catch (error) {
            console.error('Error loading shop data:', error);
            this.showError('Ошибка загрузки данных магазина');
        }
    }

    updateShopDisplay() {
        if (!this.shopData) return;
        
        document.getElementById('shop-name').textContent = this.shopData.name;
        document.getElementById('shop-title').textContent = this.shopData.name;
        document.getElementById('shop-description').textContent = this.shopData.description;
    }

    async loadProducts() {
        try {
            const response = await fetch(`${this.apiBase}/products/${this.shopId}`);
            if (response.ok) {
                this.products = await response.json();
            } else {
                // Fallback to mock data if API is not available
                this.products = this.getMockProducts();
            }
            
            this.renderProducts();
            this.updateProductsCount();
        } catch (error) {
            console.error('Error loading products:', error);
            // Use mock data as fallback
            this.products = this.getMockProducts();
            this.renderProducts();
            this.updateProductsCount();
        }
    }

    getMockProducts() {
        return [
            {
                id: 1,
                name: 'Смартфон Galaxy S24',
                price: 2500000,
                description: 'Новейший смартфон с мощным процессором и отличной камерой',
                category: 'electronics',
                photo_file_id: null
            },
            {
                id: 2,
                name: 'Ноутбук MacBook Pro',
                price: 8500000,
                description: 'Профессиональный ноутбук для работы и творчества',
                category: 'electronics',
                photo_file_id: null
            },
            {
                id: 3,
                name: 'Футболка хлопковая',
                price: 150000,
                description: 'Комфортная футболка из 100% хлопка',
                category: 'clothing',
                photo_file_id: null
            },
            {
                id: 4,
                name: 'Книга "Бизнес с нуля"',
                price: 85000,
                description: 'Практическое руководство по созданию успешного бизнеса',
                category: 'books',
                photo_file_id: null
            }
        ];
    }

    renderProducts() {
        const container = document.getElementById('products-grid');
        if (!container) return;

        const filteredProducts = this.filterProducts();
        
        if (filteredProducts.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <i class="fas fa-box-open" style="font-size: 3rem; color: #9ca3af; margin-bottom: 1rem;"></i>
                    <h3>Товары не найдены</h3>
                    <p>Попробуйте изменить фильтры поиска</p>
                </div>
            `;
            return;
        }

        container.innerHTML = filteredProducts.map(product => `
            <div class="product-card">
                <div class="product-image">
                    ${product.photo_file_id ? 
                        `<img src="${this.apiBase}/photo_telegram/${encodeURIComponent(product.photo_file_id)}" alt="${this.escapeHtml(product.name)}" onerror="this.parentElement.innerHTML='<i class=\\'fas fa-image\\'></i>'">` :
                        '<i class="fas fa-image"></i>'
                    }
                </div>
                <div class="product-content">
                    <h3 class="product-name">${this.escapeHtml(product.name)}</h3>
                    <div class="product-price">${product.price.toLocaleString()} UZS</div>
                    <p class="product-description">${this.escapeHtml(product.description)}</p>
                    <div class="product-actions">
                        <button class="btn-add-cart" onclick="shopPage.addToCart(${product.id}, '${this.escapeHtml(product.name)}', ${product.price})">
                            <i class="fas fa-cart-plus"></i>
                            В корзину
                        </button>
                        <button class="btn-view" onclick="shopPage.viewProduct(${product.id})">
                            <i class="fas fa-eye"></i>
                            Подробнее
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    filterProducts() {
        return this.products.filter(product => {
            // Category filter
            if (this.filters.category && product.category !== this.filters.category) {
                return false;
            }
            
            // Price filters
            if (this.filters.priceMin && product.price < parseFloat(this.filters.priceMin)) {
                return false;
            }
            
            if (this.filters.priceMax && product.price > parseFloat(this.filters.priceMax)) {
                return false;
            }
            
            return true;
        });
    }

    applyFilters() {
        this.renderProducts();
    }

    updateProductsCount() {
        const count = this.products.length;
        document.getElementById('products-count').textContent = count;
    }

    addToCart(productId, productName, price) {
        const existingItem = this.cart.find(item => item.id === productId);
        
        if (existingItem) {
            existingItem.quantity += 1;
        } else {
            this.cart.push({
                id: productId,
                name: productName,
                price: price,
                quantity: 1
            });
        }
        
        this.saveCartToStorage();
        this.updateCartDisplay();
        this.showNotification('Товар добавлен в корзину', 'success');
    }

    removeFromCart(productId) {
        this.cart = this.cart.filter(item => item.id !== productId);
        this.saveCartToStorage();
        this.updateCartDisplay();
    }

    updateQuantity(productId, newQuantity) {
        const item = this.cart.find(item => item.id === productId);
        if (item) {
            if (newQuantity <= 0) {
                this.removeFromCart(productId);
            } else {
                item.quantity = newQuantity;
                this.saveCartToStorage();
                this.updateCartDisplay();
            }
        }
    }

    updateCartDisplay() {
        const cartCount = document.getElementById('cart-count');
        const cartItems = document.getElementById('cart-items');
        const cartItemsCount = document.getElementById('cart-items-count');
        const cartTotalPrice = document.getElementById('cart-total-price');
        
        if (cartCount) {
            const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
            cartCount.textContent = totalItems;
        }
        
        if (cartItems) {
            if (this.cart.length === 0) {
                cartItems.innerHTML = `
                    <div style="text-align: center; padding: 2rem; color: #6b7280;">
                        <i class="fas fa-shopping-cart" style="font-size: 3rem; margin-bottom: 1rem;"></i>
                        <p>Корзина пуста</p>
                    </div>
                `;
            } else {
                cartItems.innerHTML = this.cart.map(item => `
                    <div class="cart-item">
                        <div class="cart-item-image">
                            <i class="fas fa-box"></i>
                        </div>
                        <div class="cart-item-details">
                            <div class="cart-item-name">${this.escapeHtml(item.name)}</div>
                            <div class="cart-item-price">${item.price.toLocaleString()} UZS</div>
                        </div>
                        <div class="cart-item-actions">
                            <button class="quantity-btn" onclick="shopPage.updateQuantity(${item.id}, ${item.quantity - 1})">-</button>
                            <span>${item.quantity}</span>
                            <button class="quantity-btn" onclick="shopPage.updateQuantity(${item.id}, ${item.quantity + 1})">+</button>
                        </div>
                    </div>
                `).join('');
            }
        }
        
        if (cartItemsCount) {
            const totalItems = this.cart.reduce((sum, item) => sum + item.quantity, 0);
            cartItemsCount.textContent = totalItems;
        }
        
        if (cartTotalPrice) {
            const totalPrice = this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0);
            cartTotalPrice.textContent = `${totalPrice.toLocaleString()} UZS`;
        }
    }

    toggleCart() {
        const sidebar = document.getElementById('cart-sidebar');
        const overlay = document.getElementById('cart-overlay');
        
        sidebar.classList.toggle('open');
        overlay.classList.toggle('open');
        document.body.style.overflow = sidebar.classList.contains('open') ? 'hidden' : 'auto';
    }

    closeCart() {
        const sidebar = document.getElementById('cart-sidebar');
        const overlay = document.getElementById('cart-overlay');
        
        sidebar.classList.remove('open');
        overlay.classList.remove('open');
        document.body.style.overflow = 'auto';
    }

    saveCartToStorage() {
        localStorage.setItem('commercio_cart', JSON.stringify(this.cart));
    }

    loadCartFromStorage() {
        const savedCart = localStorage.getItem('commercio_cart');
        if (savedCart) {
            this.cart = JSON.parse(savedCart);
        }
    }

    async checkout() {
        if (this.cart.length === 0) {
            this.showNotification('Корзина пуста', 'error');
            return;
        }
        
        try {
            const orderData = {
                buyer_id: 1, // In real app, get from user session
                shop_id: parseInt(this.shopId),
                items: this.cart.map(item => ({
                    product_id: item.id,
                    qty: item.quantity,
                    price: item.price
                })),
                total_amount: this.cart.reduce((sum, item) => sum + (item.price * item.quantity), 0)
            };
            
            const response = await fetch(`${this.apiBase}/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });
            
            if (response.ok) {
                const result = await response.json();
                this.cart = [];
                this.saveCartToStorage();
                this.updateCartDisplay();
                this.closeCart();
                this.showNotification('Заказ успешно оформлен!', 'success');
            } else {
                this.showNotification('Ошибка оформления заказа', 'error');
            }
        } catch (error) {
            console.error('Checkout error:', error);
            this.showNotification('Ошибка оформления заказа', 'error');
        }
    }

    viewProduct(productId) {
        const product = this.products.find(p => p.id === productId);
        if (product) {
            // In a real app, you might show a modal or navigate to product page
            this.showNotification(`Просмотр товара: ${product.name}`, 'info');
        }
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showNotification(message, type = 'info') {
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#10b981' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
            z-index: 3000;
            display: flex;
            align-items: center;
            gap: 0.5rem;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }

    showError(message) {
        const container = document.querySelector('.products-container .container');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem;">
                    <i class="fas fa-exclamation-triangle" style="font-size: 3rem; color: #ef4444; margin-bottom: 1rem;"></i>
                    <h3>Ошибка</h3>
                    <p>${message}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Обновить страницу</button>
                </div>
            `;
        }
    }
}

// Initialize shop page
document.addEventListener('DOMContentLoaded', () => {
    window.shopPage = new ShopPage();
}); 