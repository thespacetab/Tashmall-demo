// Events Page JavaScript
class EventsPage {
    constructor() {
        this.apiBase = 'http://localhost:8000/api';
        this.currentPage = 1;
        this.eventsPerPage = 6;
        this.allEvents = [];
        this.filteredEvents = [];
        this.filters = {
            category: '',
            date: '',
            status: ''
        };
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.loadEvents();
    }

    setupEventListeners() {
        // Filter controls
        document.getElementById('apply-filters')?.addEventListener('click', () => this.applyFilters());
        
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

        // Registration form
        document.getElementById('registration-form')?.addEventListener('submit', (e) => this.handleRegistration(e));
    }

    async loadEvents() {
        try {
            // Mock data for events - replace with actual API call
            this.allEvents = [
                {
                    id: 1,
                    title: 'Бизнес-встреча партнеров',
                    description: 'Ежемесячная встреча для обсуждения новых возможностей и стратегий развития бизнеса. Приглашаем всех партнеров и заинтересованных предпринимателей.',
                    category: 'business',
                    date: '2024-02-15',
                    time: '18:00',
                    location: 'Ташкент, ул. Навои 15, Business Center',
                    attendees: 45,
                    maxAttendees: 60,
                    status: 'upcoming',
                    image: 'fas fa-handshake',
                    organizer: 'Commercio Team',
                    price: 'Бесплатно',
                    tags: ['бизнес', 'нетворкинг', 'партнерство']
                },
                {
                    id: 2,
                    title: 'Мастер-класс по продажам',
                    description: 'Практические советы по увеличению продаж и работе с клиентами. Разберем современные техники продаж и маркетинговые стратегии.',
                    category: 'education',
                    date: '2024-02-20',
                    time: '14:00',
                    location: 'Онлайн (Zoom)',
                    attendees: 120,
                    maxAttendees: 200,
                    status: 'upcoming',
                    image: 'fas fa-chart-line',
                    organizer: 'Sales Academy',
                    price: '50,000 UZS',
                    tags: ['продажи', 'маркетинг', 'обучение']
                },
                {
                    id: 3,
                    title: 'Нетворкинг вечер',
                    description: 'Возможность познакомиться с другими предпринимателями и найти партнеров для совместных проектов. Неформальная атмосфера.',
                    category: 'networking',
                    date: '2024-02-25',
                    time: '19:00',
                    location: 'Ташкент, Business Center, 3 этаж',
                    attendees: 80,
                    maxAttendees: 100,
                    status: 'upcoming',
                    image: 'fas fa-users',
                    organizer: 'Business Network',
                    price: '30,000 UZS',
                    tags: ['нетворкинг', 'партнерство', 'сообщество']
                },
                {
                    id: 4,
                    title: 'Цифровой маркетинг 2024',
                    description: 'Актуальные тренды в цифровом маркетинге. SMM, контекстная реклама, email-маркетинг и аналитика.',
                    category: 'marketing',
                    date: '2024-02-10',
                    time: '15:00',
                    location: 'Ташкент, IT Park',
                    attendees: 95,
                    maxAttendees: 120,
                    status: 'ongoing',
                    image: 'fas fa-bullhorn',
                    organizer: 'Digital Marketing Pro',
                    price: '75,000 UZS',
                    tags: ['маркетинг', 'цифровой', 'SMM']
                },
                {
                    id: 5,
                    title: 'Стартап питчинг',
                    description: 'Презентация стартапов перед инвесторами. Возможность получить финансирование и менторскую поддержку.',
                    category: 'business',
                    date: '2024-02-05',
                    time: '16:00',
                    location: 'Ташкент, Innovation Center',
                    attendees: 150,
                    maxAttendees: 200,
                    status: 'completed',
                    image: 'fas fa-rocket',
                    organizer: 'Startup Hub',
                    price: '100,000 UZS',
                    tags: ['стартап', 'инвестиции', 'питчинг']
                },
                {
                    id: 6,
                    title: 'Финансовое планирование',
                    description: 'Основы финансового планирования для малого и среднего бизнеса. Бюджетирование, учет и оптимизация расходов.',
                    category: 'education',
                    date: '2024-02-28',
                    time: '13:00',
                    location: 'Ташкент, Financial District',
                    attendees: 35,
                    maxAttendees: 50,
                    status: 'upcoming',
                    image: 'fas fa-calculator',
                    organizer: 'Finance Academy',
                    price: '45,000 UZS',
                    tags: ['финансы', 'планирование', 'бюджет']
                }
            ];

            this.filteredEvents = [...this.allEvents];
            this.renderEvents();
            this.renderPagination();
        } catch (error) {
            console.error('Error loading events:', error);
            this.showNotification('Ошибка загрузки мероприятий', 'error');
        }
    }

