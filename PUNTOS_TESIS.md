# CAPÍTULO VI: DESARROLLO DEL PROYECTO

## 6.2.3. Problema Solucionado

La empresa Juno Express S.A. enfrentaba una problemática significativa en la gestión de sus procesos de venta de boletos de transporte, donde todos los trámites se realizaban de manera manual o con sistemas desintegrados que generaban múltiples ineficiencias. El sistema manual de ventas producía errores frecuentes en el control de inventario de asientos, ocasionando problemas como el sobreventa de boletos, la falta de disponibilidad real en tiempo real y conflictos en la asignación de pasajeros. Adicionalmente, existía una ausencia total de visibilidad sobre el estado de los viajes, lo que dificultaba tanto a la empresa como a los clientes el seguimiento de sus compras. Los procesos de análisis de ventas eran tediosos y limitados, impidiendo una toma de decisiones basada en datos, y la atención al cliente se realizaba de forma desorganizada sin una estructura clara de consultas y respuestas, generando insatisfacción y falta de trazabilidad en la comunicación.

La implementación del sistema web de gestión de ventas ha permitido automatizar completamente estos procesos manuales, proporcionando un control transaccional riguroso del inventario de asientos mediante Firebase Firestore, mejorando significativamente la experiencia del cliente a través de una plataforma digital intuitiva y accesible, y generando información empresarial valiosa en tiempo real para la gestión administrativa. El sistema ha transformado la operación de Juno Express de un modelo manual a un modelo digital completamente integrado, aumentando la eficiencia operativa, reduciendo errores y facilitando el crecimiento del negocio.

---

## 6.2.4. Funcionamiento General

El sistema Juno Express funciona como una aplicación web responsiva y moderna, accesible desde cualquier dispositivo (computadora, tablet o teléfono) con conexión a internet, sin necesidad de instalación de software adicional. La arquitectura general del sistema se divide en dos interfaces principales: una para pasajeros y otra para administradores.

**Flujo de los Pasajeros:**

Los usuarios pueden acceder al sitio web y navegar por el catálogo de viajes disponibles sin necesidad de autenticación. Sin embargo, para realizar compras de boletos, deben crear una cuenta mediante el proceso de registro, proporcionando información personal básica (nombre, email, teléfono y contraseña). Una vez autenticados, los pasajeros pueden acceder a su dashboard personal, donde visualizan un resumen de sus estadísticas de viajes, un listado de próximos viajes disponibles con botones de compra directa, y un historial de sus últimas compras realizadas.

El proceso de compra es sencillo e intuitivo: el pasajero utiliza la función de búsqueda avanzada para filtrar viajes por origen, destino y fecha deseada. Los resultados se presentan en tarjetas visuales con toda la información relevante (horarios, duración, asientos disponibles y precio). Al seleccionar un viaje, el pasajero puede elegir la cantidad de boletos que desea comprar, visualizar dinámicamente el monto total a pagar, y seleccionar entre varios métodos de pago disponibles (tarjeta de crédito/débito, efectivo, transferencia bancaria o billeteras digitales como Yape/Plin). Una vez confirmada la compra, el sistema registra la transacción y actualiza automáticamente la disponibilidad de asientos del viaje.

Después de completar la compra, el pasajero puede acceder a la sección "Mis Boletos" para ver el historial completo de sus compras con estados actualizados (confirmado o cancelado), información detallada de cada boleto, y todos los detalles de la transacción. Adicionalmente, los pasajeros pueden comunicarse con el equipo de atención al cliente mediante el sistema de consultas integrado, enviando preguntas o dudas que recibirán respuesta del equipo administrativo, con un seguimiento claro del estado de cada consulta.

**Flujo de Administradores:**

Los administradores acceden a un dashboard ejecutivo que proporciona una visión completa del negocio en tiempo real. Este dashboard muestra cuatro métricas clave: ingresos totales generados, cantidad de boletos vendidos, número total de usuarios registrados en el sistema, y cantidad de viajes programados. Adicionalmente, incluye un gráfico interactivo que visualiza las ventas de los últimos 7 días, permitiendo identificar tendencias y patrones de comportamiento. Una sección de ventas recientes muestra los últimos movimientos comerciales con detalles del cliente, ruta, cantidad de boletos y monto.

