// Main JavaScript File - Common Utilities

class MedFindApp {
    constructor() {
        this.init();
    }

    init() {
        this.setupEventListeners();
        this.initComponents();
        this.checkAuthStatus();
    }

    setupEventListeners() {
        // Initialize tooltips
        this.initTooltips();
        
        // Initialize dropdowns
        this.initDropdowns();
        
        // Initialize modals
        this.initModals();
    }

    initComponents() {
        // Load common components
        this.loadCommonComponents();
        
        // Initialize search functionality
        this.initSearch();
        
        // Initialize notifications
        this.initNotifications();
    }

    checkAuthStatus() {
        const user = localStorage.getItem('medfind_user');
        if (user) {
            this.updateUIForLoggedInUser(JSON.parse(user));
        }
    }

    updateUIForLoggedInUser(user) {
        // Update navbar with user info
        const userElements = document.querySelectorAll('.user-name, .nav-user-name');
        userElements.forEach(el => {
            if (el.classList.contains('user-name')) {
                el.textContent = user.name.split(' ')[0];
            }
        });
        
        // Show/hide login/logout buttons
        const loginBtn = document.querySelector('.login-btn');
        const logoutBtn = document.querySelector('.logout-btn');
        
        if (loginBtn) loginBtn.style.display = 'none';
        if (logoutBtn) logoutBtn.style.display = 'flex';
    }

    initTooltips() {
        const tooltips = document.querySelectorAll('[data-tooltip]');
        tooltips.forEach(tooltip => {
            tooltip.addEventListener('mouseenter', (e) => {
                const text = e.target.getAttribute('data-tooltip');
                this.showTooltip(e.target, text);
            });
            
            tooltip.addEventListener('mouseleave', () => {
                this.hideTooltip();
            });
        });
    }

    showTooltip(element, text) {
        const tooltip = document.createElement('div');
        tooltip.className = 'tooltip';
        tooltip.textContent = text;
        
        const rect = element.getBoundingClientRect();
        tooltip.style.position = 'fixed';
        tooltip.style.top = (rect.top - 40) + 'px';
        tooltip.style.left = (rect.left + rect.width / 2) + 'px';
        tooltip.style.transform = 'translateX(-50%)';
        
        document.body.appendChild(tooltip);
        
        element.tooltipElement = tooltip;
    }

    hideTooltip() {
        const tooltip = document.querySelector('.tooltip');
        if (tooltip) {
            tooltip.remove();
        }
    }

