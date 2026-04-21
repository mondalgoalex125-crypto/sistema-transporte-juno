# 📋 Documentación Detallada de Funcionalidades

## 🎯 Sistema de Gestión de Ventas para Empresa de Transporte

---

## 📊 DIMENSIÓN 1: PLANIFICACIÓN

### 🗓️ Gestión de Viajes

**Funcionalidades:**
- ✅ Programar nuevos viajes con fecha y hora específica
- ✅ Seleccionar ruta desde el catálogo existente
- ✅ Definir cantidad de asientos disponibles (1-60)
- ✅ Visualización de todos los viajes programados
- ✅ Estados de viaje: Programado, En Curso, Completado, Cancelado
- ✅ Barra de ocupación visual por viaje
- ✅ Control automático de asientos disponibles

**Campos del Formulario:**
- Ruta (selección de rutas activas)
- Fecha de Salida (calendario)
- Hora de Salida (selector de hora)
- Asientos Totales (número, default: 40)

**Vista de Lista:**
- ID del viaje
- Ruta completa (Origen → Destino)
- Fecha y hora de salida
- Asientos disponibles vs totales
- Estado actual del viaje
- Porcentaje de ocupación con barra de progreso

---

### 🛣️ Gestión de Rutas

**Funcionalidades:**
- ✅ Crear nuevas rutas de transporte
- ✅ Definir origen y destino
- ✅ Establecer precio por boleto
- ✅ Indicar duración estimada del viaje
- ✅ Activar/desactivar rutas
- ✅ Ver cantidad de viajes programados por ruta

**Campos del Formulario:**
- Origen (texto libre)
- Destino (texto libre)
- Precio en Soles (decimal, ej: 80.00)
- Duración (texto, ej: "16 horas")

**Tarjetas de Ruta Muestran:**
- Número de ruta
- Estado (Activa/Inactiva)
- Origen y destino destacados
- Precio en formato monetario
- Duración del viaje
- Cantidad de viajes programados

---

## 👥 DIMENSIÓN 2: ATENCIÓN AL CLIENTE

### 💬 Sistema de Consultas (Vista Pasajero)

**Funcionalidades:**
- ✅ Enviar consultas al equipo administrativo
- ✅ Formulario con asunto y mensaje
- ✅ Ver historial completo de consultas
- ✅ Visualizar respuestas del equipo
- ✅ Estados: Pendiente, Respondida
- ✅ Fecha y hora de consulta y respuesta

**Proceso:**
1. Pasajero completa formulario (asunto + mensaje)
2. Sistema registra consulta como "Pendiente"
3. Administrador recibe notificación
4. Administrador responde la consulta
5. Pasajero ve la respuesta en su panel

---

### 🎧 Atención al Cliente (Vista Administrador)

**Funcionalidades:**
- ✅ Ver todas las consultas de clientes
- ✅ Filtrar por estado (Todas/Pendientes/Respondidas)
- ✅ Ver información completa del cliente
- ✅ Responder consultas directamente
- ✅ Contador de consultas pendientes
- ✅ Notificaciones visuales en el menú

**Información Mostrada:**
- Asunto de la consulta
- Mensaje del cliente
- Datos del cliente (nombre, email, teléfono)
- Fecha y hora de la consulta
- Estado actual
- Respuesta (si existe)

**Filtros Disponibles:**
- 📋 Todas las consultas
- ⏰ Solo pendientes
- ✅ Solo respondidas

---

## 💰 DIMENSIÓN 3: CONTROL COMERCIAL

### 📈 Dashboard de Ventas

**Estadísticas en Tiempo Real:**
- 💵 **Ingresos Totales**: Suma de todas las ventas confirmadas
- 🎫 **Boletos Vendidos**: Cantidad total de boletos
- 👥 **Total Pasajeros**: Usuarios registrados
- 🚌 **Total Viajes**: Viajes programados

**Gráfico Interactivo:**
- 📊 Ventas de los últimos 7 días
- Visualización con Chart.js
- Datos actualizados dinámicamente vía API
- Formato monetario en eje Y

**Ventas Recientes:**
- Tabla con las últimas 10 ventas
- ID de venta
- Nombre del cliente
- Ruta del viaje
- Cantidad de boletos
- Total pagado
- Fecha y hora de compra

---

### 💼 Reportes Comerciales

**Métricas del Día:**
- 💵 Ingresos del día actual
- 🎫 Boletos vendidos hoy
- 📊 Comparativa con días anteriores