Desde el dashboard, los administradores pueden acceder a sus funciones principales:

- **Planificación de Viajes:** Pueden crear nuevos viajes seleccionando una ruta existente, especificando fecha y hora de salida, y definiendo la cantidad de asientos disponibles. El sistema valida automáticamente la disponibilidad y permite visualizar todos los viajes programados con sus estados actuales (programado, en curso, completado o cancelado).

- **Gestión de Rutas:** Pueden crear, editar y administrar las rutas de transporte, definiendo origen, destino, precio por boleto y duración estimada del viaje. Las rutas pueden activarse o desactivarse, y el sistema proporciona información sobre cuántos viajes están programados en cada ruta.

- **Control Comercial:** Incluye funcionalidades avanzadas de reportes que permiten analizar el desempeño comercial desde múltiples perspectivas. Los reportes muestran ingresos diarios y mensuales, boletos vendidos por período, métodos de pago utilizados, y tendencias de comportamiento de clientes.

- **Atención al Cliente:** Los administradores pueden visualizar todas las consultas recibidas de los pasajeros, filtrarlas por estado (pendientes, respondidas), ver los detalles completos de cada consulta incluyendo la información del cliente, y responder directamente a través de la plataforma. El sistema notifica automáticamente al cliente cuando su consulta ha sido respondida.

- **Gestión de Usuarios:** Proporciona una vista de todos los usuarios registrados en el sistema con información de contacto, rol asignado, fecha de registro y cantidad de compras realizadas.

El sistema mantiene sincronizado el estado de toda la información: cuando un pasajero realiza una compra, los asientos disponibles se actualizan automáticamente en tiempo real, las estadísticas del dashboard se recalculan, y el administrador recibe notificaciones de nueva actividad comercial. Esta integración permite que tanto clientes como administradores trabajen con información siempre actualizada.

---

## 6.2.5. Usuarios del Sistema

El sistema Juno Express contempla dos tipos de usuarios claramente diferenciados, cada uno con roles, permisos y funcionalidades específicas:

### **Pasajero (Customer)**

El usuario tipo Pasajero es cualquier persona que desea comprar boletos de transporte a través de la plataforma. Sus capacidades y permisos incluyen:

- **Registro y Autenticación:** Crear una cuenta personal proporcionando información básica (nombre completo, email, teléfono y contraseña) y acceder a su cuenta usando sus credenciales.

- **Búsqueda de Viajes:** Utilizar filtros avanzados para buscar viajes disponibles por origen, destino y fecha específica, con visualización clara de horarios, duración, disponibilidad de asientos y precios.

- **Compra de Boletos:** Realizar compras en línea seleccionando cantidad de boletos, eligiendo método de pago (múltiples opciones disponibles), y recibiendo confirmación inmediata.

- **Gestión de Compras:** Acceder a un historial completo de boletos comprados con estados actualizados, detalles de cada transacción, información del viaje, método de pago utilizado y monto total pagado.

- **Atención al Cliente:** Enviar consultas y dudas al equipo administrativo, visualizar el historial de sus consultas, ver respuestas del equipo, y monitorear el estado de cada consulta (pendiente o respondida).

- **Perfil Personal:** Visualizar y actualizar su información personal, cambiar su contraseña, y administrar sus preferencias de cuenta.

### **Administrador (Admin)**

El usuario tipo Administrador representa al personal de Juno Express encargado de la operación y gestión integral del negocio. Sus capacidades y permisos incluyen:

- **Acceso Completo al Panel Administrativo:** Acceso sin restricciones a todas las funcionalidades del sistema y a información confidencial de operaciones.

- **Planificación de Viajes:** Crear y programar nuevos viajes especificando ruta, fecha, hora y capacidad de asientos, visualizar todos los viajes programados y su estado, modificar viajes existentes, y cancelar viajes si es necesario.

- **Gestión de Rutas:** Crear rutas nuevas definiendo origen, destino, precio y duración, editar rutas existentes para actualizar precios o información, activar o desactivar rutas, y visualizar análisis de utilización de rutas.

