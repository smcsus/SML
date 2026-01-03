// Sunday Movie League - Interactive Features

document.addEventListener('DOMContentLoaded', () => {
    // Intersection Observer for scroll animations
    const observerOptions = {
        root: null,
        rootMargin: '0px',
        threshold: 0.1
    };

    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('in-view');
            }
        });
    }, observerOptions);

    // Observe all animated elements
    document.querySelectorAll('.champion-row, .runner-card, .timeline-item, .member-card, .alumni-card').forEach(el => {
        observer.observe(el);
    });

    // Smooth scroll for navigation
    document.querySelectorAll('.nav-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            const targetId = link.getAttribute('href');
            const targetElement = document.querySelector(targetId);
            
            if (targetElement) {
                const navHeight = document.querySelector('.nav').offsetHeight;
                const targetPosition = targetElement.offsetTop - navHeight - 20;
                
                window.scrollTo({
                    top: targetPosition,
                    behavior: 'smooth'
                });
            }
        });
    });

    // Parallax effect for hero section
    const hero = document.querySelector('.hero');
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        const heroContent = document.querySelector('.hero-content');
        
        if (scrolled < window.innerHeight) {
            heroContent.style.transform = `translateY(${scrolled * 0.3}px)`;
            heroContent.style.opacity = 1 - (scrolled / window.innerHeight) * 0.5;
        }
    });

    // Easter egg: Konami code reveals a message
    const konamiCode = ['ArrowUp', 'ArrowUp', 'ArrowDown', 'ArrowDown', 'ArrowLeft', 'ArrowRight', 'ArrowLeft', 'ArrowRight', 'b', 'a'];
    let konamiIndex = 0;

    document.addEventListener('keydown', (e) => {
        if (e.key === konamiCode[konamiIndex]) {
            konamiIndex++;
            if (konamiIndex === konamiCode.length) {
                showEasterEgg();
                konamiIndex = 0;
            }
        } else {
            konamiIndex = 0;
        }
    });

    function showEasterEgg() {
        const message = document.createElement('div');
        message.innerHTML = '~ DUCK RACE CHAMPION ~';
        message.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            background: linear-gradient(135deg, #d4af37, #f4d03f);
            color: #0a0a0b;
            padding: 2rem 4rem;
            font-family: 'Bebas Neue', sans-serif;
            font-size: 2rem;
            border-radius: 8px;
            z-index: 10000;
            animation: easterEgg 3s ease-out forwards;
        `;
        
        const style = document.createElement('style');
        style.textContent = `
            @keyframes easterEgg {
                0% { transform: translate(-50%, -50%) scale(0); opacity: 0; }
                20% { transform: translate(-50%, -50%) scale(1.2); opacity: 1; }
                30% { transform: translate(-50%, -50%) scale(1); }
                80% { opacity: 1; }
                100% { opacity: 0; transform: translate(-50%, -50%) scale(0.8); }
            }
        `;
        
        document.head.appendChild(style);
        document.body.appendChild(message);
        
        setTimeout(() => {
            message.remove();
            style.remove();
        }, 3000);
    }

    // Add click effect to trophy
    document.querySelectorAll('.champion-trophy, .row-trophy').forEach(trophy => {
        trophy.style.cursor = 'pointer';
        trophy.addEventListener('click', function() {
            this.style.animation = 'none';
            this.offsetHeight; // Trigger reflow
            this.style.animation = 'spin 0.5s ease-out';
        });
    });

    // Add spin animation
    const spinStyle = document.createElement('style');
    spinStyle.textContent = `
        @keyframes spin {
            0% { transform: rotate(0deg) scale(1); }
            50% { transform: rotate(180deg) scale(1.2); }
            100% { transform: rotate(360deg) scale(1); }
        }
    `;
    document.head.appendChild(spinStyle);

    // Console message for curious developers
    console.log('%cSunday Movie League', 'font-size: 24px; color: #d4af37; font-weight: bold;');
    console.log('%cEst. 2016 | Commissioner: Steven Masters', 'font-size: 12px; color: #a1a1aa;');
    console.log('%cNever forget Kirchergate 2018', 'font-size: 10px; color: #ef4444; font-style: italic;');
});

