class PartnersApp {
    constructor() {
        this.apiBase = 'http://localhost:5000';
        this.partners = [];
        this.filters = {
            role: '',
            industry: ''
        };
        this.init();
    }

    async init() {
        this.setupEventListeners();
        await this.loadPartners();
        this.renderPartners();
    }

    setupEventListeners() {
        // Mobile menu toggle
        document.getElementById('mobile-menu-toggle')?.addEventListener('click', () => this.toggleMobileMenu());
        
        // Close mobile menu when clicking on nav links
        document.querySelectorAll('.nav-link').forEach(link => {
            link.addEventListener('click', () => this.closeMobileMenu());
        });

        // Filter controls
        document.getElementById('apply-filters')?.addEventListener('click', () => this.applyFilters());
        
        // Filter inputs
        document.getElementById('role-filter')?.addEventListener('change', (e) => {
            this.filters.role = e.target.value;
        });
        
        document.getElementById('industry-filter')?.addEventListener('change', (e) => {
            this.filters.industry = e.target.value;
        });

        // Modal controls
        document.querySelectorAll('.close').forEach(btn => {
            btn.addEventListener('click', (e) => this.closeModal(e.target.closest('.modal')));
        });

        // Close modal on outside click
        document.querySelectorAll('.modal').forEach(modal => {
            modal.addEventListener('click', (e) => {
                if (e.target === modal) this.closeModal(modal);
            });
        });

        // Become partner button
        document.getElementById('become-partner-btn')?.addEventListener('click', () => this.showModal('become-partner-modal'));
        
        // Become partner form
        document.getElementById('become-partner-form')?.addEventListener('submit', (e) => this.handleBecomePartner(e));
    }

    async loadPartners() {
        try {
            const response = await fetch(`${this.apiBase}/partners`);
            if (response.ok) {
                this.partners = await response.json();
            } else {
                // Mock data if API is not available
                this.partners = this.getMockPartners();
            }
        } catch (error) {
            console.error('Error loading partners:', error);
            this.partners = this.getMockPartners();
        }
    }

    getMockPartners() {
        return [
            {
                id: 1,
                name: 'Александр Петров',
                role: 'Основатель',
                company: 'TechStart',
                industry: 'tech',
                avatar: '👨‍💼',
                description: 'Основатель успешного стартапа в сфере технологий',
                experience: '8 лет',
                projects: 15,
                rating: 4.9
            },
            {
                id: 2,
                name: 'Мария Сидорова',
                role: 'CEO',
                company: 'FashionHub',
                industry: 'fashion',
                avatar: '👩‍💼',
                description: 'CEO крупной fashion-компании с оборотом $10M+',
                experience: '12 лет',
                projects: 28,
                rating: 4.8
            },
            {
                id: 3,
                name: 'Дмитрий Козлов',
                role: 'Директор',
                company: 'FoodCorp',
                industry: 'food',
                avatar: '👨‍🍳',
                description: 'Директор сети ресторанов быстрого питания',
                experience: '6 лет',
                projects: 22,
                rating: 4.7
            },
            {
                id: 4,
                name: 'Елена Воробьева',
                role: 'Консультант',
                company: 'FinancePro',
                industry: 'finance',
                avatar: '👩‍💻',
                description: 'Финансовый консультант с опытом работы в крупных банках',
                experience: '10 лет',
                projects: 45,
                rating: 4.9
            },
            {
                id: 5,
                name: 'Сергей Новиков',
                role: 'Менеджер',
                company: 'EduTech',
                industry: 'education',
                avatar: '👨‍🎓',
                description: 'Менеджер по развитию образовательных технологий',
                experience: '5 лет',
                projects: 18,
                rating: 4.6
            },
            {
                id: 6,
                name: 'Анна Морозова',
                role: 'Основатель',
                company: 'GreenTech',
                industry: 'tech',
                avatar: '👩‍🔬',
                description: 'Основатель экологичного технологического стартапа',
                experience: '7 лет',
                projects: 12,
                rating: 4.8
            }
        ];
    }

