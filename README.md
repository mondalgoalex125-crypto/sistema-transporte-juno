# 🚌 Sistema de Gestión de Ventas para Empresa de Transporte

Sistema web completo desarrollado en Python Flask para la gestión de ventas de una empresa de transporte, con tres dimensiones principales: **Planificación**, **Atención al Cliente** y **Control Comercial**.

## ✨ Características Principales

### 👥 Dos Tipos de Usuarios

#### 🔐 Administrador
- **Dashboard Administrativo** con estadísticas en tiempo real
- **Planificación de Viajes**: Programar y gestionar viajes
- **Gestión de Rutas**: Crear y administrar rutas de transporte
- **Control Comercial**: Reportes de ventas, ingresos y análisis
- **Atención al Cliente**: Responder consultas de pasajeros
- **Gestión de Usuarios**: Ver y administrar usuarios del sistema

#### 🎫 Pasajero
- **Dashboard Personal** con historial de compras
- **Búsqueda de Viajes**: Buscar por origen, destino y fecha
- **Compra de Boletos**: Sistema de compra en línea
- **Mis Boletos**: Ver historial de compras
- **Atención al Cliente**: Enviar consultas y recibir respuestas

## 🎨 Diseño

- **Interfaz Moderna y Responsiva**: Compatible con todos los dispositivos
- **Colores Vibrantes**: Gradientes modernos y atractivos
- **Animaciones Suaves**: Transiciones y efectos visuales
- **Gráficos Dinámicos**: Visualización de datos con Chart.js
- **UX Optimizada**: Navegación intuitiva y fácil de usar

## 🛠️ Tecnologías Utilizadas

- **Backend**: Python 3.x + Flask
- **Base de Datos**: SQLite (SQLAlchemy ORM)
- **Frontend**: HTML5, CSS3, JavaScript
- **Framework CSS**: Bootstrap 5
- **Iconos**: Font Awesome 6
- **Gráficos**: Chart.js

## 📦 Instalación

### Requisitos Previos
- Python 3.7 o superior
- pip (gestor de paquetes de Python)

### Pasos de Instalación

1. **Clonar o descargar el proyecto**
   ```bash
   cd d:/JUNNO/sistema_transporte
   ```