- **Control Comercial:** Visualizar dashboard ejecutivo con métricas en tiempo real, generar reportes de ventas por período (diario, semanal, mensual), analizar ingresos totales y por ruta, revisar métodos de pago preferidos, e identificar tendencias de comportamiento comercial mediante gráficos interactivos.

- **Gestión de Usuarios:** Visualizar lista completa de usuarios registrados con información de contacto, rol y actividad, filtrar usuarios por criterios específicos, y monitorear crecimiento de la base de usuarios.

- **Atención al Cliente:** Visualizar todas las consultas recibidas de pasajeros con opción de filtrar por estado, responder consultas directamente a través de la plataforma, marcar consultas como respondidas, y mantener un registro del historial de comunicación.

- **Análisis y Reportes Avanzados:** Acceso a reportes de desempeño operativo, análisis de ocupación de viajes, métricas de satisfacción de clientes derivadas de consultas, e información de auditoría del sistema.

---

## 6.2.6. Metodología SCRUM en el Desarrollo

El desarrollo del sistema Juno Express fue ejecutado bajo la metodología ágil SCRUM, permitiendo una gestión flexible, iterativa y adaptativa del proyecto. Esta aproximación permitió responder eficientemente a cambios en los requisitos, mantener comunicación constante con los stakeholders, y garantizar la entrega incremental de funcionalidades de valor.

**Estructura de Sprints:**

El proyecto fue dividido en ciclos de desarrollo de dos semanas de duración (sprints), cada uno con objetivos claramente definidos y entregables específicos. Esta duración permitió un balance efectivo entre la entrega de valor y el tiempo de planificación, facilitando adaptaciones cuando fuera necesario.

**Actividades por Sprint:**

Al inicio de cada sprint se realizaba una reunión de Planificación (Sprint Planning) donde se priorizaban los requisitos del Product Backlog, se desglosaban historias de usuario en tareas técnicas concretas, se estimaba el esfuerzo requerido, y se comprometían los objetivos del sprint. Durante el sprint, se realizaban reuniones diarias de 15 minutos (Daily Standup) donde cada miembro del equipo informaba sobre lo completado el día anterior, lo que planificaba completar en el día actual, y cualquier impedimento que obstaculizara el progreso.

Al finalizar cada sprint se realizaba una reunión de Revisión (Sprint Review) donde se demostraba el software funcional desarrollado a stakeholders y usuarios finales para recopilar retroalimentación inmediata. Esto permitía validar que las funcionalidades desarrolladas cumplían con las expectativas y requisitos del negocio. Inmediatamente después, se realizaba una reunión Retrospectiva (Sprint Retrospective) donde el equipo reflexionaba sobre qué había funcionado bien durante el sprint, qué podría mejorar, y qué acciones específicas implementaría en el próximo ciclo para mejorar la productividad y calidad.

**Beneficios Obtenidos:**

La implementación de SCRUM en el desarrollo de Juno Express proporcionó múltiples beneficios:

- **Detección Temprana de Problemas:** Los ciclos cortos permitieron identificar desviaciones de requisitos o problemas técnicos en etapas tempranas, antes de que impactaran significativamente el cronograma global.

- **Adaptabilidad a Cambios:** La estructura iterativa permitió incorporar nuevos requisitos o cambios en las prioridades sin desestabilizar completamente el plan de desarrollo. Cuando surgían nuevas necesidades del negocio, podían integrarse en los siguientes sprints.

- **Entrega Continua de Valor:** Cada sprint entregaba funcionalidades completas y testadas que podían ser utilizadas inmediatamente, proporcionando valor incremental al negocio de forma continua.

- **Comunicación Efectiva:** Las reuniones frecuentes y estructuradas garantizaban que todos los miembros del equipo estuvieran alineados con los objetivos, y que los stakeholders tuvieran visibilidad constante del progreso.

- **Motivación del Equipo:** Los ciclos cortos con objetivos claros y la demostración visible de progreso mantenían la motivación del equipo alta, y la participación en retrospectivas promovía un ambiente de mejora continua.

