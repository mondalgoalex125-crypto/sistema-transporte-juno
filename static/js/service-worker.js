// Service Worker para JUNO EXPRESS - PWA y Cache
const CACHE_NAME = 'juno-express-v1';
const urlsToCache = [
  '/',
  '/static/css/bootstrap.min.css',
  '/static/js/bootstrap.bundle.min.js',
  '/static/js/fontawesome.min.js',
  '/static/images/bus-hero.png',
  '/static/images/chincha.png',
  '/static/images/pisco.png',
  '/static/images/ica.png'
];

// Instalación del Service Worker
self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => {
        return cache.addAll(urlsToCache);
      })
  );
});

// Activación y limpieza de caché antigua
self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(cacheNames => {
      return Promise.all(
        cacheNames.map(cacheName => {
          if (cacheName !== CACHE_NAME) {
            return caches.delete(cacheName);
          }
        })
      );
    })
  );
});

// Estrategia de caché: Network First con fallback a caché
self.addEventListener('fetch', event => {
  event.respondWith(
    fetch(event.request)
      .then(response => {
        // Si la respuesta es válida, la guardamos en caché
        if (response.status === 200) {
          const responseClone = response.clone();
          caches.open(CACHE_NAME)
            .then(cache => {
              cache.put(event.request, responseClone);
            });
        }
        return response;
      })
      .catch(() => {
        // Si falla la red, intentamos desde caché
        return caches.match(event.request)
          .then(response => {
            if (response) {
              return response;
            }
            // Para páginas HTML, devolvemos página offline
            if (event.request.destination === 'document') {
              return caches.match('/offline.html');
            }
          });
      })
  );
});

// Background Sync para sincronización cuando vuelve la conexión
self.addEventListener('sync', event => {
  if (event.tag === 'sync-notifications') {
    event.waitUntil(syncNotifications());
  }
});

// Push notifications
self.addEventListener('push', event => {
  const options = {
    body: event.data ? event.data.text() : 'Nueva notificación de JUNO EXPRESS',
    icon: '/static/images/bus-icon.png',
    badge: '/static/images/badge.png',
    vibrate: [100, 50, 100],
    data: {
      dateOfArrival: Date.now(),
      primaryKey: 1
    },
    actions: [
      {
        action: 'explore',
        title: 'Ver Detalles',
        icon: '/static/images/checkmark.png'
      },
      {
        action: 'close',
        title: 'Cerrar',
        icon: '/static/images/xmark.png'
      }
    ]
  };

  event.waitUntil(
    self.registration.showNotification('JUNO EXPRESS', options)
  );
});

// Manejo de clics en notificaciones
self.addEventListener('notificationclick', event => {
  event.notification.close();

  if (event.action === 'explore') {
    event.waitUntil(
      clients.openWindow('/dashboard')
    );
  } else if (event.action === 'close') {
    // Cerrar notificación
  } else {
    // Acción por defecto: abrir la aplicación
    event.waitUntil(
      clients.openWindow('/')
    );
  }
});

function syncNotifications() {
  // Lógica para sincronizar notificaciones pendientes
  return Promise.resolve();
}
