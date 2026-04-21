// Sistema de Pagos Móviles para JUNO EXPRESS
class MobilePaymentManager {
    constructor() {
        this.currentPayment = null;
        this.paymentMethods = null;
        this.pollingInterval = null;
        this.init();
    }

    async init() {
        try {
            // Cargar métodos de pago disponibles
            await this.loadPaymentMethods();
            
            // Configurar event listeners
            this.setupEventListeners();
            
            console.log('Mobile Payment Manager initialized');
        } catch (error) {
            console.error('Error initializing Mobile Payment Manager:', error);
        }
    }

    async loadPaymentMethods() {
        try {
            const response = await fetch('/api/payments/methods');
            if (response.ok) {
                this.paymentMethods = await response.json();
            }
        } catch (error) {
            console.error('Error loading payment methods:', error);
        }
    }

    setupEventListeners() {
        // Escuchar cambios en los métodos de pago
        document.addEventListener('change', (event) => {
            if (event.target.name === 'payment_method') {
                this.handlePaymentMethodChange(event.target.value);
            }
        });

        // Escuchar submit de formularios de pago
        document.addEventListener('submit', (event) => {
            if (event.target.classList.contains('payment-form')) {
                event.preventDefault();
                this.handlePaymentSubmit(event.target);
            }
        });
    }

    handlePaymentMethodChange(method) {
        // Mostrar/ocultar campos específicos del método
        const methodFields = document.querySelectorAll('.payment-method-fields');
        methodFields.forEach(field => {
            field.style.display = 'none';
        });

        const selectedFields = document.querySelector(`.payment-method-fields[data-method="${method}"]`);
        if (selectedFields) {
            selectedFields.style.display = 'block';
        }

        // Actualizar UI del método seleccionado
        this.updatePaymentMethodUI(method);
    }

    updatePaymentMethodUI(method) {
        const methodInfo = this.paymentMethods?.[method];
        if (!methodInfo) return;

        // Actualizar información del método
        const methodName = document.querySelector('.selected-method-name');
        const methodIcon = document.querySelector('.selected-method-icon');
        const methodDescription = document.querySelector('.selected-method-description');

        if (methodName) methodName.textContent = methodInfo.name;
        if (methodIcon) methodIcon.src = methodInfo.icon;
        if (methodDescription) methodDescription.textContent = methodInfo.description;

        // Actualizar límites y comisiones
        this.updatePaymentLimits(methodInfo);
    }

    updatePaymentLimits(methodInfo) {
        const limits = methodInfo.limits;
        const fees = methodInfo.fees;

        // Mostrar límites si existen
        const limitsContainer = document.querySelector('.payment-limits');
        if (limitsContainer && limits) {
            limitsContainer.innerHTML = `
                <small class="text-muted">
                    Límite: S/. ${limits.min} - S/. ${limits.max}
                    ${fees > 0 ? `| Comisión: S/. ${fees.toFixed(2)}` : '| Sin comisiones'}
                </small>
            `;
        }
    }

    async handlePaymentSubmit(form) {
        try {
            const formData = new FormData(form);
            const paymentData = Object.fromEntries(formData.entries());

            // Validar datos del pago
            const validation = this.validatePaymentData(paymentData);
            if (!validation.valid) {
                this.showPaymentError(validation.errors);
                return;
            }

            // Mostrar loading
            this.showPaymentLoading(true);

            // Crear pago
            const result = await this.createPayment(paymentData);

            if (result.success) {
                this.currentPayment = result;
                this.showPaymentQR(result);
                this.startPaymentPolling(result.payment_id, result.method);
            } else {
                this.showPaymentError([result.error]);
            }

        } catch (error) {
            console.error('Error handling payment submit:', error);
            this.showPaymentError(['Error al procesar el pago']);
        } finally {
            this.showPaymentLoading(false);
        }
    }