    applyFilters() {
        const category = document.getElementById('category-filter').value;
        const date = document.getElementById('date-filter').value;
        const status = document.getElementById('status-filter').value;

        this.filters = { category, date, status };
        this.currentPage = 1;

        this.filteredEvents = this.allEvents.filter(event => {
            let matches = true;

            if (category && event.category !== category) {
                matches = false;
            }

            if (date && event.date !== date) {
                matches = false;
            }

            if (status && event.status !== status) {
                matches = false;
            }

            return matches;
        });

        this.renderEvents();
        this.renderPagination();
    }

    renderEvents() {
        const container = document.getElementById('events-grid');
        if (!container) return;

        const startIndex = (this.currentPage - 1) * this.eventsPerPage;
        const endIndex = startIndex + this.eventsPerPage;
        const eventsToShow = this.filteredEvents.slice(startIndex, endIndex);

        if (eventsToShow.length === 0) {
            container.innerHTML = `
                <div style="grid-column: 1 / -1; text-align: center; padding: 3rem;">
                    <i class="fas fa-calendar-times" style="font-size: 3rem; color: #9ca3af; margin-bottom: 1rem;"></i>
                    <h3>Мероприятия не найдены</h3>
                    <p>Попробуйте изменить фильтры поиска</p>
                </div>
            `;
            return;
        }

        container.innerHTML = eventsToShow.map(event => `
            <div class="event-card-large">
                <div class="event-image-large">
                    <i class="${event.image}"></i>
                    <div class="event-status ${event.status}">
                        ${this.getStatusText(event.status)}
                    </div>
                </div>
                <div class="event-content-large">
                    <div class="event-meta-large">
                        <span><i class="fas fa-calendar"></i> ${this.formatDate(event.date)} • ${event.time}</span>
                        <span><i class="fas fa-users"></i> ${event.attendees}/${event.maxAttendees}</span>
                    </div>
                    <h3 class="event-title">${event.title}</h3>
                    <p class="event-description">${event.description.substring(0, 120)}${event.description.length > 120 ? '...' : ''}</p>
                    <div class="event-meta-large">
                        <span><i class="fas fa-map-marker-alt"></i> ${event.location}</span>
                        <span><i class="fas fa-tag"></i> ${event.price}</span>
                    </div>
                    <div class="event-actions">
                        <button class="btn-register" onclick="eventsPage.showEventDetails(${event.id})">
                            <i class="fas fa-info-circle"></i>
                            Подробнее
                        </button>
                        <button class="btn-register" onclick="eventsPage.registerForEvent(${event.id})" 
                                ${event.status === 'completed' ? 'disabled' : ''}>
                            <i class="fas fa-user-plus"></i>
                            ${event.status === 'completed' ? 'Завершено' : 'Регистрация'}
                        </button>
                    </div>
                </div>
            </div>
        `).join('');
    }

    renderPagination() {
        const container = document.getElementById('pagination');
        if (!container) return;

        const totalPages = Math.ceil(this.filteredEvents.length / this.eventsPerPage);
        
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let paginationHTML = '';

        // Previous button
        if (this.currentPage > 1) {
            paginationHTML += `<button class="page-btn" onclick="eventsPage.goToPage(${this.currentPage - 1})">
                <i class="fas fa-chevron-left"></i>
            </button>`;
        }

        // Page numbers
        for (let i = 1; i <= totalPages; i++) {
            if (i === 1 || i === totalPages || (i >= this.currentPage - 1 && i <= this.currentPage + 1)) {
                paginationHTML += `<button class="page-btn ${i === this.currentPage ? 'active' : ''}" 
                    onclick="eventsPage.goToPage(${i})">${i}</button>`;
            } else if (i === this.currentPage - 2 || i === this.currentPage + 2) {
                paginationHTML += `<span class="page-btn">...</span>`;
            }
        }

        // Next button
        if (this.currentPage < totalPages) {
            paginationHTML += `<button class="page-btn" onclick="eventsPage.goToPage(${this.currentPage + 1})">
                <i class="fas fa-chevron-right"></i>
            </button>`;
        }

        container.innerHTML = paginationHTML;
    }

