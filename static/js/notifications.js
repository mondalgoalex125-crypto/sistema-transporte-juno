// Sistema de Notificaciones Push para JUNO EXPRESS
class NotificationManager {
    constructor() {
        this.isSupported = 'Notification' in window && 'serviceWorker' in navigator;
        this.permission = 'default';
        this.subscription = null;
        this.init();
    }

    async init() {
        if (!this.isSupported) {
            console.warn('Notificaciones no soportadas en este navegador');
            return;
        }

        // Verificar permiso actual
        this.permission = Notification.permission;
        
        // Si ya hay permiso, registrar subscription
        if (this.permission === 'granted') {
            await this.registerSubscription();
        }

        // Escuchar mensajes del service worker
        navigator.serviceWorker.addEventListener('message', this.handleServiceWorkerMessage.bind(this));
        
        // Configurar handlers para notificaciones programadas
        this.setupScheduledNotifications();
    }

    async requestPermission() {
        if (!this.isSupported) {
            throw new Error('Notificaciones no soportadas');
        }

        if (this.permission === 'granted') {
            return true;
        }

        try {
            const permission = await Notification.requestPermission();
            this.permission = permission;
            
            if (permission === 'granted') {
                await this.registerSubscription();
                return true;
            } else {
                throw new Error('Permiso de notificaciones denegado');
            }
        } catch (error) {
            console.error('Error solicitando permiso de notificaciones:', error);
            throw error;
        }
    }

    async registerSubscription() {
        try {
            const registration = await navigator.serviceWorker.ready;
            
            // Crear subscription para push notifications
            const subscription = await registration.pushManager.subscribe({
                userVisibleOnly: true,
                applicationServerKey: this.urlBase64ToUint8Array(this.getVapidKey())
            });

            this.subscription = subscription;
            
            // Enviar subscription al servidor
            await this.sendSubscriptionToServer(subscription);
            
            console.log('Subscription registrada exitosamente');
            return subscription;
        } catch (error) {
            console.error('Error registrando subscription:', error);
            throw error;
        }
    }

