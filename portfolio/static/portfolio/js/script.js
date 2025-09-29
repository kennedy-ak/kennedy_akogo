// Clean Professional Portfolio JavaScript

document.addEventListener('DOMContentLoaded', function() {
    // Set dark theme
    const htmlElement = document.documentElement;
    htmlElement.setAttribute('data-bs-theme', 'dark');
    
    // Initialize minimal interactions
    initSmoothScrolling();
    initFormValidation();
    
    console.log('✅ Clean portfolio loaded');
});

// Smooth scrolling for navigation links
function initSmoothScrolling() {
    const navLinks = document.querySelectorAll('a[href^="#"]');
    
    navLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const targetId = this.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const offsetTop = targetElement.offsetTop - 80;
                window.scrollTo({
                    top: offsetTop,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// Basic form validation
function initFormValidation() {
    const forms = document.querySelectorAll('form');
    
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                    field.classList.add('is-valid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
}

// Simple navbar background change on scroll
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const navbar = document.querySelector('.navbar');
    
    if (navbar) {
        if (scrolled > 50) {
            navbar.style.background = 'rgba(26, 26, 26, 0.95)';
            navbar.style.backdropFilter = 'blur(10px)';
        } else {
            navbar.style.background = 'rgba(26, 26, 26, 0.8)';
        }
    }
});

// Page load completion
window.addEventListener('load', function() {
    console.log('🚀 Professional portfolio fully loaded');
});