    goToPage(page) {
        this.currentPage = page;
        this.renderEvents();
        this.renderPagination();
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }

    showEventDetails(eventId) {
        const event = this.allEvents.find(e => e.id === eventId);
        if (!event) return;

        const modal = document.getElementById('event-modal');
        const detailsContainer = document.getElementById('event-details');

        detailsContainer.innerHTML = `
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 2rem;">
                <div>
                    <div class="event-image-large">
                        <i class="${event.image}"></i>
                        <div class="event-status ${event.status}">
                            ${this.getStatusText(event.status)}
                        </div>
                    </div>
                </div>
                <div>
                    <h2 style="margin-bottom: 1rem; color: #1f2937;">${event.title}</h2>
                    <p style="color: #6b7280; line-height: 1.6; margin-bottom: 1.5rem;">${event.description}</p>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Организатор:</strong> ${event.organizer}
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Дата и время:</strong> ${this.formatDate(event.date)} в ${event.time}
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Место:</strong> ${event.location}
                    </div>
                    
                    <div style="margin-bottom: 1rem;">
                        <strong>Стоимость:</strong> ${event.price}
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <strong>Участники:</strong> ${event.attendees}/${event.maxAttendees}
                    </div>
                    
                    <div style="margin-bottom: 1.5rem;">
                        <strong>Теги:</strong>
                        <div style="display: flex; gap: 0.5rem; flex-wrap: wrap; margin-top: 0.5rem;">
                            ${event.tags.map(tag => `<span style="background: #f3f4f6; padding: 0.25rem 0.75rem; border-radius: 20px; font-size: 0.8rem;">${tag}</span>`).join('')}
                        </div>
                    </div>
                    
                    <button class="btn-register" onclick="eventsPage.registerForEvent(${event.id})" 
                            ${event.status === 'completed' ? 'disabled' : ''}>
                        <i class="fas fa-user-plus"></i>
                        ${event.status === 'completed' ? 'Мероприятие завершено' : 'Зарегистрироваться'}
                    </button>
                </div>
            </div>
        `;

        modal.style.display = 'block';
        document.body.style.overflow = 'hidden';
    }

    registerForEvent(eventId) {
        const event = this.allEvents.find(e => e.id === eventId);
        if (!event || event.status === 'completed') return;

        // Store event ID for registration form
        window.currentEventId = eventId;
        
        // Pre-fill form if user is logged in
        if (window.app && window.app.currentUser) {
            document.getElementById('reg-name').value = window.app.currentUser.name;
        }

        this.closeModal(document.getElementById('event-modal'));
        this.showModal('registration-modal');
    }

    async handleRegistration(e) {
        e.preventDefault();
        
        const formData = {
            name: document.getElementById('reg-name').value,
            email: document.getElementById('reg-email').value,
            phone: document.getElementById('reg-phone').value,
            company: document.getElementById('reg-company').value,
            eventId: window.currentEventId
        };

        try {
            // Here you would typically send to your API
            console.log('Registration data:', formData);
            
            // Mock successful registration
            this.closeModal(document.getElementById('registration-modal'));
            this.showNotification('Регистрация успешна! Проверьте email для подтверждения.', 'success');
            
            // Update event attendees count
            const event = this.allEvents.find(e => e.id === window.currentEventId);
            if (event && event.attendees < event.maxAttendees) {
                event.attendees++;
                this.renderEvents();
            }
            
            // Clear form
            e.target.reset();
            
        } catch (error) {
            this.showNotification('Ошибка регистрации. Попробуйте еще раз.', 'error');
        }
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

    getStatusText(status) {
        const statusMap = {
            'upcoming': 'Предстоящее',
            'ongoing': 'Текущее',
            'completed': 'Завершено'
        };
        return statusMap[status] || status;
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
}

// Initialize events page
document.addEventListener('DOMContentLoaded', () => {
    window.eventsPage = new EventsPage();
}); 