    validatePaymentData(data) {
        const errors = [];

        // Validar método de pago
        if (!data.payment_method) {
            errors.push('Selecciona un método de pago');
        }

        // Validar número de teléfono
        if (!data.phone_number) {
            errors.push('Ingresa tu número de teléfono');
        } else if (!this.validatePhoneNumber(data.phone_number)) {
            errors.push('El número de teléfono no es válido (debe ser 9xxxxxxxx)');
        }

        // Validar monto
        const amount = parseFloat(data.amount);
        if (!amount || amount <= 0) {
            errors.push('El monto debe ser mayor a 0');
        }

        const methodInfo = this.paymentMethods?.[data.payment_method];
        if (methodInfo && methodInfo.limits) {
            if (amount < methodInfo.limits.min) {
                errors.push(`El monto mínimo es S/. ${methodInfo.limits.min}`);
            }
            if (amount > methodInfo.limits.max) {
                errors.push(`El monto máximo es S/. ${methodInfo.limits.max}`);
            }
        }

        return {
            valid: errors.length === 0,
            errors: errors
        };
    }

    validatePhoneNumber(phone) {
        // Validar formato peruano: 9xxxxxxxx
        const pattern = /^9\d{8}$/;
        return pattern.test(phone);
    }

    async createPayment(paymentData) {
        try {
            const response = await fetch('/api/payments/create', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(paymentData)
            });

            if (!response.ok) {
                throw new Error('Error al crear el pago');
            }

            return await response.json();
        } catch (error) {
            console.error('Error creating payment:', error);
            return {
                success: false,
                error: error.message
            };
        }
    }

    showPaymentQR(paymentData) {
        // Ocultar formulario de pago
        const paymentForm = document.querySelector('.payment-form-container');
        if (paymentForm) {
            paymentForm.style.display = 'none';
        }

        // Mostrar QR y instrucciones
        const qrContainer = document.querySelector('.payment-qr-container');
        if (qrContainer) {
            qrContainer.style.display = 'block';
            
            qrContainer.innerHTML = `
                <div class="text-center">
                    <h4 class="mb-3">Escanea el código QR</h4>
                    <div class="qr-code mb-3">
                        <img src="${paymentData.qr_code}" alt="QR Code" class="img-fluid" style="max-width: 250px;">
                    </div>
                    <p class="mb-2">Abre ${paymentData.method === 'yape' ? 'Yape' : 'Plin'} y escanea este código</p>
                    <p class="text-muted small mb-3">
                        Monto: S/. ${paymentData.amount} | 
                        Expira: ${new Date(paymentData.expires_at).toLocaleTimeString()}
                    </p>
                    <div class="payment-status mb-3">
                        <div class="spinner-border text-primary" role="status">
                            <span class="visually-hidden">Verificando pago...</span>
                        </div>
                        <p class="mt-2">Esperando pago...</p>
                    </div>
                    <button type="button" class="btn btn-outline-secondary btn-sm" onclick="mobilePaymentManager.cancelPayment()">
                        Cancelar
                    </button>
                </div>
            `;
        }
    }

    startPaymentPolling(paymentId, method) {
        // Iniciar polling para verificar el estado del pago
        this.pollingInterval = setInterval(async () => {
            try {
                const status = await this.checkPaymentStatus(paymentId, method);
                
                if (status.success) {
                    if (status.status === 'completed') {
                        this.handlePaymentSuccess(status);
                    } else if (status.status === 'expired') {
                        this.handlePaymentExpired();
                    }
                }
            } catch (error) {
                console.error('Error checking payment status:', error);
            }
        }, 3000); // Verificar cada 3 segundos

        // Auto-cancelar después de 15 minutos
        setTimeout(() => {
            this.cancelPayment();
        }, 15 * 60 * 1000);
    }

    async checkPaymentStatus(paymentId, method) {
        try {
            const response = await fetch(`/api/payments/status/${paymentId}?method=${method}`);
            if (response.ok) {
                return await response.json();
            }
            return { success: false };
        } catch (error) {
            console.error('Error checking payment status:', error);
            return { success: false };
        }
    }

    handlePaymentSuccess(statusData) {
        // Detener polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }

        // Mostrar éxito
        const qrContainer = document.querySelector('.payment-qr-container');
        if (qrContainer) {
            qrContainer.innerHTML = `
                <div class="text-center">
                    <div class="success-icon mb-3">
                        <i class="fas fa-check-circle fa-4x text-success"></i>
                    </div>
                    <h4 class="mb-3">¡Pago Exitoso!</h4>
                    <p class="mb-2">Tu pago ha sido procesado correctamente</p>
                    <p class="text-muted small mb-3">
                        Transacción: ${statusData.transaction_id}<br>
                        Monto: S/. ${statusData.amount}
                    </p>
                    <button type="button" class="btn btn-primary" onclick="mobilePaymentManager.completePayment()">
                        Continuar
                    </button>
                </div>
            `;
        }

        // Enviar evento de éxito
        this.dispatchPaymentEvent('payment-success', statusData);
    }

    handlePaymentExpired() {
        // Detener polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }

        // Mostrar expiración
        const qrContainer = document.querySelector('.payment-qr-container');
        if (qrContainer) {
            qrContainer.innerHTML = `
                <div class="text-center">
                    <div class="expired-icon mb-3">
                        <i class="fas fa-clock fa-4x text-warning"></i>
                    </div>
                    <h4 class="mb-3">Pago Expirado</h4>
                    <p class="mb-3">El tiempo para el pago ha expirado</p>
                    <button type="button" class="btn btn-primary" onclick="mobilePaymentManager.retryPayment()">
                        Reintentar
                    </button>
                </div>
            `;
        }

        // Enviar evento de expiración
        this.dispatchPaymentEvent('payment-expired', {});
    }

    cancelPayment() {
        // Detener polling
        if (this.pollingInterval) {
            clearInterval(this.pollingInterval);
            this.pollingInterval = null;
        }

        // Restaurar formulario
        const paymentForm = document.querySelector('.payment-form-container');
        const qrContainer = document.querySelector('.payment-qr-container');

        if (paymentForm) paymentForm.style.display = 'block';
        if (qrContainer) {
            qrContainer.style.display = 'none';
            qrContainer.innerHTML = '';
        }

        // Limpiar pago actual
        this.currentPayment = null;

        // Enviar evento de cancelación
        this.dispatchPaymentEvent('payment-cancelled', {});
    }

    retryPayment() {
        this.cancelPayment();
        // El formulario se reinicia automáticamente
    }

    completePayment() {
        // Redirigir o completar acción
        if (this.currentPayment && this.currentPayment.redirect_url) {
            window.location.href = this.currentPayment.redirect_url;
        } else {
            window.location.reload();
        }
    }

    showPaymentLoading(show) {
        const submitButton = document.querySelector('.payment-form button[type="submit"]');
        if (submitButton) {
            if (show) {
                submitButton.disabled = true;
                submitButton.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span>Procesando...';
            } else {
                submitButton.disabled = false;
                submitButton.innerHTML = 'Pagar';
            }
        }
    }

    showPaymentError(errors) {
        const errorContainer = document.querySelector('.payment-errors');
        if (errorContainer) {
            errorContainer.innerHTML = `
                <div class="alert alert-danger">
                    <i class="fas fa-exclamation-triangle me-2"></i>
                    ${errors.join('<br>')}
                </div>
            `;
            errorContainer.style.display = 'block';

            // Ocultar después de 5 segundos
            setTimeout(() => {
                errorContainer.style.display = 'none';
            }, 5000);
        }
    }

    dispatchPaymentEvent(eventType, data) {
        const event = new CustomEvent(eventType, { detail: data });
        document.dispatchEvent(event);
    }

    // Métodos públicos
    async initiatePayment(amount, ventaId, description = 'Pago JUNO EXPRESS') {
        // Abrir modal de pago con monto predefinido
        const modal = document.querySelector('#paymentModal');
        if (modal) {
            // Establecer monto
            const amountInput = modal.querySelector('input[name="amount"]');
            if (amountInput) amountInput.value = amount;

            // Establecer venta_id
            const ventaIdInput = modal.querySelector('input[name="venta_id"]');
            if (ventaIdInput) ventaIdInput.value = ventaId;

            // Establecer descripción
            const descInput = modal.querySelector('input[name="description"]');
            if (descInput) descInput.value = description;

            // Mostrar modal
            const bsModal = new bootstrap.Modal(modal);
            bsModal.show();
        }
    }

    formatAmount(amount) {
        return new Intl.NumberFormat('es-PE', {
            style: 'currency',
            currency: 'PEN'
        }).format(amount);
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.mobilePaymentManager = new MobilePaymentManager();
    
    // Exponer globalmente
    window.MobilePaymentManager = MobilePaymentManager;
});

// Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = MobilePaymentManager;
}