- **Calidad del Producto:** La integración de testing y revisión en cada sprint aseguraba que solo código de calidad fuera integrado al sistema principal, reduciendo problemas en producción.

**Herramientas Utilizadas:**

Para soportar el proceso SCRUM, se utilizaron herramientas colaborativas que permitieron tracking del trabajo, comunicación del equipo, y gestión de incidencias. El sistema versionó todo el código fuente en un repositorio centralizado, permitiendo que múltiples desarrolladores trabajaran en paralelo con control de cambios y trazabilidad completa.

**Resultado Final:**

La aplicación disciplinada de SCRUM durante todo el ciclo de desarrollo permitió que Juno Express fuera desarrollado dentro de los plazos establecidos, cumpliendo con todos los requisitos funcionales identificados inicialmente, manteniendo una arquitectura escalable y mantenible, y asegurando que el producto final resolviera efectivamente los problemas operacionales de la empresa. El sistema resultante es robusto, funcional y listo para su despliegue en producción, habiendo sido validado continuamente con usuarios finales a lo largo de todo el proceso de desarrollo.

## 6.2.7. Análisis de Requerimientos

### Requerimientos Funcionales

El proceso de levantamiento de requerimientos se realizó mediante entrevistas con el personal de Juno Express S.A., análisis de sus procesos operacionales actuales, observación directa de sus flujos de trabajo, y revisión de documentación administrativa existente. A continuación se presentan los requerimientos funcionales identificados y desarrollados en el sistema:

| Código | Requerimiento | Descripción |
|--------|---------------|-------------|
| RF01 | Registro de usuarios | Permitir que nuevos pasajeros se registren en el sistema mediante correo electrónico, teléfono y contraseña. |
| RF02 | Autenticación de usuario | Implementar sistema de login seguro con validación de credenciales para pasajeros y administradores. |
| RF03 | Búsqueda de viajes | Permitir búsqueda de viajes disponibles por origen, destino y fecha de salida. |
| RF04 | Filtrado de viajes | Implementar filtros por ruta, rango de precios y horarios disponibles. |
| RF05 | Carrito de boletos | Implementar carrito de compras persistente con gestión de cantidades de boletos. |
| RF06 | Compra de boletos | Permitir completar el proceso de compra con selección de método de pago. |
| RF07 | Registro de ventas | Almacenar información completa de las ventas (cliente, ruta, fecha, monto, método de pago). |
| RF08 | Historial de boletos | Permitir a los pasajeros visualizar su historial completo de boletos comprados. |
| RF09 | Gestión de viajes | Permitir a administradores crear, editar y cancelar viajes especificando ruta, fecha, hora y capacidad. |
| RF10 | Gestión de rutas | Implementar CRUD completo de rutas con origen, destino, precio y duración. |
| RF11 | Control de asientos | Implementar control automático de asientos disponibles con actualización en tiempo real. |
| RF12 | Estados de viaje | Soportar cuatro estados de viaje (programado, en curso, completado, cancelado). |
| RF13 | Dashboard administrativo | Proporcionar dashboard con estadísticas en tiempo real (ingresos, boletos, usuarios, viajes). |
| RF14 | Reportes de ventas | Generar reportes de ingresos por período (diario, semanal, mensual). |
| RF15 | Gráficos de ventas | Visualizar gráficos interactivos de ventas de los últimos 7 días. |
| RF16 | Sistema de consultas | Implementar sistema bidireccional de consultas entre pasajeros y administradores. |
| RF17 | Respuestas de consultas | Permitir a administradores responder consultas de pasajeros y marcarlas como resueltas. |
| RF18 | Seguimiento de consultas | Permitir pasajeros visualizar historial de sus consultas y respuestas recibidas. |
| RF19 | Notificaciones de consultas | Mostrar contador de consultas pendientes en interfaz administrativa. |
| RF20 | Generación de comprobantes | Generar comprobantes digitales (boletas y facturas) en formato PDF. |
| RF21 | Cálculo de IGV | Incluir cálculo automático de IGV (18%) en comprobantes fiscales. |
| RF22 | Gestión de usuarios | Permitir administradores visualizar y filtrar usuarios por rol y datos de contacto. |
| RF23 | Perfil de usuario | Permitir usuarios visualizar y actualizar su perfil personal y cambiar contraseña. |
| RF24 | Métodos de pago | Soportar múltiples métodos de pago (tarjeta, efectivo, transferencia, billeteras digitales). |

