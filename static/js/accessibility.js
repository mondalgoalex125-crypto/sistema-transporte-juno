// Sistema de Accesibilidad Mejorada para JUNO EXPRESS
class AccessibilityManager {
    constructor() {
        this.isHighContrast = false;
        this.isLargeText = false;
        this.isDarkMode = false;
        this.isReducedMotion = false;
        this.currentLanguage = 'es';
        this.keyboardNavigation = true;
        this.screenReaderMode = false;
        this.init();
    }

    init() {
        this.loadUserPreferences();
        this.setupAccessibilityControls();
        this.setupKeyboardNavigation();
        this.setupScreenReaderSupport();
        this.setupColorBlindSupport();
        this.setupVoiceNavigation();
        this.detectSystemPreferences();
        console.log('Accessibility Manager initialized');
    }

    loadUserPreferences() {
        const preferences = JSON.parse(localStorage.getItem('accessibility_preferences') || '{}');
        
        this.isHighContrast = preferences.highContrast || false;
        this.isLargeText = preferences.largeText || false;
        this.isDarkMode = preferences.darkMode || false;
        this.isReducedMotion = preferences.reducedMotion || false;
        this.currentLanguage = preferences.language || 'es';
        this.keyboardNavigation = preferences.keyboardNavigation !== false;
        this.screenReaderMode = preferences.screenReaderMode || false;
        
        this.applyAccessibilitySettings();
    }

    saveUserPreferences() {
        const preferences = {
            highContrast: this.isHighContrast,
            largeText: this.isLargeText,
            darkMode: this.isDarkMode,
            reducedMotion: this.isReducedMotion,
            language: this.currentLanguage,
            keyboardNavigation: this.keyboardNavigation,
            screenReaderMode: this.screenReaderMode
        };
        
        localStorage.setItem('accessibility_preferences', JSON.stringify(preferences));
    }

    detectSystemPreferences() {
        // Detectar preferencias del sistema
        if (window.matchMedia) {
            // Modo oscuro
            const darkModeQuery = window.matchMedia('(prefers-color-scheme: dark)');
            if (darkModeQuery.matches && !this.isDarkMode) {
                this.toggleDarkMode();
            }
            darkModeQuery.addListener((e) => {
                if (e.matches && !this.isDarkMode) {
                    this.toggleDarkMode();
                }
            });

            // Movimiento reducido
            const reducedMotionQuery = window.matchMedia('(prefers-reduced-motion: reduce)');
            if (reducedMotionQuery.matches) {
                this.isReducedMotion = true;
                this.applyReducedMotion();
            }

            // Contraste alto
            const highContrastQuery = window.matchMedia('(prefers-contrast: high)');
            if (highContrastQuery.matches) {
                this.toggleHighContrast();
            }
        }
    }

    setupAccessibilityControls() {
        // Crear panel de control de accesibilidad
        const accessibilityPanel = document.createElement('div');
        accessibilityPanel.id = 'accessibility-panel';
        accessibilityPanel.innerHTML = `
            <button id="accessibility-toggle" class="accessibility-toggle" aria-label="Opciones de accesibilidad">
                <i class="fas fa-universal-access"></i>
            </button>
            
            <div id="accessibility-controls" class="accessibility-controls" style="display: none;">
                <h6>Accesibilidad</h6>
                
                <div class="accessibility-option">
                    <label class="form-check">
                        <input type="checkbox" id="high-contrast" class="form-check-input">
                        <span class="form-check-label">Alto Contraste</span>
                    </label>
                </div>
                
                <div class="accessibility-option">
                    <label class="form-check">
                        <input type="checkbox" id="large-text" class="form-check-input">
                        <span class="form-check-label">Texto Grande</span>
                    </label>
                </div>
                
                <div class="accessibility-option">
                    <label class="form-check">
                        <input type="checkbox" id="dark-mode" class="form-check-input">
                        <span class="form-check-label">Modo Oscuro</span>
                    </label>
                </div>
                
                <div class="accessibility-option">
                    <label class="form-check">
                        <input type="checkbox" id="reduced-motion" class="form-check-input">
                        <span class="form-check-label">Reducir Movimiento</span>
                    </label>
                </div>
                
                <div class="accessibility-option">
                    <label class="form-check">
                        <input type="checkbox" id="screen-reader" class="form-check-input">
                        <span class="form-check-label">Modo Lector</span>
                    </label>
                </div>
                
                <div class="accessibility-option">
                    <label for="language-select">Idioma:</label>
                    <select id="language-select" class="form-select form-select-sm">
                        <option value="es">Español</option>
                        <option value="en">English</option>
                        <option value="que">Quechua</option>
                    </select>
                </div>
                
                <div class="accessibility-actions">
                    <button class="btn btn-sm btn-outline-secondary" onclick="accessibilityManager.resetSettings()">
                        Restablecer
                    </button>
                    <button class="btn btn-sm btn-primary" onclick="accessibilityManager.closePanel()">
                        Cerrar
                    </button>
                </div>
            </div>
        `;

        document.body.appendChild(accessibilityPanel);
        
        // Agregar estilos
        this.addAccessibilityStyles();
        
        // Configurar event listeners
        this.setupAccessibilityEventListeners();
    }

