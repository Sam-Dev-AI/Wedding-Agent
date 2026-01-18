document.addEventListener('DOMContentLoaded', () => {

    // --- Register GSAP Plugins ---
    gsap.registerPlugin(ScrollTrigger);

    // --- Lenis Smooth Scroll ---
    initLenis();

    // --- Three.js Particle System (Hero) ---
    initParticles();

    // --- GSAP Hero Animations ---
    initHeroAnimations();

    // --- Scroll Animations ---
    initScrollAnimations();

    // --- Vanilla Tilt ---
    initTilt();

    // --- Swiper 3D Gallery ---
    initSwiper();

    // --- Mobile Menu ---
    initMobileMenu();

    // --- Hide Loader ---
    window.addEventListener('load', () => {
        const loader = document.getElementById('loader');
        const loaderText = document.querySelector('.loader-text span');

        if (loaderText) {
            gsap.to(loaderText, {
                y: 0,
                duration: 1,
                ease: 'power4.out'
            });
        }

        if (loader) {
            gsap.to(loader, {
                opacity: 0,
                duration: 0.8,
                delay: 1.0,
                ease: 'power2.inOut',
                onComplete: () => loader.style.display = 'none'
            });
        }
    });
});

function initLenis() {
    // Check if Lenis is loaded
    if (typeof Lenis === 'undefined') return;

    const lenis = new Lenis({
        duration: 1.2,
        easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
        direction: 'vertical',
        gestureDirection: 'vertical',
        smooth: true,
        mouseMultiplier: 1,
        smoothTouch: false,
        touchMultiplier: 2,
    });

    function raf(time) {
        lenis.raf(time);
        requestAnimationFrame(raf);
    }

    requestAnimationFrame(raf);
}

function initParticles() {
    const container = document.getElementById('canvas-container');
    if (!container) return;

    // Clear existing canvas if any (though logic should prevent double init)
    container.innerHTML = '';

    const scene = new THREE.Scene();
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });

    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    container.appendChild(renderer.domElement);

    // Create Particles
    const particlesGeometry = new THREE.BufferGeometry();
    const particlesCount = 400; // Optimal density for performance

    const posArray = new Float32Array(particlesCount * 3);

    for (let i = 0; i < particlesCount * 3; i++) {
        posArray[i] = (Math.random() - 0.5) * 18;
    }

    particlesGeometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

    // Gold colored particles with soft glow texture (simulated by blending)
    const material = new THREE.PointsMaterial({
        size: 0.025,
        color: 0xD4AF37,
        transparent: true,
        opacity: 0.7,
        blending: THREE.AdditiveBlending
    });

    const particlesMesh = new THREE.Points(particlesGeometry, material);
    scene.add(particlesMesh);

    camera.position.z = 4;

    // Mouse Interaction
    let mouseX = 0;
    let mouseY = 0;

    // Throttled mouse move
    document.addEventListener('mousemove', (event) => {
        mouseX = (event.clientX / window.innerWidth - 0.5) * 2;
        mouseY = (event.clientY / window.innerHeight - 0.5) * 2;
    });

    const clock = new THREE.Clock();

    function animate() {
        requestAnimationFrame(animate);
        const elapsedTime = clock.getElapsedTime();

        // Organic movement
        particlesMesh.rotation.y = elapsedTime * 0.03;

        // Gentle mouse reaction
        particlesMesh.rotation.x += 0.05 * (mouseY * 0.2 - particlesMesh.rotation.x);
        particlesMesh.rotation.y += 0.05 * (mouseX * 0.2 - (particlesMesh.rotation.y - elapsedTime * 0.03));

        // Wave effect
        // Accessing positions to wave them is expensive in JS loop, using rotation for performance is better

        renderer.render(scene, camera);
    }

    animate();

    window.addEventListener('resize', () => {
        camera.aspect = window.innerWidth / window.innerHeight;
        camera.updateProjectionMatrix();
        renderer.setSize(window.innerWidth, window.innerHeight);
    });
}

// Helper to Split Text
// Helper to Split Text (Preserves <br>)
// Helper to Split Text (Handles multiple elements)
function splitTextToSpans(selector) {
    const elements = document.querySelectorAll(selector);
    elements.forEach(element => {
        const text = element.innerText;
        element.innerHTML = text.split('').map(char => `<span class="char">${char === ' ' ? '&nbsp;' : char}</span>`).join('');
        // Ensure visibility
        element.style.opacity = '1';
    });
}