    renderPartners() {
        const grid = document.getElementById('partners-grid');
        if (!grid) return;

        const filteredPartners = this.getFilteredPartners();
        
        grid.innerHTML = filteredPartners.map(partner => `
            <div class="partner-card" data-partner-id="${partner.id}">
                <div class="partner-avatar">
                    <span style="font-size: 3rem;">${partner.avatar}</span>
                </div>
                <h3 class="partner-name">${partner.name}</h3>
                <p class="partner-role">${partner.role} • ${partner.company}</p>
                <p class="partner-description">${partner.description}</p>
                <div class="partner-stats">
                    <div class="stat">
                        <span class="stat-number">${partner.experience}</span>
                        <span class="stat-label">Опыт</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${partner.projects}</span>
                        <span class="stat-label">Проектов</span>
                    </div>
                    <div class="stat">
                        <span class="stat-number">${partner.rating}</span>
                        <span class="stat-label">Рейтинг</span>
                    </div>
                </div>
                <button class="btn btn-outline" onclick="partnersApp.contactPartner(${partner.id})">
                    <i class="fas fa-envelope"></i>
                    Связаться
                </button>
            </div>
        `).join('');
    }

    getFilteredPartners() {
        return this.partners.filter(partner => {
            if (this.filters.role && partner.role.toLowerCase() !== this.filters.role) {
                return false;
            }
            if (this.filters.industry && partner.industry !== this.filters.industry) {
                return false;
            }
            return true;
        });
    }

    applyFilters() {
        this.renderPartners();
        this.showNotification('Фильтры применены', 'success');
    }

    contactPartner(partnerId) {
        const partner = this.partners.find(p => p.id === partnerId);
        if (partner) {
            this.showNotification(`Открываем чат с ${partner.name}...`, 'info');
            // Here you would typically open a chat or contact form
        }
    }

    async handleBecomePartner(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('partner-name').value,
            role: document.getElementById('partner-role').value,
            company: document.getElementById('partner-company').value,
            email: document.getElementById('partner-email').value,
            phone: document.getElementById('partner-phone').value,
            description: document.getElementById('partner-description').value
        };

        try {
            // Here you would typically send to your API
            console.log('Partner application:', formData);
            
            this.closeModal(document.getElementById('become-partner-modal'));
            this.showNotification('Заявка отправлена! Мы свяжемся с вами в ближайшее время.', 'success');
            
            // Clear form
            e.target.reset();
            
        } catch (error) {
            this.showNotification('Ошибка отправки заявки. Попробуйте еще раз.', 'error');
        }
    }

    showModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'block';
        }
    }

    closeModal(modal) {
        if (modal) {
            modal.style.display = 'none';
        }
    }

    showNotification(message, type = 'info') {
        // Create notification element
        const notification = document.createElement('div');
        notification.className = `notification notification-${type}`;
        notification.innerHTML = `
            <div class="notification-content">
                <i class="fas fa-${type === 'success' ? 'check-circle' : type === 'error' ? 'exclamation-circle' : 'info-circle'}"></i>
                <span>${message}</span>
            </div>
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
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;
        
        // Add to page
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

    toggleMobileMenu() {
        const nav = document.getElementById('nav-menu');
        const toggle = document.getElementById('mobile-menu-toggle');
        
        if (nav && toggle) {
            nav.classList.toggle('active');
            
            // Change icon
            const icon = toggle.querySelector('i');
            if (icon) {
                if (nav.classList.contains('active')) {
                    icon.className = 'fas fa-times';
                } else {
                    icon.className = 'fas fa-bars';
                }
            }
        }
    }

    closeMobileMenu() {
        const nav = document.getElementById('nav-menu');
        const toggle = document.getElementById('mobile-menu-toggle');
        
        if (nav && toggle) {
            nav.classList.remove('active');
            
            // Reset icon
            const icon = toggle.querySelector('i');
            if (icon) {
                icon.className = 'fas fa-bars';
            }
        }
    }
}

// Add notification animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
    
    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
    
    .notification-content {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
`;
document.head.appendChild(style);

// Initialize app
const partnersApp = new PartnersApp(); 