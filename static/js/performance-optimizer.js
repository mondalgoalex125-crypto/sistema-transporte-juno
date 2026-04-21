// Optimizador de Rendimiento para JUNO EXPRESS
class PerformanceOptimizer {
    constructor() {
        this.init();
    }

    init() {
        // Lazy Loading de imágenes
        this.setupLazyLoading();
        
        // Preload de recursos críticos
        this.preloadCriticalResources();
        
        // Optimización de animaciones
        this.optimizeAnimations();
        
        // Cache dinámico
        this.setupDynamicCaching();
        
        // Optimización de scroll
        this.optimizeScroll();
        
        // Monitor de rendimiento
        this.setupPerformanceMonitoring();
    }

    // Lazy Loading para imágenes y componentes
    setupLazyLoading() {
        if ('IntersectionObserver' in window) {
            const imageObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const img = entry.target;
                        if (img.dataset.src) {
                            img.src = img.dataset.src;
                            img.classList.remove('lazy');
                            observer.unobserve(img);
                        }
                    }
                });
            });

            // Observar imágenes con lazy loading
            document.querySelectorAll('img[data-src]').forEach(img => {
                imageObserver.observe(img);
            });

            // Lazy loading para componentes pesados
            const componentObserver = new IntersectionObserver((entries, observer) => {
                entries.forEach(entry => {
                    if (entry.isIntersecting) {
                        const component = entry.target;
                        if (component.dataset.component) {
                            this.loadComponent(component.dataset.component, component);
                            observer.unobserve(component);
                        }
                    }
                });
            });

            document.querySelectorAll('[data-component]').forEach(comp => {
                componentObserver.observe(comp);
            });
        }
    }

    // Preload de recursos críticos
    preloadCriticalResources() {
        const criticalResources = [
            '/static/css/bootstrap.min.css',
            '/static/js/bootstrap.bundle.min.js',
            '/static/fonts/fontawesome.woff2'
        ];

        criticalResources.forEach(resource => {
            const link = document.createElement('link');
            link.rel = 'preload';
            link.href = resource;
            link.as = this.getResourceType(resource);
            document.head.appendChild(link);
        });
    }

    getResourceType(url) {
        if (url.endsWith('.css')) return 'style';
        if (url.endsWith('.js')) return 'script';
        if (url.endsWith('.woff2') || url.endsWith('.woff')) return 'font';
        return 'fetch';
    }

    // Optimización de animaciones con requestAnimationFrame
    optimizeAnimations() {
        let ticking = false;

        const updateAnimations = () => {
            // Actualizar animaciones visibles
            const animatedElements = document.querySelectorAll('.fade-in:not(.animated)');
            animatedElements.forEach(element => {
                const rect = element.getBoundingClientRect();
                if (rect.top < window.innerHeight && rect.bottom > 0) {
                    element.classList.add('animated');
                    element.style.opacity = '1';
                    element.style.transform = 'translateY(0)';
                }
            });

            ticking = false;
        };

        const requestTick = () => {
            if (!ticking) {
                requestAnimationFrame(updateAnimations);
                ticking = true;
            }
        };

        // Throttled scroll handler
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(requestTick, 16); // ~60fps
        }, { passive: true });
    }

    // Cache dinámico para respuestas API
    setupDynamicCaching() {
        this.apiCache = new Map();
        
        // Interceptar fetch calls para cachear respuestas API
        const originalFetch = window.fetch;
        window.fetch = async (...args) => {
            const url = args[0];
            const cacheKey = typeof url === 'string' ? url : url.url;
            
            // Verificar caché para GET requests
            if (args[1]?.method !== 'POST' && this.apiCache.has(cacheKey)) {
                const cached = this.apiCache.get(cacheKey);
                if (Date.now() - cached.timestamp < 5 * 60 * 1000) { // 5 minutos
                    return Promise.resolve(cached.response.clone());
                }
            }

            const response = await originalFetch(...args);
            
            // Cachear respuestas exitosas
            if (response.ok && args[1]?.method !== 'POST') {
                this.apiCache.set(cacheKey, {
                    response: response.clone(),
                    timestamp: Date.now()
                });
            }

            return response;
        };
    }

    // Optimización de scroll con passive listeners
    optimizeScroll() {
        // Throttle scroll events
        let scrollTimeout;
        window.addEventListener('scroll', () => {
            if (scrollTimeout) {
                clearTimeout(scrollTimeout);
            }
            scrollTimeout = setTimeout(() => {
                // Lógica de scroll optimizada
                this.handleScroll();
            }, 100);
        }, { passive: true });

        // Optimizar resize events
        let resizeTimeout;
        window.addEventListener('resize', () => {
            if (resizeTimeout) {
                clearTimeout(resizeTimeout);
            }
            resizeTimeout = setTimeout(() => {
                this.handleResize();
            }, 250);
        }, { passive: true });
    }

    handleScroll() {
        // Actualizar navegación sticky
        const navbar = document.querySelector('.navbar');
        if (navbar) {
            if (window.scrollY > 100) {
                navbar.classList.add('navbar-scrolled');
            } else {
                navbar.classList.remove('navbar-scrolled');
            }
        }
    }

    handleResize() {
        // Recalcular layouts
        this.updateMobileLayout();
    }

    updateMobileLayout() {
        const isMobile = window.innerWidth < 768;
        document.body.classList.toggle('mobile-view', isMobile);
        document.body.classList.toggle('desktop-view', !isMobile);
    }

    // Monitor de rendimiento
    setupPerformanceMonitoring() {
        // Monitorizar Core Web Vitals
        this.monitorWebVitals();
        
        // Monitorizar tiempo de carga
        this.monitorLoadTimes();
        
        // Optimizar imágenes automáticamente
        this.optimizeImages();
    }

    monitorWebVitals() {
        // Largest Contentful Paint (LCP)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            const lastEntry = entries[entries.length - 1];
            console.log('LCP:', lastEntry.startTime);
            
            // Enviar a analytics si es necesario
            this.sendToAnalytics('LCP', lastEntry.startTime);
        }).observe({ entryTypes: ['largest-contentful-paint'] });

        // First Input Delay (FID)
        new PerformanceObserver((entryList) => {
            const entries = entryList.getEntries();
            entries.forEach(entry => {
                console.log('FID:', entry.processingStart - entry.startTime);
                this.sendToAnalytics('FID', entry.processingStart - entry.startTime);
            });
        }).observe({ entryTypes: ['first-input'] });

        // Cumulative Layout Shift (CLS)
        let clsValue = 0;
        new PerformanceObserver((entryList) => {
            for (const entry of entryList.getEntries()) {
                if (!entry.hadRecentInput) {
                    clsValue += entry.value;
                }
            }
            console.log('CLS:', clsValue);
            this.sendToAnalytics('CLS', clsValue);
        }).observe({ entryTypes: ['layout-shift'] });
    }

    monitorLoadTimes() {
        window.addEventListener('load', () => {
            const loadTime = performance.now();
            console.log('Page load time:', loadTime);
            
            // Enviar métricas a analytics
            this.sendToAnalytics('PAGE_LOAD', loadTime);
        });
    }

    optimizeImages() {
        // Convertir imágenes a WebP si el navegador lo soporta
        if (this.supportsWebP()) {
            document.querySelectorAll('img[data-webp]').forEach(img => {
                if (img.dataset.webp) {
                    img.src = img.dataset.webp;
                }
            });
        }

        // Optimizar tamaños de imágenes según viewport
        document.querySelectorAll('img[data-src]').forEach(img => {
            const size = this.getOptimalImageSize(img);
            if (img.dataset.src.includes('?')) {
                img.dataset.src += `&size=${size}`;
            } else {
                img.dataset.src += `?size=${size}`;
            }
        });
    }

    supportsWebP() {
        const canvas = document.createElement('canvas');
        canvas.width = 1;
        canvas.height = 1;
        return canvas.toDataURL('image/webp').indexOf('data:image/webp') === 0;
    }

    getOptimalImageSize(img) {
        const rect = img.getBoundingClientRect();
        const dpr = window.devicePixelRatio || 1;
        const width = Math.ceil(rect.width * dpr);
        
        // Tamaños predefinidos
        const sizes = [320, 640, 960, 1280, 1920];
        return sizes.find(size => size >= width) || sizes[sizes.length - 1];
    }

    sendToAnalytics(metric, value) {
        // Enviar métricas a sistema de analytics
        if (window.gtag) {
            gtag('event', metric, {
                value: value,
                custom_parameter: 'juno_express'
            });
        }
        
        // También guardar en localStorage para análisis offline
        const metrics = JSON.parse(localStorage.getItem('performance_metrics') || '{}');
        metrics[metric] = value;
        metrics.timestamp = Date.now();
        localStorage.setItem('performance_metrics', JSON.stringify(metrics));
    }

    // Método público para limpiar caché
    clearCache() {
        this.apiCache.clear();
        caches.delete('juno-express-v1');
    }

    // Método para precargar próxima página
    preloadPage(url) {
        if ('requestIdleCallback' in window) {
            requestIdleCallback(() => {
                const link = document.createElement('link');
                link.rel = 'prefetch';
                link.href = url;
                document.head.appendChild(link);
            });
        }
    }
}

// Inicializar optimizador cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.performanceOptimizer = new PerformanceOptimizer();
});

// Exponer para uso global
window.PerformanceOptimizer = PerformanceOptimizer;