**Métricas del Mes:**
- 💰 Ingresos totales del mes
- 📈 Tendencia de ventas
- 🎯 Proyecciones

**Registro Completo de Ventas:**
- ID de venta
- Cliente (nombre y email)
- Ruta completa
- Fecha del viaje
- Fecha de compra
- Cantidad de boletos
- Método de pago
- Total en soles
- Estado (Confirmado/Cancelado)

---

## 🎫 FUNCIONALIDADES PARA PASAJEROS

### 🏠 Dashboard Personal

**Estadísticas Personales:**
- 🛣️ Viajes realizados
- 🎫 Boletos comprados
- 📅 Miembro desde (fecha de registro)

**Viajes Disponibles:**
- Muestra próximos 6 viajes disponibles
- Información completa de cada viaje
- Botón directo para comprar
- Enlace a búsqueda avanzada

**Últimas Compras:**
- Tabla con últimas 5 compras
- Fecha de compra
- Ruta del viaje
- Fecha del viaje
- Cantidad de boletos
- Total pagado
- Estado

---

### 🔍 Búsqueda de Viajes

**Filtros de Búsqueda:**
- 📍 Origen (búsqueda por texto)
- 📍 Destino (búsqueda por texto)
- 📅 Fecha (selector de calendario)

**Resultados Muestran:**
- Ruta completa con iconos
- Fecha y hora de salida
- Duración del viaje
- Asientos disponibles
- Precio destacado
- Botón de compra

**Características:**
- Búsqueda flexible (no requiere todos los campos)
- Resultados en tarjetas visuales
- Ordenados por fecha de salida
- Contador de resultados encontrados

---

### 🛒 Compra de Boletos

**Proceso de Compra:**

1. **Información del Viaje:**
   - Origen y destino destacados
   - Fecha y hora de salida
   - Duración del viaje
   - Asientos disponibles

2. **Formulario de Compra:**
   - Cantidad de boletos (selector numérico)
   - Validación de disponibilidad
   - Método de pago:
     * Tarjeta de Crédito/Débito
     * Efectivo (pagar en terminal)
     * Transferencia Bancaria
     * Yape/Plin

3. **Resumen de Compra:**
   - Precio unitario
   - Cantidad seleccionada
   - Total a pagar (actualización dinámica)
   - Información sobre envío de boleto

4. **Confirmación:**
   - Validación de asientos disponibles
   - Actualización automática de disponibilidad
   - Registro de la venta
   - Mensaje de éxito

---

### 🎟️ Mis Boletos

**Información por Boleto:**
- Número de boleto único
- Estado (Confirmado/Cancelado)
- Ruta completa
- Fecha y hora del viaje
- Cantidad de boletos
- Método de pago utilizado
- Total pagado
- Fecha de compra
- Mensaje de confirmación

**Características:**
- Tarjetas visuales con código de colores
- Verde para confirmados
- Rojo para cancelados
- Información completa y clara
- Historial completo de compras

---

## 👨‍💼 FUNCIONALIDADES ADMINISTRATIVAS

### 📊 Dashboard Administrativo

**Panel de Control:**
- 4 tarjetas con estadísticas principales
- Gráfico de ventas de 7 días
- Tabla de ventas recientes
- Accesos rápidos a funciones principales
- Alertas de consultas pendientes

**Accesos Rápidos:**
- ➕ Crear Viaje
- 🛣️ Gestionar Rutas
- 📈 Ver Reportes
- 💬 Consultas (con contador)

---

### 👥 Gestión de Usuarios

**Funcionalidades:**
- Ver lista completa de usuarios
- Información detallada de cada usuario
- Filtrado por rol (Admin/Pasajero)
- Estadísticas de usuarios
- Cantidad de compras por usuario

**Información Mostrada:**
- ID de usuario
- Nombre completo
- Email
- Teléfono
- Rol con badge visual
- Fecha de registro
- Cantidad de compras realizadas

---

## 🎨 CARACTERÍSTICAS DE DISEÑO

### 🌈 Paleta de Colores

**Colores Principales:**
- 🔵 Primary: #2563eb (Azul)
- 🟣 Secondary: #7c3aed (Púrpura)
- 🟢 Success: #10b981 (Verde)
- 🔴 Danger: #ef4444 (Rojo)
- 🟡 Warning: #f59e0b (Naranja)
- 🔵 Info: #06b6d4 (Cyan)

**Gradientes:**
- Fondos con gradientes suaves
- Botones con efectos degradados
- Tarjetas estadísticas coloridas

---