function initHeroAnimations() {
    // 1. Prepare Title
    const heroTitle = document.querySelector('.hero-title');
    if (heroTitle) {
        // Ensure it starts visible in CSS terms so GSAP can handle opacity
        heroTitle.style.visibility = 'visible';
        heroTitle.style.opacity = '1';
        splitTextToSpans('.hero-line');
    }

    const tl = gsap.timeline({ defaults: { ease: "power3.out" } });

    // 2. Animate
    tl.to('.hero-reveal', { y: 0, opacity: 1, duration: 1, delay: 0.2 })
        .from('.hero-title .char', {
            opacity: 0,
            y: 80,
            rotateX: -90,
            stagger: 0.05,
            duration: 1.2
        }, "-=0.5")
        .to('.hero-title .char', { opacity: 1 }, "<") // Safety safety check to ensure opacity hits 1
        .to('.hero-text', { opacity: 1, y: 0, duration: 1 }, "-=0.5")
        .to('.hero-btns', { opacity: 1, y: 0, duration: 1 }, "-=0.8")
        // Continuous Micro Float (Professional) - Starts after entrance
        .to('.hero-title .char', {
            y: -10, // Move UP by 10px (floating effect)
            duration: 3,
            ease: "sine.inOut",
            yoyo: true,
            repeat: -1,
            stagger: 0,
            force3D: true
        });

    // Scroll Parallax (Title moves up/down)
    gsap.to('.hero-title', {
        scrollTrigger: {
            trigger: 'header',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        },
        y: 100
    });

    gsap.to('#hero-bg', {
        scrollTrigger: {
            trigger: 'header',
            start: 'top top',
            end: 'bottom top',
            scrub: true
        },
        y: 200,
        scale: 1.2
    });
}

function initScrollAnimations() {

    // Navbar Scroll Effect
    ScrollTrigger.create({
        start: 'top -80',
        end: 99999,
        onToggle: (self) => {
            const nav = document.getElementById('navbar');
            if (self.isActive) {
                nav.classList.add('scrolled', 'glass-nav');
                // Shrink Navbar
                gsap.to(nav, { height: '80px', padding: '0 20px', duration: 0.3 });
            } else {
                nav.classList.remove('scrolled', 'glass-nav');
                // Expand Navbar
                gsap.to(nav, { height: '96px', padding: '0', duration: 0.3 }); // 96px = h-24
            }
        }
    });

    // Reveal Elements with DRAMATIC side entrance
    const revealElements = document.querySelectorAll('[data-aos]');

    revealElements.forEach(elem => {
        let xVal = 0;
        let yVal = 0;

        const type = elem.getAttribute('data-aos');
        // Increase offsets for drama
        if (type === 'fade-right') xVal = -100; // was -50
        else if (type === 'fade-left') xVal = 100; // was 50
        else if (type === 'fade-up') yVal = 80; // was 50

        gsap.set(elem, { autoAlpha: 0, x: xVal, y: yVal });

        gsap.to(elem, {
            duration: 1.5,
            autoAlpha: 1,
            x: 0,
            y: 0,
            ease: "power3.out",
            scrollTrigger: {
                trigger: elem,
                start: "top 85%",
                end: "bottom 0%", // Define end to know when to reverse
                toggleActions: "play reverse play reverse" // Enter -> Play, Leave -> Reverse, EnterBack -> Play, LeaveBack -> Reverse
            }
        });
    });

    // Reveal ALL paragraphs 
    gsap.utils.toArray('p:not(.hero-reveal):not(.hero-text)').forEach(p => {
        gsap.from(p, {
            scrollTrigger: {
                trigger: p,
                start: "top 90%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse"
            },
            y: 50, opacity: 0, duration: 1.2, ease: "power3.out"
        });
    });

    // Reveal ALL remaining images 
    gsap.utils.toArray('img:not(.parallax-img):not(.hero-bg)').forEach(img => {
        gsap.from(img, {
            scrollTrigger: {
                trigger: img,
                start: "top 85%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse"
            },
            scale: 0.9, opacity: 0, duration: 1.5, ease: "power2.out"
        });
    });

    // Specific Parallax Images
    gsap.utils.toArray('.parallax-img').forEach(img => {
        gsap.to(img, {
            yPercent: 20,
            ease: "none",
            scrollTrigger: {
                trigger: img.parentElement,
                start: "top bottom",
                end: "bottom top",
                scrub: true
            }
        });
    });

    // Section Headers (H2) - Elegant Reveal
    gsap.utils.toArray('h2').forEach(h2 => {
        h2.classList.add('title-underline');

        gsap.from(h2, {
            scrollTrigger: {
                trigger: h2,
                start: "top 90%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse",
                onEnter: () => h2.classList.add('active'),
                onLeaveBack: () => h2.classList.remove('active') // Reset underline on reverse
            },
            y: 30, opacity: 0, duration: 1.2, ease: "power3.out"
        });

        // Hover Effect
        h2.addEventListener('mouseenter', () => gsap.to(h2, { color: '#D4AF37', duration: 0.3 }));
        h2.addEventListener('mouseleave', () => gsap.to(h2, { color: 'inherit', duration: 0.3 }));
    });

    // Features Section Text Reveals (H4)
    gsap.utils.toArray('h4').forEach(h4 => {
        gsap.from(h4, {
            scrollTrigger: {
                trigger: h4,
                start: "top 90%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse"
            },
            x: -30, opacity: 0, duration: 1.2
        });
    });

    // Staggered List Reveals (About Section)
    const listItems = document.querySelectorAll('#about ul li');
    if (listItems.length > 0) {
        gsap.from(listItems, {
            scrollTrigger: {
                trigger: '#about ul',
                start: "top 85%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse"
            },
            x: -30,
            opacity: 0,
            duration: 1,
            stagger: 0.2,
            ease: "power2.out"
        });
    }

    // Staggered Form Inputs (Contact Section)
    const formInputs = document.querySelectorAll('#inquiry-form input, #inquiry-form textarea');
    if (formInputs.length > 0) {
        gsap.from(formInputs, {
            scrollTrigger: {
                trigger: '#inquiry-form',
                start: "top 80%",
                end: "bottom 0%",
                toggleActions: "play reverse play reverse"
            },
            y: 30,
            opacity: 0,
            duration: 0.8,
            stagger: 0.1,
            ease: "power2.out"
        });
    }

    // Button Hover Effects
    gsap.utils.toArray('button, .glass-panel, #book-btn').forEach(btn => {
        btn.addEventListener('mouseenter', () => {
            gsap.to(btn, { scale: 1.05, duration: 0.3, ease: "power1.out" });
        });
        btn.addEventListener('mouseleave', () => {
            gsap.to(btn, { scale: 1, duration: 0.3, ease: "power1.out" });
        });
    });
}