2. **Crear un entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   ```

3. **Activar el entorno virtual**
   - Windows:
     ```bash
     venv\Scripts\activate
     ```
   - Linux/Mac:
     ```bash
     source venv/bin/activate
     ```

4. **Instalar las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

6. **Abrir en el navegador**
   ```
   http://localhost:5000
   ```

## 🔑 Credenciales de Acceso

### Administrador
- **Email**: admin@transporte.com
- **Contraseña**: admin123

### Pasajero
- Crear una nueva cuenta desde la página de registro

## 📊 Estructura del Proyecto

```
sistema_transporte/
│
├── app.py                          # Aplicación principal Flask
├── requirements.txt                # Dependencias del proyecto
├── README.md                       # Este archivo
│
├── templates/                      # Plantillas HTML
│   ├── base.html                  # Plantilla base
│   ├── index.html                 # Página de inicio
│   ├── login.html                 # Inicio de sesión
│   ├── registro.html              # Registro de usuarios
│   │
│   ├── pasajero/                  # Vistas de pasajero
│   │   ├── dashboard.html         # Dashboard del pasajero
│   │   ├── buscar_viajes.html     # Búsqueda de viajes
│   │   ├── comprar_boleto.html    # Compra de boletos
│   │   ├── mis_boletos.html       # Historial de boletos
│   │   └── consultas.html         # Atención al cliente
│   │
│   └── admin/                     # Vistas de administrador
│       ├── dashboard.html         # Dashboard administrativo
│       ├── planificacion.html     # Planificación de viajes
│       ├── rutas.html             # Gestión de rutas
│       ├── control_comercial.html # Control comercial
│       ├── atencion_cliente.html  # Atención al cliente
│       └── usuarios.html          # Gestión de usuarios
│
└── transporte.db                  # Base de datos SQLite (se crea automáticamente)
```

## 🎯 Funcionalidades por Dimensión

### 📅 Planificación
- Crear y programar viajes
- Gestionar rutas (origen, destino, precio, duración)
- Control de asientos disponibles
- Visualización de ocupación de viajes
- Estados de viajes (programado, en curso, completado, cancelado)

### 👨‍💼 Atención al Cliente
- Sistema de consultas y respuestas
- Historial de consultas por usuario
- Notificaciones de consultas pendientes
- Respuestas en tiempo real del equipo administrativo

### 📈 Control Comercial
- Dashboard con estadísticas en tiempo real
- Gráficos de ventas de los últimos 7 días
- Reportes de ingresos diarios y mensuales
- Registro completo de todas las ventas
- Análisis de boletos vendidos
- Métodos de pago registrados

## 🔒 Seguridad

- Contraseñas encriptadas con Werkzeug
- Sistema de autenticación con sesiones
- Decoradores para proteger rutas
- Validación de roles (admin/pasajero)
- Protección contra accesos no autorizados

## 🚀 Características Dinámicas

- **Búsqueda en Tiempo Real**: Filtrado de viajes por múltiples criterios
- **Cálculo Automático**: Total de compra se actualiza dinámicamente
- **Gráficos Interactivos**: Visualización de datos con Chart.js
- **Validaciones**: Formularios con validación del lado del cliente y servidor
- **Mensajes Flash**: Notificaciones de éxito, error y advertencia
- **Responsive Design**: Adaptable a móviles, tablets y escritorio

## 📝 Datos de Ejemplo

El sistema se inicializa con:
- 1 usuario administrador
- 5 rutas de ejemplo (Lima-Arequipa, Lima-Cusco, etc.)
- 30 viajes programados para los próximos 10 días
- Precios realistas y duraciones de viaje

## 🔧 Personalización

### Cambiar la Clave Secreta
En `app.py`, línea 11:
```python
app.config['SECRET_KEY'] = 'tu_clave_secreta_aqui_cambiar_en_produccion'
```

### Modificar Colores
En `templates/base.html`, sección `<style>`:
```css
:root {
    --primary-color: #2563eb;
    --secondary-color: #7c3aed;
    /* ... más colores ... */
}
```

### Agregar Más Rutas
Acceder como administrador → Gestión de Rutas → Crear Nueva Ruta

## 🐛 Solución de Problemas

### Error: "No module named 'flask'"
```bash
pip install -r requirements.txt
```

### Error: "Address already in use"
El puerto 5000 está ocupado. Cambiar en `app.py`:
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

### La base de datos no se crea
Asegurarse de tener permisos de escritura en el directorio del proyecto.

## 📱 Compatibilidad

- ✅ Chrome/Edge (recomendado)
- ✅ Firefox
- ✅ Safari
- ✅ Opera
- ✅ Dispositivos móviles

## 🎓 Uso del Sistema

### Para Pasajeros:
1. Registrarse en el sistema
2. Iniciar sesión
3. Buscar viajes disponibles
4. Seleccionar viaje y cantidad de boletos
5. Completar la compra
6. Ver boletos en "Mis Boletos"
7. Enviar consultas si es necesario

### Para Administradores:
1. Iniciar sesión con credenciales de admin
2. Ver estadísticas en el dashboard
3. Crear rutas nuevas
4. Programar viajes
5. Revisar ventas en Control Comercial
6. Responder consultas de clientes
7. Gestionar usuarios

## 📞 Soporte

Para preguntas o problemas, contactar al equipo de desarrollo.

## 📄 Licencia

Este proyecto es de código abierto y está disponible para uso educativo y comercial.

---

**Desarrollado con ❤️ usando Python Flask**

🚌 **TransporteExpress** - Tu viaje comienza aquí