    initDropdowns() {
        const dropdowns = document.querySelectorAll('.dropdown-toggle');
        dropdowns.forEach(dropdown => {
            dropdown.addEventListener('click', (e) => {
                e.preventDefault();
                const menu = dropdown.nextElementSibling;
                menu.style.display = menu.style.display === 'block' ? 'none' : 'block';
            });
        });
        
        // Close dropdowns when clicking outside
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.dropdown')) {
                document.querySelectorAll('.dropdown-menu').forEach(menu => {
                    menu.style.display = 'none';
                });
            }
        });
    }

    initModals() {
        const modalTriggers = document.querySelectorAll('[data-modal]');
        modalTriggers.forEach(trigger => {
            trigger.addEventListener('click', (e) => {
                e.preventDefault();
                const modalId = trigger.getAttribute('data-modal');
                this.openModal(modalId);
            });
        });
        
        // Close modal buttons
        const closeButtons = document.querySelectorAll('.modal-close, [data-dismiss="modal"]');
        closeButtons.forEach(button => {
            button.addEventListener('click', () => {
                this.closeModal();
            });
        });
        
        // Close modal when clicking outside
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('modal')) {
                this.closeModal();
            }
        });
    }

    openModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) {
            modal.style.display = 'flex';
            document.body.style.overflow = 'hidden';
        }
    }

    closeModal() {
        const modals = document.querySelectorAll('.modal');
        modals.forEach(modal => {
            modal.style.display = 'none';
        });
        document.body.style.overflow = 'auto';
    }

    initSearch() {
        const searchForms = document.querySelectorAll('.search-form');
        searchForms.forEach(form => {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const input = form.querySelector('input[type="text"]');
                const query = input.value.trim();
                
                if (query) {
                    this.performSearch(query);
                }
            });
        });
    }

    performSearch(query) {
        // In production, this would make an API call
        console.log('Searching for:', query);
        
        // Show loading state
        this.showLoading('Searching...');
        
        // Simulate API delay
        setTimeout(() => {
            this.hideLoading();
            
            // For now, redirect to search results page
            window.location.href = `search-results.html?q=${encodeURIComponent(query)}`;
        }, 1000);
    }

    initNotifications() {
        // Check for new notifications
        this.checkNotifications();
        
        // Initialize notification dropdown
        const notificationBtn = document.querySelector('.notification-btn');
        if (notificationBtn) {
            notificationBtn.addEventListener('click', (e) => {
                e.preventDefault();
                this.toggleNotificationDropdown();
            });
        }
    }

    checkNotifications() {
        // In production, check for new notifications via API
        const unreadCount = 3; // Example count
        
        const badge = document.querySelector('.notification-badge');
        if (badge) {
            badge.textContent = unreadCount;
            badge.style.display = unreadCount > 0 ? 'flex' : 'none';
        }
    }

    toggleNotificationDropdown() {
        const dropdown = document.querySelector('.notification-dropdown');
        if (dropdown) {
            dropdown.style.display = dropdown.style.display === 'block' ? 'none' : 'block';
        }
    }

    loadCommonComponents() {
        // Load navbar if container exists
        const navbarContainer = document.getElementById('navbar-container');
        if (navbarContainer && !navbarContainer.innerHTML) {
            this.loadComponent('../Components/navbar.html', 'navbar-container');
        }
        
        // Load footer if container exists
        const footerContainer = document.getElementById('footer-container');
        if (footerContainer && !footerContainer.innerHTML) {
            this.loadComponent('../Components/footer.html', 'footer-container');
        }
    }

    async loadComponent(url, containerId) {
        try {
            const response = await fetch(url);
            if (!response.ok) throw new Error('Component not found');
            
            const html = await response.text();
            document.getElementById(containerId).innerHTML = html;
            
            // Re-initialize components in loaded HTML
            this.initDropdowns();
            this.initModals();
            
        } catch (error) {
            console.error('Error loading component:', error);
        }
    }

    showLoading(message = 'Loading...') {
        // Create loading overlay
        const loadingOverlay = document.createElement('div');
        loadingOverlay.className = 'loading-overlay';
        loadingOverlay.innerHTML = `
            <div class="loading-spinner">
                <div class="spinner"></div>
                <div class="loading-text">${message}</div>
            </div>
        `;
        
        document.body.appendChild(loadingOverlay);
    }

    hideLoading() {
        const loadingOverlay = document.querySelector('.loading-overlay');
        if (loadingOverlay) {
            loadingOverlay.remove();
        }
    }

    showToast(message, type = 'info', duration = 3000) {
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.innerHTML = `
            <div class="toast-content">
                <i class="fas fa-${this.getToastIcon(type)}"></i>
                <span>${message}</span>
            </div>
            <button class="toast-close">&times;</button>
        `;
        
        const container = document.querySelector('.toast-container') || this.createToastContainer();
        container.appendChild(toast);
        
        // Animate in
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Auto remove
        setTimeout(() => {
            this.removeToast(toast);
        }, duration);
        
        // Close button
        const closeBtn = toast.querySelector('.toast-close');
        closeBtn.addEventListener('click', () => {
            this.removeToast(toast);
        });
    }

    getToastIcon(type) {
        const icons = {
            success: 'check-circle',
            error: 'exclamation-circle',
            warning: 'exclamation-triangle',
            info: 'info-circle'
        };
        return icons[type] || 'info-circle';
    }

    createToastContainer() {
        const container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
        return container;
    }

    removeToast(toast) {
        toast.classList.remove('show');
        toast.classList.add('hide');
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }

    // Utility functions
    formatDate(date) {
        return new Date(date).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        });
    }

    formatTime(time) {
        return new Date(`2000-01-01T${time}`).toLocaleTimeString('en-US', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    debounce(func, wait) {
        let timeout;
        return function executedFunction(...args) {
            const later = () => {
                clearTimeout(timeout);
                func(...args);
            };
            clearTimeout(timeout);
            timeout = setTimeout(later, wait);
        };
    }

    throttle(func, limit) {
        let inThrottle;
        return function() {
            const args = arguments;
            const context = this;
            if (!inThrottle) {
                func.apply(context, args);
                inThrottle = true;
                setTimeout(() => inThrottle = false, limit);
            }
        };
    }

    // Form validation
    validateForm(form) {
        const inputs = form.querySelectorAll('input, select, textarea');
        let isValid = true;
        
        inputs.forEach(input => {
            if (!this.validateField(input)) {
                isValid = false;
            }
        });
        
        return isValid;
    }

    validateField(field) {
        const value = field.value.trim();
        const type = field.type;
        const required = field.required;
        
        // Clear previous errors
        this.clearFieldError(field);
        
        // Check required fields
        if (required && !value) {
            this.showFieldError(field, 'This field is required');
            return false;
        }
        
        // Validate based on type
        switch (type) {
            case 'email':
                if (value && !this.isValidEmail(value)) {
                    this.showFieldError(field, 'Please enter a valid email address');
                    return false;
                }
                break;
                
            case 'tel':
                if (value && !this.isValidPhone(value)) {
                    this.showFieldError(field, 'Please enter a valid phone number');
                    return false;
                }
                break;
                
            case 'password':
                if (value && value.length < 6) {
                    this.showFieldError(field, 'Password must be at least 6 characters');
                    return false;
                }
                break;
        }
        
        // Custom validation for data attributes
        if (field.hasAttribute('data-min-length')) {
            const minLength = parseInt(field.getAttribute('data-min-length'));
            if (value.length < minLength) {
                this.showFieldError(field, `Must be at least ${minLength} characters`);
                return false;
            }
        }
        
        return true;
    }

    isValidEmail(email) {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    }

    isValidPhone(phone) {
        const re = /^[\+]?[0-9\s\-\(\)]{10,}$/;
        return re.test(phone);
    }

    showFieldError(field, message) {
        field.classList.add('is-invalid');
        
        const errorDiv = document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        
        field.parentNode.appendChild(errorDiv);
    }

    clearFieldError(field) {
        field.classList.remove('is-invalid');
        
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }

    // API calls
    async apiRequest(endpoint, method = 'GET', data = null) {
        const baseURL = 'http://localhost:3000/api'; // Update with your backend URL
        const url = `${baseURL}${endpoint}`;
        
        const options = {
            method,
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('medfind_token')}`
            }
        };
        
        if (data && (method === 'POST' || method === 'PUT' || method === 'PATCH')) {
            options.body = JSON.stringify(data);
        }
        
        try {
            const response = await fetch(url, options);
            const result = await response.json();
            
            if (!response.ok) {
                throw new Error(result.message || 'API request failed');
            }
            
            return result;
        } catch (error) {
            console.error('API Request Error:', error);
            this.showToast(error.message, 'error');
            throw error;
        }
    }

    // Local storage utilities
    setLocalStorage(key, value) {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (error) {
            console.error('Error saving to localStorage:', error);
        }
    }

    getLocalStorage(key) {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (error) {
            console.error('Error reading from localStorage:', error);
            return null;
        }
    }

    removeLocalStorage(key) {
        localStorage.removeItem(key);
    }

    // Authentication
    async login(email, password) {
        try {
            this.showLoading('Logging in...');
            
            const response = await this.apiRequest('/auth/login', 'POST', {
                email,
                password
            });
            
            // Store user data
            this.setLocalStorage('medfind_user', response.user);
            this.setLocalStorage('medfind_token', response.token);
            
            this.showToast('Login successful!', 'success');
            
            // Redirect based on role
            setTimeout(() => {
                switch (response.user.role) {
                    case 'patient':
                        window.location.href = '../patients/patient-dashboard.html';
                        break;
                    case 'doctor':
                        window.location.href = '../doctors/doctor-dashboard.html';
                        break;
                    case 'admin':
                        window.location.href = '../admin/admin-dashboard.html';
                        break;
                    default:
                        window.location.href = '../index.html';
                }
            }, 1000);
            
            return response;
        } catch (error) {
            throw error;
        } finally {
            this.hideLoading();
        }
    }

    logout() {
        this.removeLocalStorage('medfind_user');
        this.removeLocalStorage('medfind_token');
        this.showToast('Logged out successfully', 'info');
        setTimeout(() => {
            window.location.href = '../index.html';
        }, 1000);
    }

    // Search functionality
    async searchDoctors(query, filters = {}) {
        const params = new URLSearchParams({
            q: query,
            ...filters
        });
        
        return await this.apiRequest(`/doctors/search?${params}`);
    }

    async searchHospitals(query, filters = {}) {
        const params = new URLSearchParams({
            q: query,
            ...filters
        });
        
        return await this.apiRequest(`/hospitals/search?${params}`);
    }

    // Appointment booking
    async bookAppointment(appointmentData) {
        return await this.apiRequest('/appointments', 'POST', appointmentData);
    }

    async getAppointments(userId, filters = {}) {
        const params = new URLSearchParams(filters);
        return await this.apiRequest(`/appointments/user/${userId}?${params}`);
    }

    // Medical records
    async getMedicalRecords(patientId) {
        return await this.apiRequest(`/medical-records/${patientId}`);
    }

    async uploadMedicalRecord(recordData) {
        return await this.apiRequest('/medical-records', 'POST', recordData);
    }
}

// Initialize app when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.MedFind = new MedFindApp();
});

// Export for module usage
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MedFindApp;
}
// Load common components (Navbar, Footer)
document.addEventListener("DOMContentLoaded", () => {

    // Navbar load
    const navbar = document.getElementById("navbar-container");
    if (navbar) {
        fetch("../components/navbar.html")
            .then(res => res.text())
            .then(data => navbar.innerHTML = data);
    }

    // Footer load
    const footer = document.getElementById("footer-container");
    if (footer) {
        fetch("../components/footer.html")
            .then(res => res.text())
            .then(data => footer.innerHTML = data);
    }

});
