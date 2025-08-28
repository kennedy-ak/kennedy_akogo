// Professional Portfolio JavaScript with Vibrant Animations

document.addEventListener('DOMContentLoaded', function() {
    // Force dark theme for vibrant color palette
    const htmlElement = document.documentElement;
    htmlElement.setAttribute('data-bs-theme', 'dark');
    
    // Initialize all animations and interactions
    initScrollAnimations();
    initCardAnimations();
    initButtonAnimations();
    initProgressiveLoading();
    initSmoothScrolling();
    initRippleEffects();
    
    console.log('🎨 Vibrant portfolio loaded with professional animations!');
});

// Scroll-triggered animations with Intersection Observer
function initScrollAnimations() {
    const observerOptions = {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    };
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('revealed');
                // Add slight random delay for natural effect
                entry.target.style.animationDelay = Math.random() * 0.2 + 's';
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, observerOptions);
    
    // Observe elements with animation classes
    const animatedElements = document.querySelectorAll('.fade-in, .fade-in-left, .fade-in-right, .bounce-in, .scale-in, .slide-up, .scroll-reveal, .card');
    animatedElements.forEach(el => {
        observer.observe(el);
    });
    
    // Stagger animation for multiple items
    document.querySelectorAll('.stagger-item').forEach((el, index) => {
        el.style.animationDelay = `${index * 0.1}s`;
        observer.observe(el);
    });
}

// Enhanced card interactions with professional hover effects
function initCardAnimations() {
    const cards = document.querySelectorAll('.card');
    
    cards.forEach((card, index) => {
        // Progressive reveal with stagger
        card.style.animationDelay = `${index * 0.1}s`;
        
        // Enhanced hover effects
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-12px) scale(1.03)';
            this.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
            this.style.boxShadow = '0 25px 50px -12px rgba(0, 0, 0, 0.35), 0 0 30px rgba(99, 102, 241, 0.3)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
            this.style.boxShadow = '0 10px 15px -3px rgba(0, 0, 0, 0.2), 0 4px 6px -2px rgba(0, 0, 0, 0.1)';
        });
        
        // Add subtle rotation on hover for project cards
        if (card.classList.contains('project-card')) {
            card.addEventListener('mouseenter', function() {
                this.style.transform = 'translateY(-12px) scale(1.03) rotate(1deg)';
            });
            
            card.addEventListener('mouseleave', function() {
                this.style.transform = 'translateY(0) scale(1) rotate(0deg)';
            });
        }
    });
}

// Professional button animations
function initButtonAnimations() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        // Enhanced hover effect
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-6px) scale(1.05)';
            this.style.transition = 'all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0) scale(1)';
        });
        
        // Active press effect
        button.addEventListener('mousedown', function() {
            this.style.transform = 'translateY(-3px) scale(1.02)';
        });
        
        button.addEventListener('mouseup', function() {
            this.style.transform = 'translateY(-6px) scale(1.05)';
        });
    });
}

// Progressive loading animations for images
function initProgressiveLoading() {
    const images = document.querySelectorAll('img');
    
    images.forEach(img => {
        // Set initial state
        img.style.opacity = '0';
        img.style.transform = 'scale(0.9)';
        img.style.transition = 'all 0.6s ease-out';
        
        // Animate on load
        img.addEventListener('load', function() {
            setTimeout(() => {
                this.style.opacity = '1';
                this.style.transform = 'scale(1)';
            }, 100);
        });
        
        // If image is already loaded
        if (img.complete) {
            img.style.opacity = '1';
            img.style.transform = 'scale(1)';
        }
    });
}

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

// Ripple effect for buttons
function initRippleEffects() {
    const buttons = document.querySelectorAll('.btn');
    
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            const rect = this.getBoundingClientRect();
            const size = Math.max(rect.width, rect.height);
            const x = e.clientX - rect.left - size / 2;
            const y = e.clientY - rect.top - size / 2;
            
            ripple.style.cssText = `
                width: ${size}px;
                height: ${size}px;
                left: ${x}px;
                top: ${y}px;
                position: absolute;
                border-radius: 50%;
                background: rgba(255, 255, 255, 0.3);
                transform: scale(0);
                animation: ripple 0.6s ease-out;
                pointer-events: none;
            `;
            
            this.style.position = 'relative';
            this.style.overflow = 'hidden';
            this.appendChild(ripple);
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Parallax effects and navbar behavior on scroll
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    
    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    if (hero) {
        hero.style.transform = `translateY(${scrolled * 0.3}px)`;
    }
    
    // Dynamic navbar background
    const navbar = document.querySelector('.navbar');
    if (navbar) {
        if (scrolled > 50) {
            navbar.style.background = 'rgba(15, 23, 42, 0.95)';
            navbar.style.backdropFilter = 'blur(20px)';
            navbar.style.boxShadow = '0 4px 6px -1px rgba(0, 0, 0, 0.3)';
        } else {
            navbar.style.background = 'rgba(15, 23, 42, 0.8)';
            navbar.style.boxShadow = '0 1px 2px 0 rgba(0, 0, 0, 0.1)';
        }
    }
    
    // Add scroll progress indicator
    const scrollPercent = (scrolled / (document.body.scrollHeight - window.innerHeight)) * 100;
    let progressBar = document.querySelector('.scroll-progress');
    
    if (!progressBar) {
        progressBar = document.createElement('div');
        progressBar.className = 'scroll-progress';
        progressBar.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 0%;
            height: 3px;
            background: linear-gradient(90deg, #6366F1, #F43F5E, #22D3EE);
            z-index: 9999;
            transition: width 0.2s ease-out;
        `;
        document.body.appendChild(progressBar);
    }
    
    progressBar.style.width = scrollPercent + '%';
});

// Add custom CSS for ripple animation
const style = document.createElement('style');
style.textContent = `
    @keyframes ripple {
        to {
            transform: scale(2);
            opacity: 0;
        }
    }
    
    .scroll-progress {
        position: fixed;
        top: 0;
        left: 0;
        height: 3px;
        background: linear-gradient(90deg, #6366F1, #F43F5E, #22D3EE);
        z-index: 9999;
        transition: width 0.2s ease-out;
    }
    
    /* Improved focus states for accessibility */
    .btn:focus,
    .nav-link:focus,
    .form-control:focus {
        outline: 3px solid #6366F1;
        outline-offset: 2px;
        box-shadow: 0 0 0 0.25rem rgba(99, 102, 241, 0.25);
    }
    
    /* Reduce motion for users who prefer it */
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: 0.01ms !important;
            animation-iteration-count: 1 !important;
            transition-duration: 0.01ms !important;
            scroll-behavior: auto !important;
        }
    }
`;
document.head.appendChild(style);

// Add loading animation for the page
window.addEventListener('load', function() {
    document.body.style.opacity = '0';
    document.body.style.transition = 'opacity 0.5s ease-out';
    
    setTimeout(() => {
        document.body.style.opacity = '1';
    }, 100);
    
    console.log('🚀 Professional portfolio fully loaded with vibrant design!');
});