    addAccessibilityStyles() {
        const styles = `
            <style id="accessibility-styles">
                .accessibility-toggle {
                    position: fixed;
                    bottom: 90px;
                    right: 20px;
                    top: auto;
                    z-index: 9999;
                    background: var(--primary-color);
                    color: white;
                    border: none;
                    border-radius: 50%;
                    width: 50px;
                    height: 50px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                    box-shadow: 0 2px 8px rgba(0,0,0,0.2);
                    transition: all 0.3s ease;
                }
                
                .accessibility-toggle:hover {
                    transform: scale(1.1);
                    box-shadow: 0 4px 12px rgba(0,0,0,0.3);
                }
                
                .accessibility-controls {
                    position: fixed;
                    bottom: 150px;
                    right: 20px;
                    top: auto;
                    background: white;
                    border: 1px solid #ddd;
                    border-radius: 8px;
                    padding: 20px;
                    box-shadow: 0 4px 16px rgba(0,0,0,0.15);
                    z-index: 9999;
                    min-width: 250px;
                    max-width: 300px;
                }
                
                .accessibility-option {
                    margin-bottom: 12px;
                }
                
                .accessibility-actions {
                    display: flex;
                    gap: 8px;
                    margin-top: 16px;
                    padding-top: 16px;
                    border-top: 1px solid #eee;
                }
                
                /* High Contrast Mode */
                body.high-contrast {
                    --primary-color: #000000;
                    --secondary-color: #FFFFFF;
                    --success-color: #00FF00;
                    --danger-color: #FF0000;
                    --warning-color: #FFFF00;
                    --info-color: #0000FF;
                    background: #FFFFFF !important;
                    color: #000000 !important;
                }
                
                body.high-contrast * {
                    border-color: #000000 !important;
                    background-color: #FFFFFF !important;
                    color: #000000 !important;
                }
                
                body.high-contrast .btn {
                    border: 2px solid #000000 !important;
                    background: #FFFFFF !important;
                    color: #000000 !important;
                }
                
                body.high-contrast .btn-primary {
                    background: #000000 !important;
                    color: #FFFFFF !important;
                }
                
                /* Large Text Mode */
                body.large-text {
                    font-size: 120% !important;
                }
                
                body.large-text .btn {
                    font-size: 120% !important;
                    padding: 12px 24px !important;
                }
                
                body.large-text .form-control {
                    font-size: 120% !important;
                    padding: 12px !important;
                }
                
                /* Dark Mode */
                body.dark-mode {
                    background: #1a1a1a !important;
                    color: #ffffff !important;
                }
                
                body.dark-mode .card {
                    background: #2d2d2d !important;
                    border-color: #444 !important;
                    color: #ffffff !important;
                }
                
                body.dark-mode .navbar {
                    background: #2d2d2d !important;
                    border-color: #444 !important;
                }
                
                body.dark-mode .form-control {
                    background: #3d3d3d !important;
                    border-color: #555 !important;
                    color: #ffffff !important;
                }
                
                body.dark-mode .form-control::placeholder {
                    color: #aaa !important;
                }
                
                body.dark-mode .btn {
                    border-color: #666 !important;
                }
                
                body.dark-mode .btn-outline-primary {
                    border-color: var(--primary-color) !important;
                    color: var(--primary-color) !important;
                }
                
                /* Reduced Motion */
                body.reduced-motion *,
                body.reduced-motion *::before,
                body.reduced-motion *::after {
                    animation-duration: 0.01ms !important;
                    animation-iteration-count: 1 !important;
                    transition-duration: 0.01ms !important;
                    scroll-behavior: auto !important;
                }
                
                /* Screen Reader Mode */
                body.screen-reader .sr-only-focusable:focus,
                body.screen-reader .focusable:focus {
                    outline: 3px solid #000000;
                    outline-offset: 2px;
                }
                
                /* Focus Indicators */
                .btn:focus,
                .form-control:focus,
                .nav-link:focus,
                a:focus {
                    outline: 3px solid var(--primary-color);
                    outline-offset: 2px;
                }
                
                /* Skip Links */
                .skip-links {
                    position: fixed;
                    top: -40px;
                    left: 0;
                    z-index: 10001;
                }
                
                .skip-links a {
                    position: absolute;
                    top: -40px;
                    left: 0;
                    background: var(--primary-color);
                    color: white;
                    padding: 8px;
                    text-decoration: none;
                    border-radius: 0 0 4px 0;
                }
                
                .skip-links a:focus {
                    top: 0;
                }
                
                /* ARIA Live Regions */
                .aria-live {
                    position: absolute;
                    left: -10000px;
                    width: 1px;
                    height: 1px;
                    overflow: hidden;
                }
                
                /* Responsive */
                @media (max-width: 768px) {
                    .accessibility-toggle {
                        bottom: 80px;
                        right: 10px;
                        top: auto;
                        width: 45px;
                        height: 45px;
                    }

                    .accessibility-controls {
                        bottom: 135px;
                        right: 10px;
                        top: auto;
                        left: 10px;
                        min-width: auto;
                        max-width: none;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    setupAccessibilityEventListeners() {
        // Toggle panel
        document.getElementById('accessibility-toggle').addEventListener('click', () => {
            this.togglePanel();
        });

        // High contrast
        document.getElementById('high-contrast').addEventListener('change', (e) => {
            this.toggleHighContrast();
        });

        // Large text
        document.getElementById('large-text').addEventListener('change', (e) => {
            this.toggleLargeText();
        });

        // Dark mode
        document.getElementById('dark-mode').addEventListener('change', (e) => {
            this.toggleDarkMode();
        });

        // Reduced motion
        document.getElementById('reduced-motion').addEventListener('change', (e) => {
            this.toggleReducedMotion();
        });

        // Screen reader mode
        document.getElementById('screen-reader').addEventListener('change', (e) => {
            this.toggleScreenReaderMode();
        });

        // Language
        document.getElementById('language-select').addEventListener('change', (e) => {
            this.changeLanguage(e.target.value);
        });

        // Cerrar panel al hacer clic fuera
        document.addEventListener('click', (e) => {
            const panel = document.getElementById('accessibility-controls');
            const toggle = document.getElementById('accessibility-toggle');
            
            if (!panel.contains(e.target) && !toggle.contains(e.target)) {
                this.closePanel();
            }
        });

        // Atajos de teclado
        document.addEventListener('keydown', (e) => {
            // Alt + A: Abrir panel de accesibilidad
            if (e.altKey && e.key === 'a') {
                e.preventDefault();
                this.openPanel();
            }
            
            // Escape: Cerrar panel
            if (e.key === 'Escape') {
                this.closePanel();
            }
        });
    }

    togglePanel() {
        const controls = document.getElementById('accessibility-controls');
        const isVisible = controls.style.display !== 'none';
        
        controls.style.display = isVisible ? 'none' : 'block';
        
        if (!isVisible) {
            document.getElementById('high-contrast').checked = this.isHighContrast;
            document.getElementById('large-text').checked = this.isLargeText;
            document.getElementById('dark-mode').checked = this.isDarkMode;
            document.getElementById('reduced-motion').checked = this.isReducedMotion;
            document.getElementById('screen-reader').checked = this.screenReaderMode;
            document.getElementById('language-select').value = this.currentLanguage;
        }
    }

    openPanel() {
        document.getElementById('accessibility-controls').style.display = 'block';
    }

    closePanel() {
        document.getElementById('accessibility-controls').style.display = 'none';
    }

    toggleHighContrast() {
        this.isHighContrast = !this.isHighContrast;
        document.body.classList.toggle('high-contrast', this.isHighContrast);
        this.saveUserPreferences();
        this.announceToScreenReader('Alto contraste ' + (this.isHighContrast ? 'activado' : 'desactivado'));
    }

    toggleLargeText() {
        this.isLargeText = !this.isLargeText;
        document.body.classList.toggle('large-text', this.isLargeText);
        this.saveUserPreferences();
        this.announceToScreenReader('Texto grande ' + (this.isLargeText ? 'activado' : 'desactivado'));
    }

    toggleDarkMode() {
        this.isDarkMode = !this.isDarkMode;
        document.body.classList.toggle('dark-mode', this.isDarkMode);
        this.saveUserPreferences();
        this.announceToScreenReader('Modo oscuro ' + (this.isDarkMode ? 'activado' : 'desactivado'));
    }

    toggleReducedMotion() {
        this.isReducedMotion = !this.isReducedMotion;
        document.body.classList.toggle('reduced-motion', this.isReducedMotion);
        this.saveUserPreferences();
        this.announceToScreenReader('Movimiento reducido ' + (this.isReducedMotion ? 'activado' : 'desactivado'));
    }

    toggleScreenReaderMode() {
        this.screenReaderMode = !this.screenReaderMode;
        document.body.classList.toggle('screen-reader', this.screenReaderMode);
        this.saveUserPreferences();
        this.announceToScreenReader('Modo lector ' + (this.screenReaderMode ? 'activado' : 'desactivado'));
    }

    changeLanguage(language) {
        this.currentLanguage = language;
        this.saveUserPreferences();
        this.updatePageLanguage(language);
        this.announceToScreenReader('Idioma cambiado a ' + this.getLanguageName(language));
    }

    getLanguageName(language) {
        const names = {
            'es': 'Español',
            'en': 'English',
            'que': 'Quechua'
        };
        return names[language] || language;
    }

    updatePageLanguage(language) {
        document.documentElement.lang = language;
        
        // Actualizar atributos aria-label según el idioma
        const translations = {
            'es': {
                'login': 'Iniciar sesión',
                'register': 'Registrarse',
                'search': 'Buscar',
                'menu': 'Menú',
                'close': 'Cerrar'
            },
            'en': {
                'login': 'Login',
                'register': 'Register',
                'search': 'Search',
                'menu': 'Menu',
                'close': 'Close'
            },
            'que': {
                'login': 'Yaykuy',
                'register': 'Qillqakuy',
                'search': 'Maskay',
                'menu': 'Menu',
                'close': 'Wichay'
            }
        };
        
        const t = translations[language];
        if (t) {
            // Actualizar etiquetas ARIA
            this.updateAriaLabels(t);
        }
    }

    updateAriaLabels(translations) {
        // Login buttons
        document.querySelectorAll('[aria-label*="login"], [aria-label*="Login"]').forEach(el => {
            el.setAttribute('aria-label', translations.login);
        });
        
        // Register buttons
        document.querySelectorAll('[aria-label*="register"], [aria-label*="Register"]').forEach(el => {
            el.setAttribute('aria-label', translations.register);
        });
        
        // Search inputs
        document.querySelectorAll('[aria-label*="search"], [aria-label*="Search"]').forEach(el => {
            el.setAttribute('aria-label', translations.search);
        });
    }

    setupKeyboardNavigation() {
        // Navegación por teclado mejorada
        document.addEventListener('keydown', (e) => {
            if (!this.keyboardNavigation) return;
            
            // Tab navigation mejorada
            if (e.key === 'Tab') {
                // Asegurar que los elementos focusables sean visibles
                setTimeout(() => {
                    const focused = document.activeElement;
                    if (focused) {
                        focused.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    }
                }, 100);
            }
            
            // Enter en botones y links
            if (e.key === 'Enter' && e.target.tagName === 'A') {
                e.target.click();
            }
            
            // Space en checkboxes y radio buttons
            if (e.key === ' ' && (e.target.type === 'checkbox' || e.target.type === 'radio')) {
                e.preventDefault();
                e.target.click();
            }
        });

        // Agregar atributos tabindex donde sea necesario
        this.addTabIndexAttributes();
    }

    addTabIndexAttributes() {
        // Asegurar que todos los elementos interactivos tengan tabindex
        const interactiveElements = document.querySelectorAll('button, a, input, select, textarea, [role="button"]');
        interactiveElements.forEach(el => {
            if (!el.hasAttribute('tabindex')) {
                el.setAttribute('tabindex', '0');
            }
        });
    }

    setupScreenReaderSupport() {
        // Crear regiones ARIA live
        this.createAriaLiveRegions();
        
        // Mejorar etiquetas ARIA
        this.enhanceAriaLabels();
        
        // Agregar descripciones para elementos complejos
        this.addAriaDescriptions();
    }

    createAriaLiveRegions() {
        // Región para anuncios importantes
        const liveRegion = document.createElement('div');
        liveRegion.setAttribute('aria-live', 'polite');
        liveRegion.setAttribute('aria-atomic', 'true');
        liveRegion.className = 'aria-live';
        liveRegion.id = 'aria-live-region';
        document.body.appendChild(liveRegion);
        
        // Región para alertas
        const alertRegion = document.createElement('div');
        alertRegion.setAttribute('aria-live', 'assertive');
        alertRegion.setAttribute('aria-atomic', 'true');
        alertRegion.className = 'aria-live';
        alertRegion.id = 'aria-alert-region';
        document.body.appendChild(alertRegion);
    }

    enhanceAriaLabels() {
        // Mejorar etiquetas para navegación
        const nav = document.querySelector('nav');
        if (nav) {
            nav.setAttribute('aria-label', 'Navegación principal');
        }
        
        // Mejorar etiquetas para contenido principal
        const main = document.querySelector('main');
        if (main) {
            main.setAttribute('aria-label', 'Contenido principal');
        }
        
        // Mejorar etiquetas para formularios
        document.querySelectorAll('form').forEach((form, index) => {
            if (!form.getAttribute('aria-label')) {
                form.setAttribute('aria-label', `Formulario ${index + 1}`);
            }
        });
        
        // Agregar roles a elementos semánticos
        this.addSemanticRoles();
    }

    addSemanticRoles() {
        // Agregar roles a secciones sin etiquetas claras
        document.querySelectorAll('section').forEach((section, index) => {
            if (!section.getAttribute('aria-label') && !section.querySelector('h1, h2, h3, h4, h5, h6')) {
                section.setAttribute('aria-label', `Sección ${index + 1}`);
            }
        });
    }

    addAriaDescriptions() {
        // Agregar descripciones para elementos complejos
        document.querySelectorAll('.card').forEach(card => {
            const title = card.querySelector('h1, h2, h3, h4, h5, h6');
            if (title && !card.getAttribute('aria-describedby')) {
                const descId = 'card-desc-' + Math.random().toString(36).substr(2, 9);
                title.id = descId;
                card.setAttribute('aria-describedby', descId);
            }
        });
    }

    setupColorBlindSupport() {
        // Soporte para daltonismo
        this.createColorBlindFilters();
    }

    createColorBlindFilters() {
        // Filtros CSS para diferentes tipos de daltonismo
        const colorBlindStyles = `
            <style id="colorblind-styles">
                /* Protanopia (rojo-verde) */
                body.protanopia {
                    filter: url('#protanopia-filter');
                }
                
                /* Deuteranopia (verde-rojo) */
                body.deuteranopia {
                    filter: url('#deuteranopia-filter');
                }
                
                /* Tritanopia (azul-amarillo) */
                body.tritanopia {
                    filter: url('#tritanopia-filter');
                }
                
                /* Achromatopsia (monocromático) */
                body.achromatopsia {
                    filter: grayscale(100%);
                }
            </style>
        `;
        
        document.head.insertAdjacentHTML('beforeend', colorBlindStyles);
        
        // Crear filtros SVG
        this.createSVGFilters();
    }

    createSVGFilters() {
        const svg = `
            <svg style="display: none;">
                <defs>
                    <filter id="protanopia-filter">
                        <feColorMatrix type="matrix" values="
                            0.567, 0.433, 0, 0, 0
                            0.558, 0.442, 0, 0, 0
                            0, 0.242, 0.758, 0, 0
                            0, 0, 0, 1, 0
                        "/>
                    </filter>
                    
                    <filter id="deuteranopia-filter">
                        <feColorMatrix type="matrix" values="
                            0.625, 0.375, 0, 0, 0
                            0.7, 0.3, 0, 0, 0
                            0, 0.3, 0.7, 0, 0
                            0, 0, 0, 1, 0
                        "/>
                    </filter>
                    
                    <filter id="tritanopia-filter">
                        <feColorMatrix type="matrix" values="
                            0.95, 0.05, 0, 0, 0
                            0, 0.433, 0.567, 0, 0
                            0, 0.475, 0.525, 0, 0
                            0, 0, 0, 1, 0
                        "/>
                    </filter>
                </defs>
            </svg>
        `;
        
        document.body.insertAdjacentHTML('beforeend', svg);
    }

    setupVoiceNavigation() {
        // Navegación por voz (si el navegador lo soporta)
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            this.initializeVoiceRecognition();
        }
    }

    initializeVoiceRecognition() {
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        
        if (!SpeechRecognition) return;
        
        const recognition = new SpeechRecognition();
        recognition.lang = this.currentLanguage === 'es' ? 'es-ES' : 'en-US';
        recognition.continuous = false;
        recognition.interimResults = false;
        
        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript.toLowerCase();
            this.processVoiceCommand(transcript);
        };
        
        recognition.onerror = (event) => {
            console.error('Speech recognition error:', event.error);
        };
        
        this.voiceRecognition = recognition;
    }

    processVoiceCommand(command) {
        // Comandos de voz básicos
        if (command.includes('buscar')) {
            const searchInput = document.querySelector('input[type="search"], [placeholder*="buscar"]');
            if (searchInput) {
                searchInput.focus();
                this.announceToScreenReader('Cuadro de búsqueda activado');
            }
        }
        
        if (command.includes('navegar') || command.includes('menú')) {
            const nav = document.querySelector('nav');
            if (nav) {
                nav.focus();
                this.announceToScreenReader('Menú de navegación activado');
            }
        }
        
        if (command.includes('accesibilidad')) {
            this.openPanel();
            this.announceToScreenReader('Panel de accesibilidad abierto');
        }
    }

    announceToScreenReader(message) {
        const liveRegion = document.getElementById('aria-live-region');
        if (liveRegion) {
            liveRegion.textContent = message;
            
            // Limpiar después de anunciar
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    }

    applyAccessibilitySettings() {
        document.body.classList.toggle('high-contrast', this.isHighContrast);
        document.body.classList.toggle('large-text', this.isLargeText);
        document.body.classList.toggle('dark-mode', this.isDarkMode);
        document.body.classList.toggle('reduced-motion', this.isReducedMotion);
        document.body.classList.toggle('screen-reader', this.screenReaderMode);
        document.documentElement.lang = this.currentLanguage;
    }

    applyReducedMotion() {
        document.body.classList.add('reduced-motion');
    }

    resetSettings() {
        this.isHighContrast = false;
        this.isLargeText = false;
        this.isDarkMode = false;
        this.isReducedMotion = false;
        this.screenReaderMode = false;
        this.currentLanguage = 'es';
        
        this.applyAccessibilitySettings();
        this.saveUserPreferences();
        this.closePanel();
        this.announceToScreenReader('Configuración de accesibilidad restablecida');
    }

    // Métodos públicos
    enableHighContrast() {
        this.isHighContrast = true;
        this.toggleHighContrast();
    }

    enableLargeText() {
        this.isLargeText = true;
        this.toggleLargeText();
    }

    enableDarkMode() {
        this.isDarkMode = true;
        this.toggleDarkMode();
    }

    disableAnimations() {
        this.isReducedMotion = true;
        this.toggleReducedMotion();
    }

    // Métodos de ayuda
    getAccessibilityReport() {
        return {
            highContrast: this.isHighContrast,
            largeText: this.isLargeText,
            darkMode: this.isDarkMode,
            reducedMotion: this.isReducedMotion,
            screenReaderMode: this.screenReaderMode,
            language: this.currentLanguage,
            keyboardNavigation: this.keyboardNavigation
        };
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.accessibilityManager = new AccessibilityManager();
    
    // Exponer globalmente
    window.AccessibilityManager = AccessibilityManager;
});

// Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = AccessibilityManager;
}