function initTilt() {
    if (typeof VanillaTilt === 'undefined') return;

    VanillaTilt.init(document.querySelectorAll(".glass-panel"), {
        max: 8,
        speed: 400,
        glare: true,
        "max-glare": 0.3,
        scale: 1.02
    });

    // About image tilt
    VanillaTilt.init(document.querySelectorAll("#about .group"), {
        max: 5,
        speed: 1000,
        scale: 1.01
    });
}

function initSwiper() {
    if (typeof Swiper === 'undefined') return;

    // Use Coverflow effect for 3D feel BUT with linear continuous movement
    const swiper = new Swiper('.mySwiper', {
        effect: 'coverflow', // Keep 3D feel
        grabCursor: true,
        centeredSlides: true,
        slidesPerView: 'auto',
        coverflowEffect: {
            rotate: 30,
            stretch: 0,
            depth: 100,
            modifier: 1,
            slideShadows: false,
        },
        loop: true,
        speed: 5000, // Slow continuous
        allowTouchMove: true,
        autoplay: {
            delay: 0, // Continuous
            disableOnInteraction: false,
            pauseOnMouseEnter: false // FIX: Do not pause on hover
        },
    });
}

function initMobileMenu() {
    const mobileMenuBtn = document.getElementById('mobile-menu-btn');
    const mobileMenu = document.getElementById('mobile-menu');
    const mobileLinks = document.querySelectorAll('.mobile-link');
    let isMenuOpen = false;

    if (!mobileMenuBtn) return;

    mobileMenuBtn.addEventListener('click', () => {
        isMenuOpen = !isMenuOpen;
        if (isMenuOpen) {
            mobileMenu.classList.remove('hidden');
            // Animate opacity wrapper
            gsap.to(mobileMenu, { opacity: 1, duration: 0.3 });

            gsap.fromTo(mobileLinks,
                { y: 20, opacity: 0 },
                {
                    y: 0,
                    opacity: 1,
                    duration: 0.5,
                    stagger: 0.1,
                    delay: 0.1
                }
            );
        } else {
            gsap.to(mobileMenu, {
                opacity: 0,
                duration: 0.3,
                onComplete: () => mobileMenu.classList.add('hidden')
            });
        }
    });

    // Close menu when link clicked
    mobileLinks.forEach(link => {
        link.addEventListener('click', () => {
            isMenuOpen = false;
            gsap.to(mobileMenu, {
                opacity: 0,
                duration: 0.3,
                onComplete: () => mobileMenu.classList.add('hidden')
            });
        });
    });
}
