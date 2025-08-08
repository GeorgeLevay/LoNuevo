// Main JavaScript file for Sistema de Rifas

// Utility functions
const Utils = {
    // Format currency
    formatCurrency: (amount) => {
        return new Intl.NumberFormat('es-MX', {
            style: 'currency',
            currency: 'MXN'
        }).format(amount);
    },

    // Format date
    formatDate: (date) => {
        return new Date(date).toLocaleDateString('es-MX', {
            year: 'numeric',
            month: 'long',
            day: 'numeric'
        });
    },

    // Show notification
    showNotification: (message, type = 'info') => {
        const alertDiv = document.createElement('div');
        alertDiv.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
        alertDiv.style.cssText = 'top: 20px; right: 20px; z-index: 9999; min-width: 300px;';
        alertDiv.innerHTML = `
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
        `;
        document.body.appendChild(alertDiv);
        
        // Auto remove after 5 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 5000);
    },

    // Confirm action
    confirmAction: (message, callback) => {
        if (confirm(message)) {
            callback();
        }
    },

    // Loading state
    setLoading: (element, loading = true) => {
        if (loading) {
            element.classList.add('loading');
            element.disabled = true;
        } else {
            element.classList.remove('loading');
            element.disabled = false;
        }
    }
};

// Form validation
const FormValidator = {
    // Validate email
    validateEmail: (email) => {
        const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        return re.test(email);
    },

    // Validate password strength
    validatePassword: (password) => {
        return password.length >= 6;
    },

    // Validate required fields
    validateRequired: (value) => {
        return value && value.trim().length > 0;
    },

    // Show field error
    showFieldError: (field, message) => {
        field.classList.add('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback') || 
                        document.createElement('div');
        errorDiv.className = 'invalid-feedback';
        errorDiv.textContent = message;
        if (!field.parentNode.querySelector('.invalid-feedback')) {
            field.parentNode.appendChild(errorDiv);
        }
    },

    // Clear field error
    clearFieldError: (field) => {
        field.classList.remove('is-invalid');
        const errorDiv = field.parentNode.querySelector('.invalid-feedback');
        if (errorDiv) {
            errorDiv.remove();
        }
    }
};

// Purchase form handler
const PurchaseForm = {
    init: () => {
        const quantitySelect = document.getElementById('quantity');
        const totalAmount = document.getElementById('total-amount');
        
        if (quantitySelect && totalAmount) {
            quantitySelect.addEventListener('change', PurchaseForm.updateTotal);
            PurchaseForm.updateTotal(); // Initial calculation
        }
    },

    updateTotal: () => {
        const quantitySelect = document.getElementById('quantity');
        const totalAmount = document.getElementById('total-amount');
        const pricePerTicket = parseFloat(document.querySelector('[data-price]')?.dataset.price || 0);
        
        if (quantitySelect && totalAmount && pricePerTicket) {
            const quantity = parseInt(quantitySelect.value);
            const total = quantity * pricePerTicket;
            totalAmount.textContent = Utils.formatCurrency(total);
        }
    }
};

// Admin functions
const AdminPanel = {
    // Approve purchase
    approvePurchase: (purchaseId) => {
        Utils.confirmAction('¿Confirmar aprobación de esta compra?', () => {
            window.location.href = `/admin/approve_purchase/${purchaseId}`;
        });
    },

    // Reject purchase
    rejectPurchase: (purchaseId) => {
        Utils.confirmAction('¿Confirmar rechazo de esta compra?', () => {
            window.location.href = `/admin/reject_purchase/${purchaseId}`;
        });
    },

    // Delete raffle
    deleteRaffle: (raffleId) => {
        Utils.confirmAction('¿Estás seguro de que quieres eliminar esta rifa? Esta acción no se puede deshacer.', () => {
            // Implement delete functionality
            Utils.showNotification('Función de eliminación en desarrollo', 'warning');
        });
    },

    // Edit raffle
    editRaffle: (raffleId) => {
        // Implement edit functionality
        Utils.showNotification('Función de edición en desarrollo', 'info');
    }
};

// Search and filter functionality
const SearchFilter = {
    init: () => {
        const searchInput = document.getElementById('searchInput');
        if (searchInput) {
            searchInput.addEventListener('input', SearchFilter.performSearch);
        }
    },

    performSearch: (event) => {
        const searchTerm = event.target.value.toLowerCase();
        const items = document.querySelectorAll('[data-searchable]');
        
        items.forEach(item => {
            const text = item.textContent.toLowerCase();
            if (text.includes(searchTerm)) {
                item.style.display = '';
            } else {
                item.style.display = 'none';
            }
        });
    }
};

// Auto-hide alerts
const AlertManager = {
    init: () => {
        const alerts = document.querySelectorAll('.alert');
        alerts.forEach(alert => {
            setTimeout(() => {
                if (alert.parentNode) {
                    const bsAlert = new bootstrap.Alert(alert);
                    bsAlert.close();
                }
            }, 5000);
        });
    }
};

// Initialize everything when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize all components
    PurchaseForm.init();
    SearchFilter.init();
    AlertManager.init();

    // Add smooth scrolling to all links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function (e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({
                    behavior: 'smooth',
                    block: 'start'
                });
            }
        });
    });

    // Add loading states to forms
    document.querySelectorAll('form').forEach(form => {
        form.addEventListener('submit', function() {
            const submitBtn = this.querySelector('button[type="submit"]');
            if (submitBtn) {
                Utils.setLoading(submitBtn, true);
            }
        });
    });

    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Initialize popovers
    const popoverTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="popover"]'));
    popoverTriggerList.map(function (popoverTriggerEl) {
        return new bootstrap.Popover(popoverTriggerEl);
    });

    // Add animation to cards on scroll
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);

    document.querySelectorAll('.card').forEach(card => {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        card.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
        observer.observe(card);
    });
});

// Export for global use
window.Utils = Utils;
window.FormValidator = FormValidator;
window.PurchaseForm = PurchaseForm;
window.AdminPanel = AdminPanel;
window.SearchFilter = SearchFilter; 