### ✨ Animaciones y Efectos

**Interactividad:**
- ⬆️ Hover en tarjetas (elevación)
- 🔄 Transiciones suaves
- 📊 Animación de entrada (fade-in)
- 🎯 Botones con efecto de escala
- 💫 Sombras dinámicas

---

### 📱 Diseño Responsivo

**Breakpoints:**
- 📱 Móvil: < 768px
- 📱 Tablet: 768px - 992px
- 💻 Desktop: > 992px

**Adaptaciones:**
- Menú colapsable en móvil
- Tarjetas apiladas en pantallas pequeñas
- Tablas con scroll horizontal
- Sidebar oculto en móvil

---

## 🔒 SEGURIDAD

### 🛡️ Características de Seguridad

**Autenticación:**
- ✅ Contraseñas encriptadas (Werkzeug)
- ✅ Sistema de sesiones seguras
- ✅ Validación de credenciales
- ✅ Cierre de sesión seguro

**Autorización:**
- ✅ Decoradores de protección de rutas
- ✅ Validación de roles (admin/pasajero)
- ✅ Redirección automática según rol
- ✅ Mensajes de error apropiados

**Validaciones:**
- ✅ Formularios validados en cliente y servidor
- ✅ Prevención de SQL injection (ORM)
- ✅ Validación de disponibilidad de asientos
- ✅ Verificación de permisos en cada acción

---

## 🚀 CARACTERÍSTICAS TÉCNICAS

### ⚡ Rendimiento

**Optimizaciones:**
- Consultas SQL optimizadas
- Carga asíncrona de gráficos
- CDN para librerías externas
- Caché de sesiones

### 🔄 Actualizaciones Dinámicas

**AJAX/API:**
- Gráficos actualizados vía API
- Cálculo dinámico de totales
- Filtrado en tiempo real
- Validaciones instantáneas

### 📦 Base de Datos

**Modelos:**
- Usuario (autenticación y perfil)
- Ruta (origen, destino, precio)
- Viaje (programación y disponibilidad)
- Venta (transacciones)
- Consulta (atención al cliente)

**Relaciones:**
- Usuario → Ventas (1:N)
- Usuario → Consultas (1:N)
- Ruta → Viajes (1:N)
- Viaje → Ventas (1:N)

---

## 📞 FLUJOS DE TRABAJO

### 🎫 Flujo de Compra de Boleto

1. Pasajero busca viajes disponibles
2. Selecciona viaje deseado
3. Elige cantidad de boletos
4. Selecciona método de pago
5. Confirma la compra
6. Sistema valida disponibilidad
7. Actualiza asientos disponibles
8. Registra la venta
9. Muestra confirmación
10. Boleto disponible en "Mis Boletos"

### 💬 Flujo de Atención al Cliente

1. Pasajero envía consulta
2. Sistema registra como "Pendiente"
3. Contador en panel admin se actualiza
4. Admin ve consulta en su panel
5. Admin escribe respuesta
6. Sistema marca como "Respondida"
7. Pasajero ve respuesta en su panel
8. Historial completo guardado

### 🗓️ Flujo de Planificación de Viaje

1. Admin accede a Planificación
2. Selecciona ruta existente
3. Define fecha y hora
4. Establece cantidad de asientos
5. Confirma creación
6. Viaje aparece en lista de programados
7. Viaje visible para pasajeros
8. Sistema controla disponibilidad automáticamente

---

## 🎯 CASOS DE USO

### Caso 1: Pasajero Compra Boleto
**Actor:** Pasajero registrado
**Objetivo:** Comprar boleto para un viaje
**Flujo:** Buscar → Seleccionar → Comprar → Confirmar

### Caso 2: Admin Programa Viaje
**Actor:** Administrador
**Objetivo:** Programar nuevo viaje
**Flujo:** Planificación → Crear → Definir → Confirmar

### Caso 3: Atención al Cliente
**Actor:** Pasajero y Administrador
**Objetivo:** Resolver consulta
**Flujo:** Enviar → Revisar → Responder → Confirmar

---

## 📈 MÉTRICAS Y REPORTES

### Métricas Disponibles:
- 💰 Ingresos totales, diarios y mensuales
- 🎫 Boletos vendidos por período
- 👥 Cantidad de usuarios registrados
- 🚌 Viajes programados y completados
- 📊 Ocupación promedio de viajes
- 💳 Distribución por método de pago
- 🗓️ Tendencias de ventas (gráfico 7 días)

---

**Sistema completo y funcional listo para usar** ✅
