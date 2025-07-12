// Commercio - Main JavaScript
class CommercioApp {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.currentUser = null;
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadInitialData();
        this.setupAnimations();
    }

    setupEventListeners() {
        // Header buttons
        document.getElementById('login-btn')?.addEventListener('click', () => this.showModal('login-modal'));
        document.getElementById('register-btn')?.addEventListener('click', () => this.showModal('register-modal'));
        
        // Modal close buttons
        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Close modal on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeModal(modal);
            });
        });

        // Forms
        document.getElementById('login-form')?.addEventListener('submit', (e) => this.handleLogin(e));
        document.getElementById('register-form')?.addEventListener('submit', (e) => this.handleRegister(e));

        // Navigation
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', (e) => this.smoothScroll(e));
        });

        // Action buttons
        document.getElementById('start-btn')?.addEventListener('click', () => this.handleStart());
        document.getElementById('demo-btn')?.addEventListener('click', () => this.handleDemo());
        document.getElementById('view-all-events')?.addEventListener('click', () => this.navigateToEvents());

        // Header scroll effect
        window.addEventListener('scroll', () => this.handleScroll());
    }

    setupAnimations() {
        // Intersection Observer for animations
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animate-in');
                }
            });
        }, { threshold: 0.1 });

        // Observe elements for animation
        document.querySelectorAll('.feature-card, .event-card, .partner-card, .shop-card').forEach(el => {
            observer.observe(el);
        });
    }

    async loadInitialData() {
        try {
            // Load events
            await this.loadEvents();
            
            // Load partners
            await this.loadPartners();
            
            // Load shops
            await this.loadShops();
            
        } catch (error) {
            console.error('Error loading initial data:', error);
        }
    }

    async loadEvents() {
        try {
            // Mock data for events - replace with actual API call
            const events = [
                {
                    id: 1,
                    title: 'Бизнес-встреча партнеров',
                    description: 'Ежемесячная встреча для обсуждения новых возможностей и стратегий развития',
                    date: '2024-02-15',
                    time: '18:00',
                    location: 'Ташкент, ул. Навои 15',
                    attendees: 45,
                    image: 'fas fa-handshake'
                },
                {
                    id: 2,
                    title: 'Мастер-класс по продажам',
                    description: 'Практические советы по увеличению продаж и работе с клиентами',
                    date: '2024-02-20',
                    time: '14:00',
                    location: 'Онлайн',
                    attendees: 120,
                    image: 'fas fa-chart-line'
                },
                {
                    id: 3,
                    title: 'Нетворкинг вечер',
                    description: 'Возможность познакомиться с другими предпринимателями и найти партнеров',
                    date: '2024-02-25',
                    time: '19:00',
                    location: 'Ташкент, Business Center',
                    attendees: 80,
                    image: 'fas fa-users'
                }
            ];

            this.renderEvents(events);
        } catch (error) {
            console.error('Error loading events:', error);
        }
    }

    renderEvents(events) {
        const container = document.getElementById('events-grid');
        if (!container) return;

        container.innerHTML = events.map(event => `
            <div class="event-card">
                <div class="event-image">
                    <i class="${event.image}"></i>
                </div>
                <div class="event-content">
                    <div class="event-date">${this.formatDate(event.date)} • ${event.time}</div>
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-description">${event.description}</p>
                    <div class="event-meta">
                        <span><i class="fas fa-map-marker-alt"></i> ${event.location}</span>
                        <span><i class="fas fa-users"></i> ${event.attendees} участников</span>
                    </div>
                </div>
            </div>
        `).join('');
    }

    async loadPartners() {
        try {
            // Mock data for partners - replace with actual API call
            const partners = [
                {
                    id: 1,
                    name: 'Алишер Усманов',
                    role: 'Основатель TechStart',
                    avatar: 'fas fa-user-tie',
                    stats: { projects: 15, revenue: '2.5M' }
                },
                {
                    id: 2,
                    name: 'Мария Петрова',
                    role: 'CEO FashionHub',
                    avatar: 'fas fa-user',
                    stats: { projects: 8, revenue: '1.8M' }
                },
                {
                    id: 3,
                    name: 'Дмитрий Козлов',
                    role: 'Директор FoodCorp',
                    avatar: 'fas fa-user-graduate',
                    stats: { projects: 12, revenue: '3.2M' }
                },
                {
                    id: 4,
                    name: 'Анна Сидорова',
                    role: 'Основатель EcoMarket',
                    avatar: 'fas fa-user-nurse',
                    stats: { projects: 6, revenue: '950K' }
                }
            ];

            this.renderPartners(partners);
        } catch (error) {
            console.error('Error loading partners:', error);
        }
    }

    renderPartners(partners) {
        const container = document.getElementById('partners-grid');
        if (!container) return;

        container.innerHTML = partners.map(partner => `
            <div class="partner-card">
                <div class="partner-avatar">
                    <i class="${partner.avatar}"></i>
                </div>
                <h3 class="partner-name">${partner.name}</h3>
                <div class="partner-role">${partner.role}</div>
                <div class="partner-stats">
                    <span>${partner.stats.projects} проектов</span>
                    <span>${partner.stats.revenue} UZS</span>
                </div>
            </div>
        `).join('');
    }

    async loadShops() {
        try {
            const response = await fetch(`${this.apiBase}/shops`);
            const shops = await response.json();
            
            // Get products for each shop to show count
            const shopsWithProducts = await Promise.all(
                shops.map(async (shop) => {
                    try {
                        const productsResponse = await fetch(`${this.apiBase}/products/${shop.id}`);
                        const products = await productsResponse.json();
                        return {
                            ...shop,
                            productCount: products.length,
                            rating: (Math.random() * 2 + 3).toFixed(1) // Mock rating
                        };
                    } catch (error) {
                        return { ...shop, productCount: 0, rating: '0.0' };
                    }
                })
            );

            this.renderShops(shopsWithProducts);
        } catch (error) {
            console.error('Error loading shops:', error);
            // Fallback to mock data
            this.renderShops([
                { id: 1, name: 'TechStore', productCount: 45, rating: '4.8' },
                { id: 2, name: 'FashionHub', productCount: 32, rating: '4.6' },
                { id: 3, name: 'FoodMarket', productCount: 28, rating: '4.9' }
            ]);
        }
    }

    renderShops(shops) {
        const container = document.getElementById('shops-grid');
        if (!container) return;

        container.innerHTML = shops.map(shop => `
            <div class="shop-card" onclick="window.location.href='shop.html?shop_id=${shop.id}'">
                <div class="shop-image">
                    <i class="fas fa-store"></i>
                </div>
                <div class="shop-content">
                    <h3 class="shop-name">${shop.name}</h3>
                    <div class="shop-category">Интернет-магазин</div>
                    <div class="shop-rating">
                        <i class="fas fa-star"></i>
                        <span>${shop.rating}</span>
                    </div>
                    <div class="shop-products">${shop.productCount} товаров</div>
                </div>
            </div>
        `).join('');
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
            document.body.style.overflow = 'auto';
        }
    }

    async handleLogin(e) {
        e.preventDefault();
        const username = document.getElementById('login-username').value;
        const password = document.getElementById('login-password').value;

        try {
            const response = await fetch(`${this.apiBase}/user_by_username/${username}`);
            if (response.ok) {
                const user = await response.json();
                if (user.password === password) { // In real app, use proper authentication
                    this.currentUser = user;
                    this.closeModal(document.getElementById('login-modal'));
                    this.updateHeaderForUser();
                    this.showNotification('Успешный вход!', 'success');
                } else {
                    this.showNotification('Неверный пароль', 'error');
                }
            } else {
                this.showNotification('Пользователь не найден', 'error');
            }
        } catch (error) {
            this.showNotification('Ошибка входа', 'error');
        }
    }

    async handleRegister(e) {
        e.preventDefault();
        const username = document.getElementById('register-username').value;
        const email = document.getElementById('register-email').value;
        const password = document.getElementById('register-password').value;
        const role = document.getElementById('register-role').value;

        try {
            const response = await fetch(`${this.apiBase}/user`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    telegram_id: Math.floor(Math.random() * 1000000), // Mock telegram_id
                    name: username,
                    role: role,
                    password: password
                })
            });

            if (response.ok) {
                this.closeModal(document.getElementById('register-modal'));
                this.showNotification('Регистрация успешна!', 'success');
            } else {
                const error = await response.json();
                this.showNotification(error.error === 'name taken' ? 'Имя пользователя занято' : 'Ошибка регистрации', 'error');
            }
        } catch (error) {
            this.showNotification('Ошибка регистрации', 'error');
        }
    }

    updateHeaderForUser() {
        const headerActions = document.querySelector('.header-actions');
        if (headerActions && this.currentUser) {
            headerActions.innerHTML = `
                <span class="user-welcome">Привет, ${this.currentUser.name}!</span>
                <button class="btn btn-secondary" onclick="app.logout()">
                    <i class="fas fa-sign-out-alt"></i>
                    Выйти
                </button>
            `;
        }
    }

    logout() {
        this.currentUser = null;
        location.reload();
    }

    handleStart() {
        if (this.currentUser) {
            window.location.href = 'dashboard.html';
        } else {
            this.showModal('register-modal');
        }
    }

    handleDemo() {
        // Show demo modal or navigate to demo page
        this.showNotification('Демо режим будет доступен скоро!', 'info');
    }

    navigateToEvents() {
        window.location.href = 'events.html';
    }

    smoothScroll(e) {
        e.preventDefault();
        const targetId = e.target.getAttribute('href').substring(1);
        const targetElement = document.getElementById(targetId);
        if (targetElement) {
            targetElement.scrollIntoView({ behavior: 'smooth' });
        }
    }

    handleScroll() {
        const header = document.querySelector('.header');
        if (window.scrollY > 100) {
            header.style.background = 'rgba(255, 255, 255, 0.98)';
            header.style.boxShadow = '0 2px 20px rgba(0, 0, 0, 0.1)';
        } else {
            header.style.background = 'rgba(255, 255, 255, 0.95)';
            header.style.boxShadow = 'none';
        }
    }

    formatDate(dateString) {
        const date = new Date(dateString);
        return date.toLocaleDateString('ru-RU', {
            day: 'numeric',
            month: 'long',
            year: 'numeric'
        });
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
            <span>${message}</span>
        `;

        // Add styles
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

        // Remove after 3 seconds
        setTimeout(() => {
            notification.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 3000);
    }
}

// Add CSS animations for notifications
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
    
    .animate-in {
        animation: fadeInUp 0.6s ease forwards;
    }
    
    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(30px); }
        to { opacity: 1; transform: translateY(0); }
    }
`;
document.head.appendChild(style);

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.app = new CommercioApp();
}); 