    async sendSubscriptionToServer(subscription) {
        try {
            const userId = this.getCurrentUserId();
            if (!userId) {
                console.warn('No user ID available for subscription');
                return;
            }

            const response = await fetch('/api/notifications/subscribe', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    subscription: subscription
                })
            });

            if (!response.ok) {
                throw new Error('Error enviando subscription al servidor');
            }

            console.log('Subscription enviada al servidor');
        } catch (error) {
            console.error('Error enviando subscription:', error);
        }
    }

    getCurrentUserId() {
        // Obtener user ID del session storage o localStorage
        return sessionStorage.getItem('user_id') || localStorage.getItem('user_id');
    }

    // Mostrar notificación local (para testing o fallback)
    showLocalNotification(title, options = {}) {
        if (!this.isSupported || this.permission !== 'granted') {
            return;
        }

        const notification = new Notification(title, {
            icon: '/static/images/bus-icon.png',
            badge: '/static/images/badge.png',
            tag: 'juno-express',
            renotify: true,
            requireInteraction: false,
            ...options
        });

        // Manejar clics en notificación
        notification.onclick = (event) => {
            event.preventDefault();
            
            if (options.data && options.data.url) {
                window.open(options.data.url, '_blank');
            } else {
                window.focus();
            }
            
            notification.close();
        };

        // Auto-cerrar después de 5 segundos
        setTimeout(() => {
            notification.close();
        }, 5000);
    }

    // Programar notificación local
    scheduleLocalNotification(title, options, delay) {
        setTimeout(() => {
            this.showLocalNotification(title, options);
        }, delay);
    }

    // Enviar recordatorio de viaje
    async scheduleTravelReminder(viajeData) {
        const departureTime = new Date(`${viajeData.fecha_salida} ${viajeData.hora_salida}`);
        const reminderTime = new Date(departureTime.getTime() - 2 * 60 * 60 * 1000); // 2 horas antes
        const now = new Date();
        
        if (reminderTime > now) {
            const delay = reminderTime.getTime() - now.getTime();
            this.scheduleLocalNotification(
                'Recordatorio de Viaje - JUNO EXPRESS',
                {
                    body: `Tu viaje a ${viajeData.destino} sale en 2 horas. ¡No te quedes!`,
                    data: {
                        type: 'travel_reminder',
                        url: `/pasajero/mis-boletos`
                    }
                },
                delay
            );
        }
    }

    // Configurar handlers para diferentes tipos de notificaciones
    handleServiceWorkerMessage(event) {
        const data = event.data;
        
        if (data.type === 'notification-click') {
            this.handleNotificationClick(data);
        } else if (data.type === 'notification-close') {
            this.handleNotificationClose(data);
        }
    }

    handleNotificationClick(data) {
        const { notification, action } = data;
        
        if (action === 'explore') {
            // Abrir detalles de la notificación
            if (notification.data && notification.data.url) {
                window.location.href = notification.data.url;
            }
        } else if (action === 'close') {
            // Cerrar notificación (ya se cierra automáticamente)
        } else {
            // Acción por defecto: ir al dashboard
            window.location.href = '/dashboard';
        }
    }

    handleNotificationClose(data) {
        console.log('Notification closed:', data);
    }

    // Configurar notificaciones programadas desde el servidor
    setupScheduledNotifications() {
        // Verificar cada minuto si hay notificaciones programadas
        setInterval(async () => {
            await this.checkScheduledNotifications();
        }, 60000);
    }

    async checkScheduledNotifications() {
        try {
            const userId = this.getCurrentUserId();
            if (!userId) return;

            const response = await fetch(`/api/notifications/scheduled/${userId}`);
            if (!response.ok) return;

            const notifications = await response.json();
            
            notifications.forEach(notification => {
                const scheduledTime = new Date(notification.scheduled_time);
                const now = new Date();
                
                if (scheduledTime <= now) {
                    this.showLocalNotification(notification.title, {
                        body: notification.body,
                        data: notification.data
                    });
                }
            });
        } catch (error) {
            console.error('Error checking scheduled notifications:', error);
        }
    }

    // Métodos para diferentes tipos de notificaciones
    async notifyBookingConfirmation(bookingData) {
        if (this.permission === 'granted') {
            this.showLocalNotification(
                'Reserva Confirmada - JUNO EXPRESS',
                {
                    body: `Tu reserva a ${bookingData.destino} está confirmada. Boletos: ${bookingData.cantidad_boletos}`,
                    data: {
                        type: 'booking_confirmation',
                        url: '/pasajero/mis-boletos'
                    }
                }
            );
        }
    }

    async notifyPaymentConfirmation(paymentData) {
        if (this.permission === 'granted') {
            this.showLocalNotification(
                'Pago Recibido - JUNO EXPRESS',
                {
                    body: `Tu pago de S/. ${paymentData.monto} ha sido procesado exitosamente`,
                    data: {
                        type: 'payment_confirmation',
                        url: '/pasajero/mis-boletos'
                    }
                }
            );
        }
    }

    async notifyRouteUpdate(routeData) {
        if (this.permission === 'granted') {
            this.showLocalNotification(
                'Actualización de Ruta - JUNO EXPRESS',
                {
                    body: `La ruta ${routeData.origen} - ${routeData.destino} ha sido actualizada`,
                    data: {
                        type: 'route_update',
                        url: '/pasajero/buscar-viajes'
                    }
                }
            );
        }
    }

    // Utilidad para convertir VAPID key
    urlBase64ToUint8Array(base64String) {
        const padding = '='.repeat((4 - base64String.length % 4) % 4);
        const base64 = (base64String + padding)
            .replace(/-/g, '+')
            .replace(/_/g, '/');

        const rawData = window.atob(base64);
        const outputArray = new Uint8Array(rawData.length);

        for (let i = 0; i < rawData.length; ++i) {
            outputArray[i] = rawData.charCodeAt(i);
        }
        return outputArray;
    }

    // VAPID key (debería venir del servidor)
    getVapidKey() {
        return 'BM_vKTgHz7ZJ6cH2nTj5a1k3Qe8JmXfN4Yw6Zt7U8I9K0L1M2N3O4P5Q6R7S8T9U0V1W2X3Y4Z5';
    }

    // Métodos para gestión de preferencias
    async saveNotificationPreferences(preferences) {
        try {
            const userId = this.getCurrentUserId();
            if (!userId) return;

            const response = await fetch('/api/notifications/preferences', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: userId,
                    preferences: preferences
                })
            });

            if (response.ok) {
                localStorage.setItem('notification_preferences', JSON.stringify(preferences));
            }
        } catch (error) {
            console.error('Error saving notification preferences:', error);
        }
    }

    getNotificationPreferences() {
        const saved = localStorage.getItem('notification_preferences');
        return saved ? JSON.parse(saved) : {
            travel_reminders: true,
            booking_confirmations: true,
            payment_notifications: true,
            route_updates: true,
            promotions: false
        };
    }

    // Método para desuscribirse
    async unsubscribe() {
        try {
            if (this.subscription) {
                await this.subscription.unsubscribe();
                this.subscription = null;
            }

            const userId = this.getCurrentUserId();
            if (userId) {
                await fetch('/api/notifications/unsubscribe', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({ user_id: userId })
                });
            }
        } catch (error) {
            console.error('Error unsubscribing from notifications:', error);
        }
    }
}

// Inicializar notification manager cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.notificationManager = new NotificationManager();
    
    // Exponer globalmente para uso en otras partes
    window.NotificationManager = NotificationManager;
});

// Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = NotificationManager;
}