### Requerimientos No Funcionales

| Código | Requerimiento | Descripción |
|--------|---------------|-------------|
| RNF01 | Seguridad | Implementar autenticación segura con Firebase Authentication y reglas de seguridad en Firestore. |
| RNF02 | Encriptación | Encriptar contraseñas de usuarios con algoritmos seguros (werkzeug.security). |
| RNF03 | Disponibilidad | El sistema debe estar disponible 24/7 con tiempo de inactividad mínimo. |
| RNF04 | Tiempo de respuesta | El tiempo de carga de páginas no debe exceder 3 segundos en condiciones normales. |
| RNF05 | Escalabilidad | El sistema debe soportar crecimiento en número de usuarios, viajes y transacciones. |
| RNF06 | Usabilidad | Interfaz intuitiva y amigable para usuarios no técnicos de ambos roles. |
| RNF07 | Mantenibilidad | Código modular, documentado y bien estructurado para facilitar mantenimiento futuro. |
| RNF08 | Compatibilidad | Compatible con navegadores modernos (Chrome, Firefox, Safari, Edge). |
| RNF09 | Responsividad | Interfaz adaptativa y responsive para dispositivos móviles, tablets y desktop. |
| RNF10 | Rendimiento | Capacidad de manejar múltiples usuarios concurrentes sin degradación significativa. |
| RNF11 | Respaldo de datos | Implementar mecanismos de respaldo automático de datos mediante Firestore. |
| RNF12 | Integridad transaccional | Garantizar integridad de transacciones en ventas mediante transacciones atómicas en Firestore. |
| RNF13 | Sincronización en tiempo real | Actualización instantánea de disponibilidad de asientos y estadísticas. |
| RNF14 | Cumplimiento normativo | Cumplir con normativa peruana para libro de reclamaciones y facturación electrónica. |

### Requerimientos Técnicos

| Elemento | Tecnología | Justificación |
|----------|-----------|--------------|
| Framework Web | Flask 2.3.3 | Framework web Python ligero y flexible, ideal para aplicaciones CRUD con lógica compleja. |
| Lenguaje Backend | Python 3.x | Lenguaje versátil con excelentes librerías para acceso a bases de datos y generación de reportes. |
| Frontend | HTML5, CSS3, JavaScript | Tecnologías estándar web para interfaz responsiva y moderna. |
| Framework CSS | Bootstrap 5 | Framework de utilidades CSS para desarrollo rápido de interfaces responsivas. |
| Base de Datos Principal | Firebase Firestore | Base de datos NoSQL en tiempo real, escalable, sin servidor, con sincronización automática. |
| Autenticación | Firebase Authentication | Sistema de autenticación seguro con soporte para email/password integrado con Firestore. |
| Seguridad | Werkzeug Security | Biblioteca de seguridad para encriptación de contraseñas con algoritmos robustos. |
| Generación de PDF | ReportLab 4.0+ | Biblioteca Python para generación de comprobantes fiscales y reportes en formato PDF. |
| Gráficos Interactivos | Chart.js | Biblioteca JavaScript para visualización de datos con gráficos dinámicos e interactivos. |
| Iconos | Font Awesome 6 | Librería de iconos moderna y completa para interfaz visual mejorada. |
| Solicitudes HTTP | Requests 2.31+ | Biblioteca Python para realizar solicitudes HTTP hacia APIs externas. |
| Variables de Entorno | python-dotenv 1.0+ | Gestión segura de variables de entorno y credenciales sensibles. |
| Servidor de Aplicación | Gunicorn 21.2+ | Servidor WSGI para despliegue de la aplicación Flask en producción. |
| Control de Versiones | Git | Sistema de control de versiones para gestión del código fuente. |
| Metodología | SCRUM | Metodología ágil para desarrollo iterativo, entregas incrementales y adaptabilidad a cambios. |

---

---
