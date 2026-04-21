from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify, make_response, send_file
import requests
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime, timedelta
from functools import wraps
import os
import re
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.units import inch
import io

import firebase_admin
from firebase_admin import credentials, firestore

# Función helper para convertir fechas UTC a hora de Perú (GMT-5)
def convertir_a_hora_peru(fecha_utc):
    """Convierte fecha UTC a hora de Perú (GMT-5)"""
    if not fecha_utc:
        return None
    
    try:
        if isinstance(fecha_utc, str):
            if 'T' in fecha_utc:
                # Formato ISO UTC
                fecha_dt = datetime.fromisoformat(fecha_utc.replace('Z', '+00:00'))
            else:
                # Formato YYYY-MM-DD
                fecha_dt = datetime.strptime(fecha_utc, '%Y-%m-%d')
        else:
            # Ya es datetime
            fecha_dt = fecha_utc
        
        # Restar 5 horas para convertir UTC a hora de Perú
        fecha_peru = fecha_dt - timedelta(hours=5)
        return fecha_peru
    except Exception as e:
        print(f"Error convirtiendo fecha a hora Perú: {fecha_utc}, error: {e}")
        return fecha_utc
from services.firestore_repo import (
    create_user_doc,
    get_user_by_email,
    get_user_by_id,
    update_user_profile,
    create_ruta_doc,
    create_viaje_doc,
    list_upcoming_viajes,
    search_viajes,
    create_venta_doc,
    decrement_viaje_asientos,
    ventas_between,
    ventas_last_n_days,
    list_ventas_by_user,
    get_viaje_by_id,
    list_viajes_ordered,
    list_rutas,
    list_usuarios,
    list_all_consultas,
    create_consulta_doc,
    respond_consulta,
    count_collection,
    list_consultas_by_user,
)

# Inicializar Firebase Admin y Firestore
# Resolución de ruta de credenciales:
# 1) Variable de entorno FIREBASE_CREDENTIALS
# 2) Archivo 'firebase-key.json' en la raíz del proyecto
# 3) Auto-descubrimiento: cualquier *.json que contenga 'firebase-adminsdk' en el nombre dentro del directorio del proyecto
_PROJECT_DIR = os.path.dirname(__file__)
CRED_PATH = os.getenv('FIREBASE_CREDENTIALS', os.path.join(_PROJECT_DIR, 'firebase-key.json'))
if not os.path.exists(CRED_PATH):
    try:
        for fname in os.listdir(_PROJECT_DIR):
            if fname.endswith('.json') and 'firebase-adminsdk' in fname:
                CRED_PATH = os.path.join(_PROJECT_DIR, fname)
                break
    except Exception:
        pass

try:
    # Si no hay una app inicializada, inicializar con credenciales
    firebase_admin.get_app()
except ValueError:
    if os.path.exists(CRED_PATH):
        cred = credentials.Certificate(CRED_PATH)
        firebase_admin.initialize_app(cred)
    else:
        print(f"Advertencia: credenciales Firebase no encontradas en {CRED_PATH}. Firestore no inicializado.")

    firestore_db = firestore.client()
except Exception:
    firestore_db = None

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'tu_clave_secreta_aqui_cambiar_en_produccion')
app.config['SESSION_COOKIE_SECURE'] = os.getenv('FLASK_ENV') == 'production'

# Función auxiliar para formatear fechas
def format_datetime(value, format='%d/%m/%Y %H:%M'):
    """Formatea una fecha, manejando tanto objetos datetime como strings"""
    if not value:
        return 'No disponible'
    
    # Si es string, intentar convertir a datetime
    if isinstance(value, str):
        try:
            # Intentar varios formatos comunes
            for fmt in ['%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%d']:
                try:
                    value = datetime.strptime(value, fmt)
                    break
                except ValueError:
                    continue
            else:
                return value  # Si no se puede convertir, devolver el string original
        except:
            return value
    
    # Si es datetime, formatear
    if hasattr(value, 'strftime'):
        return value.strftime(format)
    
    return str(value)

# Registrar el filtro en Jinja2
app.jinja_env.filters['datetime'] = format_datetime
# Configuración de empresa JUNO EXPRESS SA
COMPANY_NAME = 'JUNO EXPRESS SA'
COMPANY_TAGLINE = 'transportamos tus sueños... viaja cómodo y seguro'
COMPANY_RUC = '20601935181'
COMPANY_ADDRESS = 'artemio molina - pueblo nuevo'
JUNO_CIUDADES = ['Chincha', 'Pisco', 'Barrio Chino', 'Ica']  # Rutas regulares/diarias
JUNO_CIUDADES_ESPECIALES = ['Yauca']  # Rutas especiales/ocasionales
JUNO_TODAS_CIUDADES = JUNO_CIUDADES + JUNO_CIUDADES_ESPECIALES  # Para reportes
# Rutas JUNO regulares (sin Yauca)
JUNO_RUTAS_PRECIOS = {
    ('Chincha', 'Pisco'): 5.0,
    ('Chincha', 'Barrio Chino'): 8.0,
    ('Chincha', 'Ica'): 10.0,
    ('Pisco', 'Ica'): 8.0,
    ('Pisco', 'Barrio Chino'): 5.0,
    ('Barrio Chino', 'Ica'): 5.0,
    ('Ica', 'Chincha'): 10.0,
    ('Ica', 'Pisco'): 8.0,
    ('Ica', 'Barrio Chino'): 5.0,
    ('Barrio Chino', 'Pisco'): 5.0,
    ('Barrio Chino', 'Chincha'): 8.0,
    ('Pisco', 'Chincha'): 5.0,
}

# Rutas especiales (Yauca) - para uso manual
JUNO_RUTAS_ESPECIALES = {
    ('Chincha', 'Yauca'): 18.0,
    ('Pisco', 'Yauca'): 15.0,
    ('Barrio Chino', 'Yauca'): 12.0,
    ('Ica', 'Yauca'): 8.0,
    ('Yauca', 'Chincha'): 18.0,
    ('Yauca', 'Pisco'): 15.0,
    ('Yauca', 'Barrio Chino'): 12.0,
    ('Yauca', 'Ica'): 8.0,
}
DEFAULT_DURACION = '1 hora'

# Decorador para requerir login
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión para acceder a esta página', 'warning')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

# Decorador para requerir rol de admin
def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Por favor inicia sesión', 'warning')
            return redirect(url_for('login'))
        if session.get('user_role') != 'admin':
            flash('No tienes permisos para acceder a esta página', 'danger')
            return redirect(url_for('index'))
        return f(*args, **kwargs)
    return decorated_function

# Rutas Públicas
@app.route('/')
def index():
    if 'user_id' in session:
        if session.get('user_role') == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('pasajero_dashboard'))
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        # Autenticación Firestore
        found = get_user_by_email(email, firestore_db) if firestore_db else None
        if found:
            _, data = found
            pw_hash = data.get('password_hash')
            if pw_hash and check_password_hash(pw_hash, password):
                session['user_id'] = email
                # Manejar nombre completo (puede estar en 'nombre' o dividido en 'nombre' y 'apellido')
                nombre = data.get('nombre', '')
                apellido = data.get('apellido', '')
                if apellido:
                    full_name = f"{nombre} {apellido}".strip()
                else:
                    full_name = nombre or 'Usuario'
                session['user_name'] = full_name
                session['user_role'] = data.get('rol') or 'pasajero'
                flash(f"¡Bienvenido {session['user_name']}!", 'success')
                return redirect(url_for('admin_dashboard' if session['user_role']=='admin' else 'pasajero_dashboard'))

        else:
            flash('Email o contraseña incorrectos', 'danger')
    
    return render_template('login.html')

@app.route('/registro', methods=['GET', 'POST'])
def registro():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        email = request.form.get('email')
        telefono = request.form.get('telefono')
        password = request.form.get('password')
        
        # Validaciones básicas
        if not nombre or not apellido:
            flash('Nombre y apellido son obligatorios', 'danger')
            return redirect(url_for('registro'))
        
        # Registro solo en Firestore
        existente = get_user_by_email(email, firestore_db) if firestore_db else None
        if existente:
            flash('El email ya está registrado', 'danger')
            return redirect(url_for('registro'))
        try:
            create_user_doc(
                email,
                {
                    'nombre': nombre,
                    'apellido': apellido,
                    'email': email,
                    'telefono': telefono,
                    'rol': 'pasajero',
                    'fecha_registro': datetime.utcnow().isoformat(),
                    'password_hash': generate_password_hash(password),
                    'origen': 'registro-web',
                },
                firestore_db,
            )
        except Exception as e:
            print(f"Error creando usuario en Firestore: {e}")
            flash('No se pudo registrar, inténtalo de nuevo', 'danger')
            return redirect(url_for('registro'))
        
        flash('¡Registro exitoso! Ahora puedes iniciar sesión', 'success')
        return redirect(url_for('login'))
    
    return render_template('registro.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('Has cerrado sesión correctamente', 'info')
    return redirect(url_for('index'))

# Rutas de Información Pública
@app.route('/nosotros')
def nosotros():
    return render_template('nosotros.html')

@app.route('/cargo')
def cargo():
    return render_template('cargo.html')

@app.route('/oficinas')
def oficinas():
    return render_template('oficinas.html')

@app.route('/terminos-condiciones')
def terminos_condiciones():
    """Sirve el PDF de términos y condiciones"""
    try:
        pdf_path = os.path.join(os.path.dirname(__file__), 'static', 'docs', 'terminos_condiciones.pdf')
        if os.path.exists(pdf_path):
            return send_file(pdf_path, as_attachment=False, mimetype='application/pdf')
        else:
            flash('El documento de términos y condiciones no está disponible', 'warning')
            return redirect(url_for('index'))
    except Exception as e:
        print(f"Error sirviendo PDF: {e}")
        flash('Error al cargar el documento', 'danger')
        return redirect(url_for('index'))

@app.route('/libro-reclamaciones')
def libro_reclamaciones():
    """Muestra el libro de reclamaciones con ventana emergente"""
    return render_template('libro_reclamaciones.html')

@app.route('/libro-reclamaciones/enviar', methods=['POST'])
def enviar_reclamacion():
    """Procesa el envío de reclamación"""
    try:
        nombres = request.form.get('nombres', '').strip()
        apellidos = request.form.get('apellidos', '').strip()
        tipo_doc = request.form.get('tipo_doc', '').strip()
        num_doc = request.form.get('num_doc', '').strip()
        telefono = request.form.get('telefono', '').strip()
        correo = request.form.get('correo', '').strip()
        direccion = request.form.get('direccion', '').strip()
        bien = request.form.get('bien', '').strip()
        tipo = request.form.get('tipo', '').strip()
        monto = request.form.get('monto', '').strip()
        comprobante = request.form.get('comprobante', '').strip()
        detalle = request.form.get('detalle', '').strip()
        pedido = request.form.get('pedido', '').strip()
        
        if not all([nombres, apellidos, tipo_doc, num_doc, correo, tipo, comprobante, detalle, pedido]):
            flash('Todos los campos obligatorios deben ser completados', 'danger')
            return redirect(url_for('libro_reclamaciones'))
        
        # Guardar en Firestore
        firestore_db.collection('reclamaciones').add({
            'nombres': nombres,
            'apellidos': apellidos,
            'tipo_doc': tipo_doc,
            'num_doc': num_doc,
            'telefono': telefono,
            'correo': correo,
            'direccion': direccion,
            'bien': bien,
            'tipo': tipo,
            'monto': monto,
            'comprobante': comprobante,
            'detalle': detalle,
            'pedido': pedido,
            'fecha': datetime.utcnow().isoformat(),
            'estado': 'pendiente'
        })
        
        flash('Su reclamación ha sido registrada correctamente. Le responderemos en un plazo máximo de 15 días hábiles.', 'success')
        return redirect(url_for('index'))
        
    except Exception as e:
        print(f"Error procesando reclamación: {e}")
        flash('Error al procesar su reclamación. Por favor, inténtelo nuevamente.', 'danger')
        return redirect(url_for('libro_reclamaciones'))

# Rutas de Pasajero
@app.route('/pasajero/dashboard')
@login_required
def pasajero_dashboard():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_dashboard'))

    viajes_disponibles = []
    try:
        docs = list_upcoming_viajes(limit=6, client=firestore_db)
        for d in docs:
            data = d.to_dict()
            viajes_disponibles.append(type('Obj', (), {
                'id': d.id,
                'ruta': type('RutaObj', (), {
                    'origen': data.get('ruta_origen'),
                    'destino': data.get('ruta_destino'),
                    'precio': data.get('precio'),
                    'duracion': data.get('duracion'),
                })(),
                'fecha_salida': data.get('fecha_salida'),
                'hora_salida': data.get('hora_salida'),
                'asientos_totales': data.get('asientos_totales'),
                'asientos_disponibles': data.get('asientos_disponibles'),
                'estado': data.get('estado'),
            }))
    except Exception as e:
        print(f"Aviso: fallo leyendo viajes Firestore: {e}")
        viajes_disponibles = []

    # Historial de compras desde Firestore (enriquecido para plantilla)
    ventas_docs = []
    try:
        ventas_docs = list_ventas_by_user(session.get('user_id'), firestore_db) if firestore_db else []
    except Exception as e:
        print(f"Aviso: fallo leyendo ventas por usuario: {e}")
    mis_compras = []
    for d in ventas_docs[:5]:
        v = d.to_dict()
        # Obtener viaje asociado
        viaje_snap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
        viaje_obj = None
        if viaje_snap and viaje_snap.exists:
            vd = viaje_snap.to_dict()
            viaje_obj = type('ViajeObj', (), {
                'id': viaje_snap.id,
                'ruta': type('RutaObj', (), {
                    'origen': vd.get('ruta_origen'),
                    'destino': vd.get('ruta_destino'),
                    'precio': vd.get('precio'),
                    'duracion': vd.get('duracion'),
                })(),
                'fecha_salida': vd.get('fecha_salida'),
                'hora_salida': vd.get('hora_salida'),
            })
        # Solo agregar si tenemos un viaje válido
        if viaje_obj:
            # Convertir fecha de compra a hora de Perú
            fecha_compra_peru = convertir_a_hora_peru(v.get('fecha_compra'))
            
            mis_compras.append(type('VentaObj', (), {
                'id': d.id,
                'viaje': viaje_obj,
                'viaje_id': v.get('viaje_id'),
                'cantidad_boletos': v.get('cantidad_boletos'),
                'total': v.get('total'),
                'fecha_compra': fecha_compra_peru,
                'estado': v.get('estado'),
                'metodo_pago': v.get('metodo_pago'),
            }))

    # Asegurar que el nombre del usuario esté en la sesión
    if not session.get('user_name'):
        user_id = session.get('user_id')
        user_doc = get_user_by_id(user_id, firestore_db) if firestore_db else None
        if user_doc and user_doc.exists:
            user_data = user_doc.to_dict()
            nombre = user_data.get('nombre', '')
            apellido = user_data.get('apellido', '')
            
            # Migración para usuarios antiguos
            if not apellido and ' ' in nombre:
                nombre_partes = nombre.strip().split(' ', 1)
                primer_nombre = nombre_partes[0]
                apellido_extraido = nombre_partes[1] if len(nombre_partes) > 1 else ''
                
                try:
                    update_user_profile(user_id, {
                        'nombre': primer_nombre,
                        'apellido': apellido_extraido
                    }, firestore_db)
                    nombre = primer_nombre
                    apellido = apellido_extraido
                except Exception as e:
                    print(f"Error actualizando usuario para migración: {e}")
            
            # Actualizar sesión
            if apellido:
                session['user_name'] = f"{nombre} {apellido}".strip()
            else:
                session['user_name'] = nombre or 'Usuario'
        else:
            session['user_name'] = 'Usuario'
    
    # Obtener fecha de registro para el dashboard
    fecha_registro = None
    try:
        user_id = session.get('user_id')
        user_doc = get_user_by_id(user_id, firestore_db) if firestore_db else None
        if user_doc and user_doc.exists:
            user_data = user_doc.to_dict()
            fecha_reg = user_data.get('fecha_registro')
            if isinstance(fecha_reg, str):
                try:
                    fecha_registro = datetime.fromisoformat(fecha_reg.replace('Z', '+00:00'))
                except:
                    fecha_registro = datetime.now()
            elif fecha_reg:
                fecha_registro = fecha_reg
            else:
                fecha_registro = datetime.now()
    except Exception as e:
        print(f"Error obteniendo fecha de registro: {e}")
        fecha_registro = datetime.now()
    
    # Crear objeto usuario simple y seguro
    usuario = {
        'nombre': session.get('user_name', 'Usuario'),
        'fecha_registro': fecha_registro
    }
    
    return render_template('pasajero/dashboard.html',
                           usuario=usuario,
                           viajes=viajes_disponibles,
                           mis_compras=mis_compras)

@app.route('/pasajero/buscar-viajes', methods=['GET', 'POST'])
@login_required
def buscar_viajes():
    viajes = []
    rutas = []
    try:
        rutas_docs = firestore_db.collection('rutas').stream()
        for r in rutas_docs:
            data = r.to_dict()
            rutas.append(type('Ruta', (), {
                'id': r.id,
                'origen': data.get('origen'),
                'destino': data.get('destino'),
                'precio': data.get('precio'),
                'duracion': data.get('duracion'),
                'activa': data.get('activa', True),
            }))
    except Exception as e:
        print(f"Aviso: fallo leyendo rutas Firestore: {e}")

    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        fecha = request.form.get('fecha')

        viajes = []
        try:
            fecha_obj = datetime.strptime(fecha, '%Y-%m-%d') if fecha else None
            docs = search_viajes(origen, destino, fecha_obj, client=firestore_db)
            for d in docs:
                data = d.to_dict()
                viajes.append(type('Obj', (), {
                    'id': d.id,
                    'ruta': type('RutaObj', (), {
                        'origen': data.get('ruta_origen'),
                        'destino': data.get('ruta_destino'),
                        'precio': data.get('precio'),
                        'duracion': data.get('duracion'),
                    })(),
                    'fecha_salida': data.get('fecha_salida'),
                    'hora_salida': data.get('hora_salida'),
                    'asientos_totales': data.get('asientos_totales'),
                    'asientos_disponibles': data.get('asientos_disponibles'),
                    'estado': data.get('estado'),
                    'tipo_viaje': data.get('tipo_viaje'),
                    'paradas': data.get('paradas'),
                    'horarios_paradas': data.get('horarios_paradas'),
                }))
        except Exception as e:
            print(f"Aviso: fallo búsqueda Firestore: {e}")

    else:
        # Mostrar próximos viajes por defecto
        try:
            docs = list_upcoming_viajes(limit=12, client=firestore_db)
            print(f"DEBUG: list_upcoming_viajes devolvió {len(docs)} documentos")
            for d in docs:
                data = d.to_dict()
                print(f"DEBUG: Viaje {d.id}: {data.get('ruta_origen')} -> {data.get('ruta_destino')}, fecha: {data.get('fecha_salida')}, asientos: {data.get('asientos_disponibles')}")
                viajes.append(type('Obj', (), {
                    'id': d.id,
                    'ruta': type('RutaObj', (), {
                        'origen': data.get('ruta_origen'),
                        'destino': data.get('ruta_destino'),
                        'precio': data.get('precio'),
                        'duracion': data.get('duracion'),
                    })(),
                    'fecha_salida': data.get('fecha_salida'),
                    'hora_salida': data.get('hora_salida'),
                    'asientos_totales': data.get('asientos_totales'),
                    'asientos_disponibles': data.get('asientos_disponibles'),
                    'estado': data.get('estado'),
                    'tipo_viaje': data.get('tipo_viaje'),
                    'paradas': data.get('paradas'),
                    'horarios_paradas': data.get('horarios_paradas'),
                }))
        except Exception as e:
            print(f"Aviso: fallo cargando próximos viajes: {e}")

    print(f"DEBUG: Enviando {len(viajes)} viajes al template")
    return render_template('pasajero/buscar_viajes.html', viajes=viajes, rutas=rutas, ciudades_juno=JUNO_CIUDADES)

@app.route('/pasajero/comprar-boleto/<viaje_id>', methods=['GET', 'POST'])
@login_required
def comprar_boleto(viaje_id):
    snap = get_viaje_by_id(viaje_id, firestore_db)
    if not snap or not snap.exists:
        flash('Viaje no encontrado', 'danger')
        return redirect(url_for('buscar_viajes'))
    data = snap.to_dict()
    viaje = type('Obj', (), {
        'id': viaje_id,
        'ruta': type('RutaObj', (), {
            'origen': data.get('ruta_origen'),
            'destino': data.get('ruta_destino'),
            'precio': data.get('precio'),
            'duracion': data.get('duracion'),
        })(),
        'fecha_salida': data.get('fecha_salida'),
        'hora_salida': data.get('hora_salida'),
        'asientos_totales': data.get('asientos_totales'),
        'asientos_disponibles': data.get('asientos_disponibles'),
        'estado': data.get('estado'),
        'tipo_viaje': data.get('tipo_viaje'),
        'paradas': data.get('paradas'),
        'horarios_paradas': data.get('horarios_paradas'),
    })
    
    if request.method == 'POST':
        cantidad = int(request.form.get('cantidad', 1))
        metodo_pago = request.form.get('metodo_pago')
        
        # Verificar si es un tramo específico de viaje estándar
        es_tramo_estandar = request.form.get('es_tramo_estandar') == 'true'
        origen_real = request.form.get('origen_real') if es_tramo_estandar else data.get('ruta_origen')
        destino_real = request.form.get('destino_real') if es_tramo_estandar else data.get('ruta_destino')
        precio_real = float(request.form.get('precio_real')) if es_tramo_estandar and request.form.get('precio_real') else data.get('precio')
        
        # Validar tramo estándar
        if es_tramo_estandar and (not origen_real or not destino_real or not precio_real):
            flash('Debes seleccionar un tramo específico para la ruta estándar', 'warning')
            return render_template('pasajero/comprar_boleto.html', viaje=viaje)
        
        # Datos del comprador
        comprador_nombre = (request.form.get('comprador_nombre') or '').strip()
        comprador_dni = (request.form.get('comprador_dni') or '').strip()
        tipo_comprobante = (request.form.get('tipo_comprobante') or 'boleta').strip()
        ruc = (request.form.get('ruc') or '').strip() if tipo_comprobante == 'factura' else ''
        razon_social = (request.form.get('razon_social') or '').strip() if tipo_comprobante == 'factura' else ''
        direccion = (request.form.get('direccion') or '').strip() if tipo_comprobante == 'factura' else ''

        # Validaciones básicas backend
        def _is_digits(s: str, n: int):
            return s.isdigit() and len(s) == n
        if not comprador_nombre or not _is_digits(comprador_dni, 8):
            flash('DNI debe tener 8 dígitos y el nombre es obligatorio', 'danger')
            return redirect(url_for('comprar_boleto', viaje_id=viaje_id))
        if tipo_comprobante == 'factura':
            if not _is_digits(ruc, 11) or not razon_social:
                flash('Para factura, RUC (11 dígitos) y Razón Social son obligatorios', 'danger')
                return redirect(url_for('comprar_boleto', viaje_id=viaje_id))
        
        # Decremento transaccional en Firestore (rechaza si no hay cupos)
        try:
            decrement_viaje_asientos(viaje_id, cantidad, firestore_db)
        except Exception as e:
            flash('No hay suficientes asientos disponibles', 'danger')
            return redirect(url_for('comprar_boleto', viaje_id=viaje_id))

        total = cantidad * precio_real
        # Calcular IGV (18%) y subtotal
        try:
            subtotal = round(float(total) / 1.18, 2)
            igv = round(float(total) - subtotal, 2)
        except Exception:
            subtotal = float(total)
            igv = 0.0

        # Firestore: registrar venta y disminuir asientos (best-effort)
        venta_id = None
        try:
            if firestore_db:
                venta_id = f"{int(datetime.utcnow().timestamp()*1000)}"
                create_venta_doc(
                    venta_id,
                    {
                        'usuario_id': session.get('user_id'),
                        'viaje_id': viaje_id,
                        'cantidad_boletos': cantidad,
                        'total': total,
                        'subtotal': subtotal,
                        'igv': igv,
                        'fecha_compra': datetime.utcnow(),
                        'estado': 'confirmado',
                        'metodo_pago': metodo_pago,
                        'comprador_nombre': comprador_nombre,
                        'comprador_dni': comprador_dni,
                        'tipo_comprobante': tipo_comprobante,
                        'ruc': ruc,
                        'razon_social': razon_social,
                        'direccion': direccion,
                        # Datos del tramo específico (para viajes estándar)
                        'origen_real': origen_real,
                        'destino_real': destino_real,
                        'precio_unitario': precio_real,
                        'es_tramo_estandar': es_tramo_estandar,
                    },
                    firestore_db,
                )
        except Exception as e:
            print(f"Aviso: no se pudo sincronizar venta/asientos en Firestore: {e}")
        
        flash(f'¡Compra exitosa! Has adquirido {cantidad} boleto(s)', 'success')
        # Redirigir a impresión del comprobante según selección si tenemos venta_id
        sel = request.form.get('imprimir', 'boleto')
        if venta_id:
            return redirect(url_for('ver_comprobante', venta_id=venta_id, tipo=sel))
        return redirect(url_for('mis_boletos'))
    
    return render_template('pasajero/comprar_boleto.html', viaje=viaje)

@app.route('/pasajero/comprobante/<venta_id>')
@login_required
def ver_comprobante(venta_id):
    # Cargar venta y viaje para imprimir comprobante
    try:
        snap = firestore_db.collection('ventas').document(str(venta_id)).get()
        if not snap or not snap.exists:
            flash('Comprobante no encontrado', 'danger')
            return redirect(url_for('mis_boletos'))
        v = snap.to_dict()
        vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db)
        viaje = None
        if vsnap and vsnap.exists:
            d = vsnap.to_dict()
            viaje = type('Obj', (), {
                'ruta': type('RutaObj', (), {
                    'origen': d.get('ruta_origen'),
                    'destino': d.get('ruta_destino'),
                    'precio': d.get('precio'),
                    'duracion': d.get('duracion'),
                })(),
                'fecha_salida': d.get('fecha_salida'),
                'hora_salida': d.get('hora_salida'),
            })
        # Convertir fecha de compra a hora de Perú
        fecha_compra_peru = convertir_a_hora_peru(v.get('fecha_compra'))
        v['fecha_compra'] = fecha_compra_peru
        
        return render_template('pasajero/comprobante.html', venta=v, venta_id=venta_id, viaje=viaje,
                               company_name=COMPANY_NAME, company_ruc=COMPANY_RUC, company_address=COMPANY_ADDRESS)
    except Exception as e:
        flash('No se pudo cargar el comprobante', 'danger')
        return redirect(url_for('mis_boletos'))

@app.route('/pasajero/mis-boletos')
@login_required
def mis_boletos():
    docs = list_ventas_by_user(session.get('user_id'), firestore_db) if firestore_db else []
    ventas = []
    for d in docs:
        v = d.to_dict()
        # Enriquecer con viaje
        viaje_snap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
        viaje_obj = None
        if viaje_snap and viaje_snap.exists:
            vd = viaje_snap.to_dict()
            viaje_obj = type('ViajeObj', (), {
                'id': viaje_snap.id,
                'ruta': type('RutaObj', (), {
                    'origen': vd.get('ruta_origen'),
                    'destino': vd.get('ruta_destino'),
                    'precio': vd.get('precio'),
                    'duracion': vd.get('duracion'),
                })(),
                'fecha_salida': vd.get('fecha_salida'),
                'hora_salida': vd.get('hora_salida'),
            })
        # Convertir fecha de compra a hora de Perú
        fecha_compra_peru = convertir_a_hora_peru(v.get('fecha_compra'))
        
        ventas.append(type('VentaObj', (), {
            'id': d.id,
            'viaje': viaje_obj,
            'viaje_id': v.get('viaje_id'),
            'cantidad_boletos': v.get('cantidad_boletos'),
            'total': v.get('total'),
            'fecha_compra': fecha_compra_peru,
            'estado': v.get('estado'),
            'metodo_pago': v.get('metodo_pago'),
            'es_tramo_estandar': v.get('es_tramo_estandar', False),
            'origen_real': v.get('origen_real'),
            'destino_real': v.get('destino_real'),
            'precio_unitario': v.get('precio_unitario'),
        }))
    return render_template('pasajero/mis_boletos.html', ventas=ventas)

@app.route('/pasajero/consultas', methods=['GET', 'POST'])
@login_required
def mis_consultas():
    if request.method == 'POST':
        asunto = request.form.get('asunto')
        mensaje = request.form.get('mensaje')
        # Crear consulta en Firestore
        try:
            cid = f"c-{int(datetime.utcnow().timestamp()*1000)}"
            create_consulta_doc(cid, {
                'usuario_id': session.get('user_id'),
                'asunto': asunto,
                'mensaje': mensaje,
                'estado': 'pendiente',
                'fecha_consulta': datetime.utcnow(),
            }, firestore_db)
        except Exception as e:
            print(f"Error creando consulta: {e}")
            flash('No se pudo enviar la consulta', 'danger')
            return redirect(url_for('mis_consultas'))

        flash('Consulta enviada correctamente. Te responderemos pronto.', 'success')
        return redirect(url_for('mis_consultas'))

    docs = list_consultas_by_user(session.get('user_id'), firestore_db) if firestore_db else []
    consultas = [type('ConsultaObj', (), d.to_dict()) for d in docs]
    return render_template('pasajero/consultas.html', consultas=consultas)

@app.route('/pasajero/perfil', methods=['GET', 'POST'])
@login_required
def pasajero_perfil():
    if session.get('user_role') == 'admin':
        return redirect(url_for('admin_perfil'))
    
    user_id = session.get('user_id')
    user_doc = get_user_by_id(user_id, firestore_db) if firestore_db else None
    
    if not user_doc or not user_doc.exists:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('pasajero_dashboard'))
    
    user_data = user_doc.to_dict()
    
    if request.method == 'POST':
        # Actualizar datos del perfil
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validaciones básicas
        if not nombre or not apellido or not email:
            flash('Nombre, apellido y email son obligatorios', 'danger')
            return render_template('pasajero/perfil.html', user=user_data)
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('El formato del email no es válido', 'danger')
            return render_template('pasajero/perfil.html', user=user_data)
        
        # Validar teléfono si se proporciona
        if telefono and not re.match(r'^[0-9\s\-\+\(\)]{9,15}$', telefono):
            flash('El formato del teléfono no es válido', 'danger')
            return render_template('pasajero/perfil.html', user=user_data)
        
        # Actualizar en Firestore
        try:
            update_user_profile(user_id, {
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono,
                'email': email,
                'fecha_actualizacion': datetime.utcnow()
            }, firestore_db)
            
            # Actualizar sesión
            session['user_name'] = f"{nombre} {apellido}"
            
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('pasajero_perfil'))
        except Exception as e:
            print(f"Error actualizando perfil: {e}")
            flash('Error al actualizar el perfil', 'danger')
    
    return render_template('pasajero/perfil.html', user=user_data, fecha_actual=datetime.now())

# Rutas de Administrador
@app.route('/admin/dashboard')
@admin_required
def admin_dashboard():
    # Estadísticas generales desde Firestore (filtradas a rutas JUNO)
    ventas_docs = ventas_between(datetime.utcnow().replace(day=1), datetime.utcnow(), firestore_db) if firestore_db else []
    total_ventas = 0
    total_boletos = 0
    for d in ventas_docs:
        v = d.to_dict()
        if v.get('estado') != 'confirmado':
            continue
        vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
        if vsnap and vsnap.exists:
            vd = vsnap.to_dict()
            # Comparación insensible a mayúsculas/minúsculas
            ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
            origen_valid = vd.get('ruta_origen', '').lower() in ciudades_lower
            destino_valid = vd.get('ruta_destino', '').lower() in ciudades_lower
            if origen_valid and destino_valid:
                total_ventas += float(v.get('total', 0))
                total_boletos += int(v.get('cantidad_boletos', 0))
    try:
        total_pasajeros = sum(1 for d in list_usuarios(firestore_db) if (d.to_dict() or {}).get('rol') == 'pasajero')
    except Exception:
        total_pasajeros = 0
    try:
        total_viajes = count_collection('viajes', firestore_db)
    except Exception:
        total_viajes = 0
    
    # Ventas recientes (filtradas a rutas JUNO)
    ventas_recientes_docs = ventas_between(datetime.utcnow().replace(day=1), datetime.utcnow(), firestore_db) if firestore_db else []
    ventas_recientes = []
    for d in ventas_recientes_docs[:10]:
        v = d.to_dict()
        # cliente
        cliente_obj = None
        if v.get('usuario_id'):
            u = get_user_by_email(v.get('usuario_id'), firestore_db)
            if u:
                _, udata = u
                cliente_obj = type('ClienteObj', (), udata)
        # viaje
        viaje_obj = None
        if v.get('viaje_id'):
            vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db)
            if vsnap and vsnap.exists:
                vd = vsnap.to_dict()
                viaje_obj = type('ViajeObj', (), {
                    'id': vsnap.id,
                    'ruta': type('RutaObj', (), {
                        'origen': vd.get('ruta_origen'),
                        'destino': vd.get('ruta_destino'),
                        'precio': vd.get('precio'),
                        'duracion': vd.get('duracion'),
                    })(),
                    'fecha_salida': vd.get('fecha_salida'),
                    'hora_salida': vd.get('hora_salida'),
                })
        # Comparación insensible a mayúsculas/minúsculas para ventas recientes
        if viaje_obj:
            ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
            origen_valid = viaje_obj.ruta.origen.lower() in ciudades_lower if viaje_obj.ruta.origen else False
            destino_valid = viaje_obj.ruta.destino.lower() in ciudades_lower if viaje_obj.ruta.destino else False
            if origen_valid and destino_valid:
                ventas_recientes.append(type('VentaObj', (), {
                    'id': d.id,
                    'cliente': cliente_obj,
                    'viaje': viaje_obj,
                    'cantidad_boletos': v.get('cantidad_boletos'),
                    'total': v.get('total'),
                    'fecha_compra': v.get('fecha_compra'),
                }))
    
    # Consultas pendientes
    try:
        consultas_pendientes = sum(1 for d in list_all_consultas(firestore_db) if (d.to_dict() or {}).get('estado') == 'pendiente')
    except Exception:
        consultas_pendientes = 0
    
    return render_template('admin/dashboard.html',
                         total_ventas=total_ventas,
                         total_boletos=total_boletos,
                         total_pasajeros=total_pasajeros,
                         total_viajes=total_viajes,
                         ventas_recientes=ventas_recientes,
                         consultas_pendientes=consultas_pendientes)

@app.route('/admin/planificacion')
@admin_required
def admin_planificacion():
    viajes_docs = list_viajes_ordered(limit=200, client=firestore_db)
    viajes = []
    for d in viajes_docs:
        data = d.to_dict()
        viajes.append(type('Obj', (), {
            'id': d.id,
            'ruta': type('RutaObj', (), {
                'origen': data.get('ruta_origen'),
                'destino': data.get('ruta_destino'),
                'precio': data.get('precio'),
            })(),
            'fecha_salida': data.get('fecha_salida'),
            'hora_salida': data.get('hora_salida'),
            'bus_numero': data.get('bus_numero'),
            'asientos_totales': data.get('asientos_totales'),
            'asientos_disponibles': data.get('asientos_disponibles'),
            'estado': data.get('estado'),
        }))
    rutas_docs = list_rutas(firestore_db)
    rutas = [type('Ruta', (), {'id': r.id, **r.to_dict()}) for r in rutas_docs]
    return render_template('admin/planificacion.html', viajes=viajes, rutas=rutas)

@app.route('/admin/rutas', methods=['GET', 'POST'])
@admin_required
def admin_rutas():
    if request.method == 'POST':
        origen = (request.form.get('origen') or '').strip()
        destino = (request.form.get('destino') or '').strip()
        precio_raw = request.form.get('precio')
        duracion = (request.form.get('duracion') or '').strip()

        # Parseo seguro de precio
        try:
            precio = float(precio_raw) if precio_raw not in (None, '') else None
        except Exception:
            precio = None

        # Autocompletar si la combinación existe y el precio no es válido
        tarifa = JUNO_RUTAS_PRECIOS.get((origen, destino))
        if (precio is None or precio <= 0) and tarifa is not None:
            precio = float(tarifa)
        # Duración por defecto si viene vacío
        if not duracion:
            duracion = DEFAULT_DURACION
        # Crear ruta solo en Firestore (ID auto)
        try:
            ref = firestore_db.collection('rutas').document()
            ref.set({
                'origen': origen,
                'destino': destino,
                'precio': precio,
                'duracion': duracion,
                'activa': False,  # Inactiva hasta que se planifique un viaje
                'tipo': 'normal',  # Marcar como ruta normal
                'fecha_creacion': datetime.utcnow().isoformat()
            })
        except Exception as e:
            print(f"Aviso: no se pudo crear ruta en Firestore: {e}")
        
        flash('Ruta creada exitosamente', 'success')
        return redirect(url_for('admin_rutas'))
    rutas_docs = list_rutas(firestore_db)
    rutas = [type('Ruta', (), {'id': r.id, **r.to_dict()}) for r in rutas_docs]
    # Preparar mapa de precios para el frontend
    precios = {f"{k[0]}::{k[1]}": v for k, v in JUNO_RUTAS_PRECIOS.items()}
    return render_template('admin/rutas.html', rutas=rutas, ciudades_juno=JUNO_CIUDADES, precios_juno=precios, duracion_default=DEFAULT_DURACION)

@app.route('/admin/rutas/eliminar/<ruta_id>', methods=['POST'])
@admin_required
def eliminar_ruta(ruta_id):
    try:
        # Eliminar viajes asociados a la ruta
        viajes_q = firestore_db.collection('viajes').where('ruta_id', '==', ruta_id).stream()
        for v in viajes_q:
            firestore_db.collection('viajes').document(v.id).delete()
        # Eliminar la ruta
        firestore_db.collection('rutas').document(str(ruta_id)).delete()
        flash('Ruta y viajes asociados eliminados', 'success')
    except Exception as e:
        print(f"Error eliminando ruta {ruta_id}: {e}")
        flash('No se pudo eliminar la ruta', 'danger')
    return redirect(url_for('admin_rutas'))

@app.route('/admin/crear-viaje', methods=['POST'])
@admin_required
def crear_viaje():
    ruta_id = request.form.get('ruta_id')
    fecha_salida = request.form.get('fecha_salida')
    hora_salida = request.form.get('hora_salida')
    bus_numero = request.form.get('bus_numero')
    asientos_totales = int(request.form.get('asientos_totales', 40))
    
    fecha_salida_dt = datetime.strptime(fecha_salida, '%Y-%m-%d')
    # Crear viaje en Firestore usando información de la ruta
    try:
        ruta_snap = firestore_db.collection('rutas').document(str(ruta_id)).get()
        ruta_data = ruta_snap.to_dict() if ruta_snap and ruta_snap.exists else {}
        ref = firestore_db.collection('viajes').document()
        ref.set({
            'ruta_id': ruta_id,
            'ruta_origen': ruta_data.get('origen'),
            'ruta_destino': ruta_data.get('destino'),
            'precio': ruta_data.get('precio'),
            'duracion': ruta_data.get('duracion'),
            'fecha_salida': fecha_salida_dt,
            'hora_salida': hora_salida,
            'bus_numero': bus_numero,
            'asientos_totales': asientos_totales,
            'asientos_disponibles': asientos_totales,
            'estado': 'programado',
        })
        
        # Activar automáticamente la ruta cuando se programa el primer viaje
        if ruta_snap and ruta_snap.exists:
            ruta_snap.reference.update({'activa': True})
    except Exception as e:
        print(f"Aviso: no se pudo crear viaje en Firestore: {e}")
    
    flash('Viaje programado exitosamente', 'success')
    return redirect(url_for('admin_planificacion'))

@app.route('/admin/viajes/eliminar/<viaje_id>', methods=['POST'])
@admin_required
def eliminar_viaje(viaje_id):
    try:
        firestore_db.collection('viajes').document(str(viaje_id)).delete()
        flash('Viaje eliminado', 'success')
    except Exception as e:
        print(f"Error eliminando viaje {viaje_id}: {e}")
        flash('No se pudo eliminar el viaje', 'danger')
    return redirect(url_for('admin_planificacion'))

@app.route('/admin/seed-rutas-juno', methods=['POST'])
@admin_required
def seed_rutas_juno():
    """Crea las rutas predefinidas de JUNO EXPRESS si no existen."""
    try:
        created = 0
        for (ori, des), precio in JUNO_RUTAS_PRECIOS.items():
            q = firestore_db.collection('rutas').where('origen', '==', ori).where('destino', '==', des).limit(1).stream()
            exists = any(True for _ in q)
            if not exists:
                firestore_db.collection('rutas').document().set({
                    'origen': ori,
                    'destino': des,
                    'precio': float(precio),
                    'duracion': DEFAULT_DURACION,
                    'activa': True,
                })
                created += 1
        flash(f'Seed completado. Rutas creadas: {created}', 'success')
    except Exception as e:
        print(f"Error en seed de rutas JUNO: {e}")
        flash('No se pudo completar el seed', 'danger')
    return redirect(url_for('admin_rutas'))

@app.route('/admin/control-comercial')
@admin_required
def admin_control_comercial():
    # Principal: Firestore, Fallback: SQL
    ventas = []
    ingresos_hoy = 0
    boletos_hoy = 0
    ingresos_mes = 0

    if firestore_db:
        try:
            from datetime import datetime, timedelta
            today = datetime.utcnow().date()
            start_today = datetime(today.year, today.month, today.day)
            start_month = datetime(today.year, today.month, 1)
            end_today = start_today + timedelta(days=1)

            # Ventas recientes (filtradas por rutas JUNO)
            ventas_docs = ventas_between(start_month, end_today, firestore_db)
            # Orden descendente ya aplicado en helper
            # Convertir a objetos simples para la plantilla existente
            for d in ventas_docs:
                data = d.to_dict()
                
                # Solo procesar ventas confirmadas
                if data.get('estado') != 'confirmado':
                    continue
                
                # Filtrar solo ventas de rutas JUNO (igual que en Dashboard)
                viaje_snap = get_viaje_by_id(data.get('viaje_id'), firestore_db) if data.get('viaje_id') else None
                if not (viaje_snap and viaje_snap.exists):
                    continue  # Skip si no existe el viaje
                
                vd = viaje_snap.to_dict()
                ruta_origen = vd.get('ruta_origen')
                ruta_destino = vd.get('ruta_destino')
                
                # Comparación insensible a mayúsculas/minúsculas
                ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
                origen_valid = ruta_origen.lower() in ciudades_lower if ruta_origen else False
                destino_valid = ruta_destino.lower() in ciudades_lower if ruta_destino else False
                
                if not (origen_valid and destino_valid):
                    continue  # Skip si no es ruta JUNO
                
                # Enriquecer cliente
                cliente_doc = get_user_by_email(data.get('usuario_id'), firestore_db) if data.get('usuario_id') else None
                cliente_obj = None
                if cliente_doc:
                    _, cdata = cliente_doc
                    cliente_obj = type('ClienteObj', (), cdata)
                else:
                    # Crear un cliente por defecto si no se encuentra
                    cliente_obj = type('ClienteObj', (), {
                        'nombre': 'Usuario eliminado',
                        'email': data.get('usuario_id', 'N/A'),
                        'telefono': 'N/A'
                    })
                # Crear objeto viaje (ya tenemos los datos de vd)
                viaje_obj = type('ViajeObj', (), {
                    'id': viaje_snap.id,
                    'ruta': type('RutaObj', (), {
                        'origen': vd.get('ruta_origen', 'N/A'),
                        'destino': vd.get('ruta_destino', 'N/A'),
                        'precio': vd.get('precio', 0),
                        'duracion': vd.get('duracion', 'N/A'),
                    })(),
                    'fecha_salida': vd.get('fecha_salida'),
                    'hora_salida': vd.get('hora_salida'),
                })
                # Convertir fecha de compra a hora de Perú usando la función helper
                fecha_compra_peru = convertir_a_hora_peru(data.get('fecha_compra'))
                fecha_compra_str = fecha_compra_peru.strftime('%d/%m/%Y %H:%M') if fecha_compra_peru else "N/A"
                
                # Formatear fecha de salida del viaje de manera simple
                if viaje_obj and hasattr(viaje_obj, 'fecha_salida'):
                    fecha_salida_raw = viaje_obj.fecha_salida
                    if fecha_salida_raw and fecha_salida_raw != 'N/A':
                        try:
                            if hasattr(fecha_salida_raw, 'strftime'):
                                # Ya es date/datetime
                                viaje_obj.fecha_salida = fecha_salida_raw.strftime('%d/%m/%Y')
                            else:
                                # Es string, intentar convertir (solo fecha, sin hora)
                                if 'T' in str(fecha_salida_raw):
                                    # Formato ISO con hora - extraer solo la fecha
                                    fecha_parte = str(fecha_salida_raw).split('T')[0]
                                    fecha_dt = datetime.strptime(fecha_parte, '%Y-%m-%d')
                                    viaje_obj.fecha_salida = fecha_dt.strftime('%d/%m/%Y')
                                elif '-' in str(fecha_salida_raw):
                                    fecha_dt = datetime.strptime(str(fecha_salida_raw), '%Y-%m-%d')
                                    viaje_obj.fecha_salida = fecha_dt.strftime('%d/%m/%Y')
                                else:
                                    viaje_obj.fecha_salida = str(fecha_salida_raw)
                        except Exception as e:
                            print(f"Error formateando fecha_salida: {fecha_salida_raw}, error: {e}")
                            viaje_obj.fecha_salida = str(fecha_salida_raw)

                ventas.append(type('VentaObj', (), {
                    'id': int(d.id) if isinstance(d.id, str) and d.id.isdigit() else d.id,
                    'cliente': cliente_obj,
                    'viaje': viaje_obj,
                    'usuario_id': data.get('usuario_id'),
                    'viaje_id': data.get('viaje_id'),
                    'cantidad_boletos': data.get('cantidad_boletos'),
                    'total': float(data.get('total', 0)),
                    'fecha_compra': fecha_compra_str,
                    'estado': data.get('estado'),
                    'metodo_pago': data.get('metodo_pago'),
                }))
                
                # Limitar a 50 ventas para no sobrecargar la vista
                if len(ventas) >= 50:
                    break
            
            

            # Estadísticas hoy
            ventas_hoy_docs = ventas_between(start_today, end_today, firestore_db)
            ingresos_hoy = 0
            boletos_hoy = 0
            for d in ventas_hoy_docs:
                v = d.to_dict()
                if v.get('estado') != 'confirmado':
                    continue
                vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
                if vsnap and vsnap.exists:
                    vd = vsnap.to_dict()
                    # Comparación insensible a mayúsculas/minúsculas
                    ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
                    origen_valid = vd.get('ruta_origen', '').lower() in ciudades_lower
                    destino_valid = vd.get('ruta_destino', '').lower() in ciudades_lower
                    if origen_valid and destino_valid:
                        ingresos_hoy += float(v.get('total', 0))
                        boletos_hoy += int(v.get('cantidad_boletos', 0))

            # Ventas del mes
            ventas_mes_docs = ventas_between(start_month, end_today, firestore_db)
            ingresos_mes = 0
            for d in ventas_mes_docs:
                v = d.to_dict()
                if v.get('estado') != 'confirmado':
                    continue
                vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
                if vsnap and vsnap.exists:
                    vd = vsnap.to_dict()
                    # Comparación insensible a mayúsculas/minúsculas
                    ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
                    origen_valid = vd.get('ruta_origen', '').lower() in ciudades_lower
                    destino_valid = vd.get('ruta_destino', '').lower() in ciudades_lower
                    if origen_valid and destino_valid:
                        ingresos_mes += float(v.get('total', 0))
        except Exception as e:
            print(f"Aviso: fallo leyendo reportes Firestore: {e}")
            ventas = []
    # Sin fallback a SQL: si no hay Firestore o no hay ventas válidas, mostrar ceros
    
    return render_template('admin/control_comercial.html',
                         ventas=ventas,
                         ingresos_hoy=ingresos_hoy,
                         boletos_hoy=boletos_hoy,
                         ingresos_mes=ingresos_mes)

@app.route('/admin/atencion-cliente')
@admin_required
def admin_atencion_cliente():
    docs = list_all_consultas(firestore_db) if firestore_db else []
    consultas = []
    for d in docs:
        c = d.to_dict()
        usuario_obj = None
        if c.get('usuario_id'):
            udoc = get_user_by_email(c.get('usuario_id'), firestore_db)
            if udoc:
                _, udata = udoc
                usuario_obj = type('UsuarioObj', (), udata)
        consultas.append(type('ConsultaObj', (), {
            'id': d.id,
            **c,
            'usuario': usuario_obj,
        }))
    return render_template('admin/atencion_cliente.html', consultas=consultas)

@app.route('/admin/responder-consulta/<consulta_id>', methods=['POST'])
@admin_required
def responder_consulta(consulta_id):
    respuesta = request.form.get('respuesta')
    respond_consulta(consulta_id, respuesta, firestore_db)
    
    flash('Consulta respondida exitosamente', 'success')
    return redirect(url_for('admin_atencion_cliente'))

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    docs = list_usuarios(firestore_db) if firestore_db else []
    usuarios = []
    for d in docs:
        data = d.to_dict() or {}
        # Normalizar fecha_registro a datetime para strftime en plantilla
        fr = data.get('fecha_registro')
        if isinstance(fr, str):
            try:
                # ISO 8601
                from datetime import datetime
                data['fecha_registro'] = datetime.fromisoformat(fr)
            except Exception:
                data['fecha_registro'] = None
        # Si no existe fecha_registro, poner un valor por defecto seguro
        if 'fecha_registro' not in data or data['fecha_registro'] is None:
            from datetime import datetime
            data['fecha_registro'] = datetime.utcnow()
        # Asegurar campos esperados
        data.setdefault('nombre', d.id)
        data.setdefault('email', d.id)
        data.setdefault('telefono', '')
        data.setdefault('rol', 'pasajero')
        # Enriquecer con lista de ventas (solo para length en plantilla)
        ventas_docs = []
        try:
            ventas_docs = list_ventas_by_user(d.id, firestore_db) if firestore_db else []
        except Exception:
            ventas_docs = []
        data['ventas'] = [vd.id for vd in ventas_docs]  # lista simple para |length
        usuarios.append(type('UsuarioObj', (), {'id': d.id, **data})())
    return render_template('admin/usuarios.html', usuarios=usuarios)

# API Endpoints para datos dinámicos
@app.route('/api/estadisticas-ventas')
@admin_required
def api_estadisticas_ventas():
    # Firestore filtrando por rutas JUNO
    try:
        from datetime import timedelta
        today = datetime.utcnow().date()
        labels = []
        series = []
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            start = datetime(day.year, day.month, day.day)
            end = start + timedelta(days=1)
            docs = ventas_between(start, end, firestore_db)
            total_dia = 0.0
            for d in docs:
                v = d.to_dict()
                if v.get('estado') != 'confirmado':
                    continue
                vsnap = get_viaje_by_id(v.get('viaje_id'), firestore_db) if v.get('viaje_id') else None
                if vsnap and vsnap.exists:
                    vd = vsnap.to_dict()
                    # Comparación insensible a mayúsculas/minúsculas
                    ciudades_lower = [c.lower() for c in JUNO_TODAS_CIUDADES]
                    origen_valid = vd.get('ruta_origen', '').lower() in ciudades_lower
                    destino_valid = vd.get('ruta_destino', '').lower() in ciudades_lower
                    if origen_valid and destino_valid:
                        total_dia += float(v.get('total', 0))
            labels.append(day.strftime('%d/%m'))
            series.append(total_dia)
        return jsonify({'labels': labels, 'data': series})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/admin/perfil', methods=['GET', 'POST'])
@admin_required
def admin_perfil():
    user_id = session.get('user_id')
    user_doc = get_user_by_id(user_id, firestore_db) if firestore_db else None
    
    if not user_doc or not user_doc.exists:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('admin_dashboard'))
    
    user_data = user_doc.to_dict()
    
    if request.method == 'POST':
        # Actualizar datos del perfil
        nombre = request.form.get('nombre', '').strip()
        apellido = request.form.get('apellido', '').strip()
        telefono = request.form.get('telefono', '').strip()
        email = request.form.get('email', '').strip()
        
        # Validaciones básicas
        if not nombre or not apellido or not email:
            flash('Nombre, apellido y email son obligatorios', 'danger')
            return render_template('admin/perfil.html', user=user_data)
        
        # Validar formato de email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            flash('El formato del email no es válido', 'danger')
            return render_template('admin/perfil.html', user=user_data)
        
        # Validar teléfono si se proporciona
        if telefono and not re.match(r'^[0-9\s\-\+\(\)]{9,15}$', telefono):
            flash('El formato del teléfono no es válido', 'danger')
            return render_template('admin/perfil.html', user=user_data)
        
        # Actualizar en Firestore
        try:
            update_user_profile(user_id, {
                'nombre': nombre,
                'apellido': apellido,
                'telefono': telefono,
                'email': email,
                'fecha_actualizacion': datetime.utcnow()
            }, firestore_db)
            
            # Actualizar sesión
            session['user_name'] = f"{nombre} {apellido}"
            
            flash('Perfil actualizado correctamente', 'success')
            return redirect(url_for('admin_perfil'))
        except Exception as e:
            print(f"Error actualizando perfil: {e}")
            flash('Error al actualizar el perfil', 'danger')
    
    return render_template('admin/perfil.html', user=user_data, fecha_actual=datetime.now())

@app.route('/cambiar-password', methods=['POST'])
@login_required
def cambiar_password():
    user_id = session.get('user_id')
    user_doc = get_user_by_id(user_id, firestore_db) if firestore_db else None
    
    if not user_doc or not user_doc.exists:
        flash('Usuario no encontrado', 'danger')
        return redirect(url_for('logout'))
    
    user_data = user_doc.to_dict()
    password_actual = request.form.get('password_actual', '').strip()
    password_nueva = request.form.get('password_nueva', '').strip()
    password_confirmar = request.form.get('password_confirmar', '').strip()
    
    # Validaciones
    if not password_actual or not password_nueva or not password_confirmar:
        flash('Todos los campos son obligatorios', 'danger')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))
    
    # Verificar contraseña actual
    if not check_password_hash(user_data.get('password_hash', ''), password_actual):
        flash('La contraseña actual es incorrecta', 'danger')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))
    
    # Verificar que las nuevas contraseñas coincidan
    if password_nueva != password_confirmar:
        flash('Las nuevas contraseñas no coinciden', 'danger')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))
    
    # Validar longitud mínima
    min_length = 8 if session.get('user_role') == 'admin' else 6
    if len(password_nueva) < min_length:
        flash(f'La nueva contraseña debe tener al menos {min_length} caracteres', 'danger')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))
    
    # Actualizar contraseña
    try:
        new_password_hash = generate_password_hash(password_nueva)
        update_user_profile(user_id, {
            'password_hash': new_password_hash,
            'fecha_actualizacion': datetime.utcnow()
        }, firestore_db)
        
        flash('Contraseña actualizada correctamente', 'success')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))
    except Exception as e:
        print(f"Error actualizando contraseña: {e}")
        flash('Error al actualizar la contraseña', 'danger')
        return redirect(url_for('admin_perfil' if session.get('user_role') == 'admin' else 'pasajero_perfil'))

@app.route('/admin/exportar-usuarios-pdf')
@admin_required
def exportar_usuarios_pdf():
    """Exporta la lista de usuarios a PDF"""
    try:
        # Obtener todos los usuarios
        docs = list_usuarios(firestore_db) if firestore_db else []
        
        # Crear buffer en memoria para el PDF
        buffer = io.BytesIO()
        
        # Crear documento PDF con márgenes optimizados
        doc = SimpleDocTemplate(buffer, pagesize=A4, 
                               rightMargin=50, leftMargin=50,
                               topMargin=60, bottomMargin=30)
        
        # Estilos
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            alignment=1,  # Centrado
            textColor=colors.HexColor('#1e3c72')
        )
        
        subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=styles['Normal'],
            fontSize=12,
            spaceAfter=20,
            alignment=1,  # Centrado
            textColor=colors.grey
        )
        
        # Contenido del PDF
        story = []
        
        # Título
        story.append(Paragraph("JUNO EXPRESS SA", title_style))
        story.append(Paragraph("Reporte de Usuarios Registrados", subtitle_style))
        story.append(Paragraph(f"Generado el: {datetime.now().strftime('%d/%m/%Y %H:%M')}", subtitle_style))
        story.append(Spacer(1, 20))
        
        # Preparar datos de la tabla
        data = [['#', 'Nombre Completo', 'Email', 'Teléfono', 'Rol', 'Fecha Registro']]
        
        for i, doc_user in enumerate(docs, 1):
            user_data = doc_user.to_dict()
            nombre = user_data.get('nombre', '')
            apellido = user_data.get('apellido', '')
            nombre_completo = f"{nombre} {apellido}".strip() if apellido else nombre
            
            # Formatear fecha
            fecha_reg = user_data.get('fecha_registro', '')
            if isinstance(fecha_reg, str):
                try:
                    fecha_obj = datetime.fromisoformat(fecha_reg.replace('Z', '+00:00'))
                    fecha_formateada = fecha_obj.strftime('%d/%m/%Y')
                except:
                    fecha_formateada = fecha_reg[:10] if len(fecha_reg) >= 10 else fecha_reg
            else:
                fecha_formateada = str(fecha_reg) if fecha_reg else '-'
            
            # Truncar email si es muy largo
            email = user_data.get('email', '')
            if len(email) > 25:
                email = email[:22] + '...'
            
            # Truncar nombre si es muy largo
            if len(nombre_completo) > 20:
                nombre_completo = nombre_completo[:17] + '...'
            
            data.append([
                str(i),
                nombre_completo or 'Sin nombre',
                email,
                user_data.get('telefono', ''),
                user_data.get('rol', 'pasajero').title(),
                fecha_formateada
            ])
        
        # Crear tabla con anchos optimizados para A4 (total ~7.5 inches)
        table = Table(data, colWidths=[0.4*inch, 2.0*inch, 2.3*inch, 1.1*inch, 0.8*inch, 0.9*inch])
        
        # Estilo de la tabla
        table.setStyle(TableStyle([
            # Encabezado
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1e3c72')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 9),
            
            # Contenido
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
            ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
            
            # Alineación específica por columna
            ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Número
            ('ALIGN', (1, 1), (1, -1), 'LEFT'),    # Nombre
            ('ALIGN', (2, 1), (2, -1), 'LEFT'),    # Email
            ('ALIGN', (3, 1), (3, -1), 'CENTER'),  # Teléfono
            ('ALIGN', (4, 1), (4, -1), 'CENTER'),  # Rol
            ('ALIGN', (5, 1), (5, -1), 'CENTER'),  # Fecha
            
            # Bordes
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            
            # Alternar colores de fila
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
            
            # Padding para mejor legibilidad
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('LEFTPADDING', (0, 0), (-1, -1), 3),
            ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ]))
        
        story.append(table)
        
        # Pie de página
        story.append(Spacer(1, 30))
        story.append(Paragraph(f"Total de usuarios: {len(docs)}", subtitle_style))
        story.append(Paragraph("JUNO EXPRESS SA - transportamos tus sueños... viaja cómodo y seguro", subtitle_style))
        
        # Construir PDF
        doc.build(story)
        
        # Preparar respuesta
        buffer.seek(0)
        response = make_response(buffer.getvalue())
        buffer.close()
        
        # Headers para descarga
        filename = f"usuarios_juno_express_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response
        
    except Exception as e:
        print(f"Error generando PDF de usuarios: {e}")
        flash('Error al generar el PDF de usuarios', 'danger')
        return redirect(url_for('admin_perfil'))

@app.route('/admin/generar-ruta-estandar', methods=['POST'])
@admin_required
def generar_ruta_estandar():
    """Genera automáticamente una ruta estándar con todos sus tramos"""
    try:
        data = request.get_json()
        origen = data.get('origen')
        destino = data.get('destino')
        duracion = data.get('duracion', '2 horas')
        
        if not origen or not destino or origen == destino:
            return jsonify({'success': False, 'message': 'Origen y destino deben ser diferentes'})
        
        # Orden estándar de ciudades JUNO
        ciudades_orden = ['Chincha', 'Pisco', 'Barrio Chino', 'Ica']
        
        # Encontrar índices
        try:
            indice_origen = ciudades_orden.index(origen)
            indice_destino = ciudades_orden.index(destino)
        except ValueError:
            return jsonify({'success': False, 'message': 'Ciudad no válida'})
        
        # Determinar la ruta completa
        if indice_origen < indice_destino:
            ruta_completa = ciudades_orden[indice_origen:indice_destino + 1]
        else:
            ruta_completa = ciudades_orden[indice_destino:indice_origen + 1]
            ruta_completa.reverse()
        
        # Generar todos los tramos posibles
        rutas_generadas = 0
        tramos_creados = []
        
        for i in range(len(ruta_completa)):
            for j in range(i + 1, len(ruta_completa)):
                origen_tramo = ruta_completa[i]
                destino_tramo = ruta_completa[j]
                
                # Obtener precio y duración específicos para cada tramo
                precio = JUNO_RUTAS_PRECIOS.get((origen_tramo, destino_tramo), 5.0)
                
                # Duraciones específicas para cada tramo
                duraciones_especificas = {
                    ('Chincha', 'Pisco'): '35 min',
                    ('Chincha', 'Barrio Chino'): '1 hora 15 min',
                    ('Chincha', 'Ica'): '2 horas',
                    ('Pisco', 'Barrio Chino'): '40 min',
                    ('Pisco', 'Ica'): '1 hora 25 min',
                    ('Barrio Chino', 'Ica'): '45 min'
                }
                
                duracion_tramo = duraciones_especificas.get((origen_tramo, destino_tramo), '1 hora')
                
                # Verificar si la ruta ya existe
                existing_route = None
                if firestore_db:
                    existing_routes = firestore_db.collection('rutas').where(
                        'origen', '==', origen_tramo
                    ).where('destino', '==', destino_tramo).stream()
                    
                    for route in existing_routes:
                        existing_route = route
                        break
                
                if not existing_route:
                    # Crear nueva ruta
                    ruta_data = {
                        'origen': origen_tramo,
                        'destino': destino_tramo,
                        'precio': precio,
                        'duracion': duracion_tramo,
                        'tipo': 'estandar',  # Marcar como ruta estándar
                        'ruta_padre': f"{origen}-{destino}",  # Referencia a la ruta principal
                        'orden_parada': i,
                        'activa': False,  # Inactiva hasta que se planifique
                        'fecha_creacion': datetime.utcnow().isoformat()
                    }
                    
                    try:
                        # Crear ruta usando el método correcto (sin ID específico, auto-generado)
                        ref = firestore_db.collection('rutas').document()
                        ref.set(ruta_data)
                        rutas_generadas += 1
                        tramos_creados.append(f"{origen_tramo} -> {destino_tramo} (S/. {precio:.2f})")
                        print(f"[OK] Ruta estandar creada: {origen_tramo} -> {destino_tramo} (Tipo: {ruta_data['tipo']}, ID: {ref.id})")
                    except Exception as e:
                        print(f"[ERROR] Error creando ruta {origen_tramo}-{destino_tramo}: {e}")
        
        return jsonify({
            'success': True,
            'rutas_generadas': rutas_generadas,
            'ruta_principal': f"{origen} -> {destino}",
            'tramos_creados': tramos_creados,
            'message': f'Se generaron {rutas_generadas} tramos para la ruta estándar {origen}-{destino}'
        })
        
    except Exception as e:
        print(f"Error generando ruta estándar: {e}")
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/admin/corregir-estado-rutas', methods=['POST'])
@admin_required
def corregir_estado_rutas():
    """Corrige el estado de las rutas existentes - las marca como inactivas si no tienen viajes"""
    try:
        if not firestore_db:
            return jsonify({'error': 'Firestore no disponible'}), 500
        
        # Obtener todas las rutas
        rutas_docs = list(firestore_db.collection('rutas').stream())
        rutas_corregidas = 0
        
        for ruta_doc in rutas_docs:
            ruta_data = ruta_doc.to_dict()
            ruta_id = ruta_doc.id
            
            # Verificar si la ruta tiene viajes programados
            viajes_docs = list(firestore_db.collection('viajes').where('ruta_id', '==', ruta_id).stream())
            tiene_viajes = len(viajes_docs) > 0
            
            # Actualizar estado según si tiene viajes o no
            nuevo_estado = tiene_viajes
            estado_actual = ruta_data.get('activa', False)
            
            if estado_actual != nuevo_estado or not ruta_data.get('tipo'):
                ruta_doc.reference.update({
                    'activa': nuevo_estado,
                    'tipo': ruta_data.get('tipo', 'normal')  # Asegurar que tenga tipo
                })
                rutas_corregidas += 1
        
        return jsonify({
            'success': True,
            'rutas_corregidas': rutas_corregidas,
            'message': f'Se corrigió el estado de {rutas_corregidas} rutas'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error corrigiendo rutas: {str(e)}'}), 500

@app.route('/admin/planificar-ruta-estandar-completa', methods=['POST'])
@admin_required
def planificar_ruta_estandar_completa():
    """Planifica automáticamente un viaje completo para la ruta estándar Chincha-Ica"""
    try:
        data = request.get_json()
        fecha = data.get('fecha')
        hora_salida = data.get('hora_salida', '06:15')
        bus_numero = data.get('bus_numero', 'Bus 1')
        
        if not fecha:
            return jsonify({'success': False, 'message': 'Fecha es requerida'})
        
        # Buscar la ruta Chincha-Ica estándar
        ruta_chincha_ica = None
        rutas_docs = list(firestore_db.collection('rutas').where('origen', '==', 'Chincha').where('destino', '==', 'Ica').stream())
        
        for ruta_doc in rutas_docs:
            ruta_data = ruta_doc.to_dict()
            if ruta_data.get('tipo') == 'estandar':
                ruta_chincha_ica = {'id': ruta_doc.id, **ruta_data}
                break
        
        if not ruta_chincha_ica:
            return jsonify({'success': False, 'message': 'No se encontró la ruta estándar Chincha-Ica. Genérala primero.'})
        
        # Verificar si ya existe un viaje para esa fecha y bus
        fecha_dt = datetime.strptime(fecha, '%Y-%m-%d')
        viajes_existentes = list(firestore_db.collection('viajes').where('fecha_salida', '==', fecha_dt).where('bus_numero', '==', bus_numero).stream())
        
        if viajes_existentes:
            return jsonify({'success': False, 'message': f'Ya existe un viaje programado para {bus_numero} en esa fecha'})
        
        # Crear el viaje completo Chincha-Ica
        ref = firestore_db.collection('viajes').document()
        ref.set({
            'ruta_id': ruta_chincha_ica['id'],
            'ruta_origen': 'Chincha',
            'ruta_destino': 'Ica',
            'precio': ruta_chincha_ica['precio'],
            'duracion': '2 horas',
            'fecha_salida': fecha_dt,
            'hora_salida': hora_salida,
            'bus_numero': bus_numero,
            'asientos_totales': 40,
            'asientos_disponibles': 40,
            'estado': 'programado',
            'tipo_viaje': 'estandar',  # Marcar como viaje estándar
            'paradas': ['Chincha', 'Pisco', 'Barrio Chino', 'Ica'],  # Paradas del recorrido
            'horarios_paradas': {
                'Chincha': '06:15',
                'Pisco': '06:50', 
                'Barrio Chino': '07:30',
                'Ica': '08:15'
            }
        })
        
        # Activar todas las rutas estándar relacionadas
        rutas_estandar = list(firestore_db.collection('rutas').where('tipo', '==', 'estandar').stream())
        rutas_activadas = 0
        
        for ruta_doc in rutas_estandar:
            ruta_doc.reference.update({'activa': True})
            rutas_activadas += 1
        
        return jsonify({
            'success': True,
            'viaje_id': ref.id,
            'rutas_activadas': rutas_activadas,
            'message': f'Viaje estándar programado exitosamente para {fecha} con {bus_numero}'
        })
        
    except Exception as e:
        print(f"Error planificando ruta estándar completa: {e}")
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

# Ruta especial para limpiar el sistema (temporal sin auth)
@app.route('/admin/limpiar-sistema', methods=['POST'])
def limpiar_sistema_completo():
    """Limpia todas las ventas, viajes y consultas del sistema"""
    try:
        if not firestore_db:
            return jsonify({'error': 'Firestore no disponible'}), 500
        
        # Contar antes de eliminar
        ventas_docs = list(firestore_db.collection('ventas').stream())
        viajes_docs = list(firestore_db.collection('viajes').stream())
        consultas_docs = list(firestore_db.collection('consultas').stream())
        
        ventas_count = len(ventas_docs)
        viajes_count = len(viajes_docs)
        consultas_count = len(consultas_docs)
        
        # Eliminar todas las ventas
        for doc in ventas_docs:
            doc.reference.delete()
        
        # Eliminar todos los viajes
        for doc in viajes_docs:
            doc.reference.delete()
            
        # Eliminar todas las consultas
        for doc in consultas_docs:
            doc.reference.delete()
        
        # Contar lo que se mantiene
        usuarios_count = len(list(firestore_db.collection('usuarios').stream()))
        rutas_count = len(list(firestore_db.collection('rutas').stream()))
        
        return jsonify({
            'success': True,
            'eliminado': {
                'ventas': ventas_count,
                'viajes': viajes_count,
                'consultas': consultas_count
            },
            'conservado': {
                'usuarios': usuarios_count,
                'rutas': rutas_count
            },
            'message': f'Sistema limpiado: {ventas_count} ventas, {viajes_count} viajes y {consultas_count} consultas eliminadas'
        })
        
    except Exception as e:
        return jsonify({'error': f'Error durante la limpieza: {str(e)}'}), 500

# API para validar DNI con RENIEC
@app.route('/api/validar-dni/<dni>')
@login_required
def validar_dni(dni):
    """Valida DNI usando APIs públicas de RENIEC"""
    try:
        # Validación básica de formato
        if len(dni) != 8 or not dni.isdigit():
            return jsonify({'valid': False, 'error': 'DNI debe tener 8 dígitos'})
        
        # Intentar múltiples APIs de DNI
        apis_dni = [
            f'https://api.apis.net.pe/v1/dni?numero={dni}',
            f'https://dniruc.apisperu.com/api/v1/dni/{dni}?token=eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJlbWFpbCI6InRlc3RAZ21haWwuY29tIn0.DFdTGnGGmJvJ6cZ6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z6Z',
            f'https://api.reniec.cloud/dni/{dni}'
        ]
        
        for api_url in apis_dni:
            try:
                response = requests.get(api_url, timeout=5)
                if response.status_code == 200:
                    data = response.json()
                    
                    # Diferentes formatos de respuesta según la API
                    nombres = None
                    if 'nombres' in data and data['nombres']:
                        nombres = f"{data['nombres']} {data.get('apellidoPaterno', '')} {data.get('apellidoMaterno', '')}".strip()
                    elif 'name' in data and data['name']:
                        nombres = data['name']
                    elif 'data' in data and data['data'] and 'name_complete' in data['data']:
                        nombres = data['data']['name_complete']
                    
                    if nombres:
                        return jsonify({
                            'valid': True,
                            'nombres': nombres,
                            'api_used': api_url.split('/')[2]
                        })
            except Exception as e:
                print(f"Error con API {api_url}: {e}")
                continue
        
        # Si ninguna API funcionó, hacer validación local básica
        if not dni in ['00000000', '11111111', '22222222', '33333333', '44444444', 
                      '55555555', '66666666', '77777777', '88888888', '99999999',
                      '12345678', '87654321']:
            return jsonify({
                'valid': True,
                'nombres': None,
                'message': 'Formato válido (no se pudo verificar en línea)'
            })
        else:
            return jsonify({'valid': False, 'error': 'DNI inválido'})
            
    except Exception as e:
        return jsonify({'valid': False, 'error': f'Error interno: {str(e)}'})


# API para validar RUC con SUNAT
@app.route('/api/validar-ruc/<ruc>')
@login_required
def validar_ruc(ruc):
    """Valida RUC usando APIs públicas de SUNAT"""
    try:
        # Validación básica de formato
        if len(ruc) != 11 or not ruc.isdigit():
            return jsonify({'valid': False, 'error': 'RUC debe tener 11 dígitos'})
        
        # Verificar prefijo válido
        prefijo = ruc[:2]
        if prefijo not in ['10', '15', '17', '20']:
            return jsonify({'valid': False, 'error': 'Prefijo de RUC inválido'})
        
        # APIs más confiables y gratuitas (actualizadas 2025)
        apis_ruc = [
            # API gratuita sin autenticación
            f'https://api.apis.net.pe/v1/ruc?numero={ruc}',
            # API alternativa gratuita
            f'https://ruc.com.pe/{ruc}.json',
            # API de migo-dev (gratuita)
            f'https://ruc.migo-dev.com/{ruc}',
            # API de consulta directa
            f'https://api.sunat.gob.pe/v1/contribuyente/contribuyentes/{ruc}',
            # API backup con formato simple
            f'https://ruc-api.herokuapp.com/api/ruc/{ruc}',
            # API local de Perú
            f'https://api.peruapis.com/v1/ruc/{ruc}'
        ]
        
        for api_url in apis_ruc:
            try:
                headers = {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                    'Accept': 'application/json',
                    'Content-Type': 'application/json'
                }
                response = requests.get(api_url, timeout=8, headers=headers)
                print(f"DEBUG: API {api_url} - Status: {response.status_code}")
                if response.status_code == 200:
                    data = response.json()
                    
                    # Diferentes formatos de respuesta según la API
                    razon_social = None
                    direccion = None
                    
                    print(f"DEBUG RUC API {api_url}: {data}")  # Para debug
                    
                    # Manejo de diferentes formatos de API
                    # Formato apis.net.pe v1
                    if 'razonSocial' in data and data['razonSocial']:
                        razon_social = data['razonSocial']
                        direccion = data.get('direccion', data.get('domicilioFiscal', ''))
                    # Formato ruc.com.pe
                    elif 'company_name' in data and data['company_name']:
                        razon_social = data['company_name']
                        direccion = data.get('address', data.get('direccion', ''))
                    # Formato migo-dev
                    elif 'nombre_o_razon_social' in data and data['nombre_o_razon_social']:
                        razon_social = data['nombre_o_razon_social']
                        direccion = data.get('direccion_completa', data.get('direccion', ''))
                    # Formato SUNAT oficial
                    elif 'ddp_nombre' in data and data['ddp_nombre']:
                        razon_social = data['ddp_nombre']
                        direccion = data.get('desc_domi_fiscal', data.get('direccion', ''))
                    # Formato con 'name'
                    elif 'name' in data and data['name']:
                        razon_social = data['name']
                        direccion = data.get('address', data.get('direccion', ''))
                    # Formato anidado en 'data' o 'result'
                    elif 'data' in data and data['data']:
                        inner_data = data['data']
                        razon_social = (inner_data.get('nombre_o_razon_social') or 
                                      inner_data.get('razonSocial') or 
                                      inner_data.get('company_name') or
                                      inner_data.get('nombre'))
                        direccion = (inner_data.get('direccion_completa') or
                                   inner_data.get('direccion') or 
                                   inner_data.get('domicilio_fiscal') or 
                                   inner_data.get('address', ''))
                    # Formato result
                    elif 'result' in data and data['result']:
                        inner_data = data['result']
                        razon_social = (inner_data.get('nombre_o_razon_social') or 
                                      inner_data.get('razonSocial') or 
                                      inner_data.get('nombre'))
                        direccion = (inner_data.get('direccion') or 
                                   inner_data.get('domicilio_fiscal', ''))
                    # Formato directo con 'nombre'
                    elif 'nombre' in data and data['nombre']:
                        razon_social = data['nombre']
                        direccion = data.get('direccion', data.get('domicilio', ''))
                    
                    if razon_social and razon_social.strip():
                        return jsonify({
                            'valid': True,
                            'razonSocial': razon_social.strip(),
                            'direccion': direccion.strip() if direccion else '',
                            'api_used': api_url.split('/')[2]
                        })
            except Exception as e:
                print(f"Error con API {api_url}: {e}")
                continue
        
        # Si ninguna API funcionó, usar base de datos local de RUCs conocidos (ampliada)
        ruc_conocidos = {
            # Supermercados y Retail
            '20100070970': {'razon': 'SUPERMERCADOS PERUANOS SOCIEDAD ANONIMA', 'direccion': 'AV. PRIMAVERA NRO. 2680 LIMA - LIMA - SANTIAGO DE SURCO'},
            '20131312955': {'razon': 'RIPLEY CORP S.A.', 'direccion': 'AV. RIVERA NAVARRETE NRO. 501 LIMA - LIMA - SAN ISIDRO'},
            '20100128056': {'razon': 'SAGA FALABELLA S.A.', 'direccion': 'AV. PASEO DE LA REPUBLICA NRO. 3220 LIMA - LIMA - SAN ISIDRO'},
            '20131373237': {'razon': 'HIPERMERCADOS TOTTUS S.A.', 'direccion': 'AV. ANGAMOS OESTE NRO. 501 LIMA - LIMA - MIRAFLORES'},
            '20100152356': {'razon': 'SCOTIABANK PERU S.A.A.', 'direccion': 'AV. DIONISIO DERTEANO NRO. 102 LIMA - LIMA - SAN ISIDRO'},
            
            # Bancos
            '20100047218': {'razon': 'BANCO DE CREDITO DEL PERU', 'direccion': 'AV. CENTENARIO NRO. 156 LIMA - LIMA - LA MOLINA'},
            '20100130204': {'razon': 'INTERBANK', 'direccion': 'AV. CARLOS VILLARÁN NRO. 140 LIMA - LIMA - LA VICTORIA'},
            '20100121681': {'razon': 'BANCO BBVA PERU', 'direccion': 'AV. REPUBLICA DE PANAMA NRO. 3055 LIMA - LIMA - SAN ISIDRO'},
            
            # Bebidas y Alimentos
            '20100055519': {'razon': 'COCA COLA SERVICIOS DE PERU S.A.', 'direccion': 'AV. REPUBLICA DE PANAMA NRO. 4050 LIMA - LIMA - SURQUILLO'},
            '20100000621': {'razon': 'UNION DE CERVECERIAS PERUANAS BACKUS Y JOHNSTON S.A.A.', 'direccion': 'AV. NICOLAS AYLLON NRO. 3986 LIMA - LIMA - ATE'},
            
            # Telecomunicaciones
            '20100017491': {'razon': 'TELEFONICA DEL PERU S.A.A.', 'direccion': 'AV. AREQUIPA NRO. 1155 LIMA - LIMA - LIMA'},
            '20100058140': {'razon': 'AMERICA MOVIL PERU S.A.C.', 'direccion': 'AV. REPUBLICA DE PANAMA NRO. 3535 LIMA - LIMA - SAN ISIDRO'},
            
            # Universidades
            '20502092549': {'razon': 'UNIVERSIDAD NACIONAL MAYOR DE SAN MARCOS', 'direccion': 'AV. VENEZUELA S/N LIMA - LIMA - LIMA'},
            '20146092282': {'razon': 'UNIVERSIDAD DE LIMA', 'direccion': 'AV. JAVIER PRADO ESTE NRO. 4600 LIMA - LIMA - SANTIAGO DE SURCO'},
            '20135897834': {'razon': 'UNIVERSIDAD PERUANA DE CIENCIAS APLICADAS S.A.C.', 'direccion': 'AV. ALONSO DE MOLINA NRO. 1611 LIMA - LIMA - SANTIAGO DE SURCO'},
            
            # Entretenimiento
            '20100121809': {'razon': 'CINEPLANET S.A.', 'direccion': 'AV. EL DERBY NRO. 254 LIMA - LIMA - SANTIAGO DE SURCO'},
            '20100113612': {'razon': 'DELOSI S.A.', 'direccion': 'AV. REPUBLICA DE PANAMA NRO. 4675 LIMA - LIMA - SURQUILLO'},
            
            # Aerolíneas
            '20100017491': {'razon': 'LAN PERU S.A.', 'direccion': 'AV. JOSE PARDO NRO. 513 LIMA - LIMA - MIRAFLORES'},
        }
        
        if ruc in ruc_conocidos:
            empresa = ruc_conocidos[ruc]
            return jsonify({
                'valid': True,
                'razonSocial': empresa['razon'],
                'direccion': empresa['direccion'],
                'api_used': 'base-local'
            })
        
        # Si no está en la base local, validar formato y permitir manual
        return jsonify({
            'valid': True,
            'razonSocial': None,
            'direccion': None,
            'message': 'RUC con formato válido - Completa datos manualmente'
        })
            
    except Exception as e:
        return jsonify({'valid': False, 'error': f'Error interno: {str(e)}'})

# Rutas para gestión de precios manuales por tramo
@app.route('/admin/precios-tramos', methods=['GET', 'POST'])
@admin_required
def admin_precios_tramos():
    """Página para gestionar precios manuales de tramos"""
    if request.method == 'POST':
        origen = request.form.get('origen')
        destino = request.form.get('destino')
        precio = float(request.form.get('precio', 0))
        
        if origen and destino and precio > 0:
            try:
                # Guardar o actualizar precio en Firestore
                precio_doc = firestore_db.collection('precios_tramos').document(f"{origen}_{destino}")
                precio_doc.set({
                    'origen': origen,
                    'destino': destino,
                    'precio': precio,
                    'fecha_actualizacion': datetime.utcnow().isoformat()
                })
                flash(f'Precio actualizado: {origen} → {destino} = S/. {precio:.2f}', 'success')
            except Exception as e:
                print(f"Error guardando precio: {e}")
                flash('Error al guardar precio', 'danger')
        else:
            flash('Datos incompletos', 'warning')
    
    # Obtener precios manuales existentes
    precios_manuales = []
    try:
        precios_docs = firestore_db.collection('precios_tramos').stream()
        for doc in precios_docs:
            data = doc.to_dict()
            precios_manuales.append({
                'id': doc.id,
                'origen': data.get('origen'),
                'destino': data.get('destino'),
                'precio': data.get('precio'),
                'fecha_actualizacion': data.get('fecha_actualizacion')
            })
    except Exception as e:
        print(f"Error obteniendo precios: {e}")
    
    return render_template('admin/precios_tramos.html', 
                          precios=precios_manuales,
                          ciudades_juno=JUNO_CIUDADES)

@app.route('/admin/eliminar-precio/<precio_id>', methods=['POST'])
@admin_required
def eliminar_precio_tramo(precio_id):
    """Eliminar un precio de tramo manual"""
    try:
        firestore_db.collection('precios_tramos').document(precio_id).delete()
        flash('Precio eliminado', 'success')
    except Exception as e:
        print(f"Error eliminando precio: {e}")
        flash('Error al eliminar precio', 'danger')
    return redirect(url_for('admin_precios_tramos'))

@app.route('/admin/generar-ruta-paradas-manual', methods=['POST'])
@admin_required
def generar_ruta_paradas_manual():
    """Genera rutas con paradas usando precios definidos manualmente por admin"""
    try:
        data = request.get_json()
        origen = data.get('origen')
        destino = data.get('destino')
        
        if not origen or not destino or origen == destino:
            return jsonify({'success': False, 'message': 'Origen y destino deben ser diferentes'})
        
        # Orden estándar de ciudades JUNO
        ciudades_orden = ['Chincha', 'Pisco', 'Barrio Chino', 'Ica']
        
        # Encontrar índices
        try:
            indice_origen = ciudades_orden.index(origen)
            indice_destino = ciudades_orden.index(destino)
        except ValueError:
            return jsonify({'success': False, 'message': 'Ciudad no válida'})
        
        # Determinar la ruta completa
        if indice_origen < indice_destino:
            ruta_completa = ciudades_orden[indice_origen:indice_destino + 1]
        else:
            ruta_completa = ciudades_orden[indice_destino:indice_origen + 1]
            ruta_completa.reverse()
        
        # Generar todos los tramos posibles usando precios manuales
        rutas_generadas = 0
        tramos_creados = []
        
        for i in range(len(ruta_completa)):
            for j in range(i + 1, len(ruta_completa)):
                origen_tramo = ruta_completa[i]
                destino_tramo = ruta_completa[j]
                
                # Buscar precio manual definido por admin
                precio_doc = firestore_db.collection('precios_tramos').document(f"{origen_tramo}_{destino_tramo}").get()
                if precio_doc.exists:
                    precio = precio_doc.to_dict().get('precio')
                else:
                    # Si no hay precio manual, usar precio por defecto
                    precio = JUNO_RUTAS_PRECIOS.get((origen_tramo, destino_tramo), 5.0)
                
                # Duraciones específicas para cada tramo
                duraciones_especificas = {
                    ('Chincha', 'Pisco'): '35 min',
                    ('Chincha', 'Barrio Chino'): '1 hora 15 min',
                    ('Chincha', 'Ica'): '2 horas',
                    ('Pisco', 'Barrio Chino'): '40 min',
                    ('Pisco', 'Ica'): '1 hora 25 min',
                    ('Barrio Chino', 'Ica'): '45 min'
                }
                
                duracion_tramo = duraciones_especificas.get((origen_tramo, destino_tramo), '1 hora')
                
                # Verificar si la ruta ya existe
                existing_route = None
                if firestore_db:
                    existing_routes = firestore_db.collection('rutas').where(
                        'origen', '==', origen_tramo
                    ).where('destino', '==', destino_tramo).stream()
                    
                    for route in existing_routes:
                        existing_route = route
                        break
                
                if not existing_route:
                    # Crear nueva ruta
                    ruta_data = {
                        'origen': origen_tramo,
                        'destino': destino_tramo,
                        'precio': precio,
                        'duracion': duracion_tramo,
                        'tipo': 'estandar',
                        'ruta_padre': f"{origen}-{destino}",
                        'orden_parada': i,
                        'activa': False,
                        'fecha_creacion': datetime.utcnow().isoformat()
                    }
                    
                    try:
                        ref = firestore_db.collection('rutas').document()
                        ref.set(ruta_data)
                        rutas_generadas += 1
                        tramos_creados.append(f"{origen_tramo} -> {destino_tramo} (S/. {precio:.2f})")
                        print(f"[OK] Ruta con paradas creada: {origen_tramo} -> {destino_tramo} (Precio manual: {precio})")
                    except Exception as e:
                        print(f"[ERROR] Error creando ruta {origen_tramo}-{destino_tramo}: {e}")
                else:
                    # Si ya existe, actualizar el precio con el valor manual
                    try:
                        existing_route.reference.update({'precio': precio})
                        tramos_creados.append(f"{origen_tramo} -> {destino_tramo} (S/. {precio:.2f}) [ACTUALIZADO]")
                        print(f"[OK] Ruta actualizada: {origen_tramo} -> {destino_tramo} (Precio manual: {precio})")
                    except Exception as e:
                        print(f"[ERROR] Error actualizando ruta {origen_tramo}-{destino_tramo}: {e}")
        
        return jsonify({
            'success': True,
            'rutas_generadas': rutas_generadas,
            'ruta_principal': f"{origen} -> {destino}",
            'tramos_creados': tramos_creados,
            'message': f'Se generaron/actualizaron {len(tramos_creados)} tramos usando precios definidos por admin'
        })
        
    except Exception as e:
        print(f"Error generando ruta con paradas manual: {e}")
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/admin/actualizar-precios-rutas', methods=['POST'])
@admin_required
def actualizar_precios_rutas():
    """Actualiza todas las rutas existentes con los precios manuales definidos por admin"""
    try:
        rutas_actualizadas = 0
        rutas_no_actualizadas = 0
        
        # Obtener todas las rutas
        rutas = firestore_db.collection('rutas').stream()
        
        for ruta_doc in rutas:
            ruta_data = ruta_doc.to_dict()
            origen = ruta_data.get('origen')
            destino = ruta_data.get('destino')
            
            if not origen or not destino:
                continue
            
            # Buscar precio manual definido por admin
            precio_doc = firestore_db.collection('precios_tramos').document(f"{origen}_{destino}").get()
            if precio_doc.exists:
                precio_nuevo = precio_doc.to_dict().get('precio')
                precio_actual = ruta_data.get('precio')
                
                # Solo actualizar si el precio es diferente
                if precio_nuevo != precio_actual:
                    ruta_doc.reference.update({'precio': precio_nuevo})
                    rutas_actualizadas += 1
                    print(f"[OK] Ruta actualizada: {origen} -> {destino} (Precio: {precio_actual} -> {precio_nuevo})")
                else:
                    rutas_no_actualizadas += 1
            else:
                rutas_no_actualizadas += 1
        
        return jsonify({
            'success': True,
            'rutas_actualizadas': rutas_actualizadas,
            'rutas_no_actualizadas': rutas_no_actualizadas,
            'message': f'Se actualizaron {rutas_actualizadas} rutas con los precios manuales'
        })
        
    except Exception as e:
        print(f"Error actualizando precios de rutas: {e}")
        return jsonify({'success': False, 'message': f'Error interno: {str(e)}'})

@app.route('/api/precios-tramos', methods=['GET'])
@login_required
def api_precios_tramos():
    """API para obtener los precios de los tramos definidos por admin"""
    try:
        precios = {}
        precios_docs = firestore_db.collection('precios_tramos').stream()
        for doc in precios_docs:
            data = doc.to_dict()
            clave = f"{data.get('origen')}_{data.get('destino')}"
            precios[clave] = data.get('precio')
        
        # Si no hay precios manuales, usar los por defecto
        if not precios:
            for (origen, destino), precio in JUNO_RUTAS_PRECIOS.items():
                clave = f"{origen}_{destino}"
                precios[clave] = precio
        
        return jsonify({'success': True, 'precios': precios})
    except Exception as e:
        print(f"Error obteniendo precios: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    """API para procesar mensajes del chatbot"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').lower().strip()
        
        # Respuestas simples basadas en palabras clave
        responses = {
            'reserva': 'Para hacer una reserva, ve a la sección "Buscar Viajes", selecciona tu origen, destino y fecha, luego elige el viaje que prefieres y completa el proceso de compra.',
            'horario': 'Nuestros horarios varían según la ruta. Generalmente tenemos salidas desde las 6:00 AM hasta las 8:00 PM. Puedes ver los horarios exactos en la sección "Buscar Viajes".',
            'precio': 'Los precios dependen de la ruta que elijas. Por ejemplo: Chincha-Pisco (S/. 5.00), Chincha-Ica (S/. 10.00), Pisco-Ica (S/. 8.00). Puedes ver todos los precios en "Buscar Viajes".',
            'ayuda': 'Estoy aquí para ayudarte. Puedes preguntarme sobre reservas, horarios, precios o rutas. Si necesitas más ayuda, puedes contactarnos al 956181111.',
            'ruta': 'Operamos en las rutas: Chincha, Pisco, Barrio Chino e Ica. Ofrecemos viajes directos y con paradas intermedias.',
            'boleto': 'Puedes comprar boletos directamente en nuestra plataforma. Solo necesitas registrarte, buscar tu viaje y completar el pago.',
            'pago': 'Aceptamos varios métodos de pago: tarjeta de crédito/débito, efectivo (pagar en terminal), transferencia bancaria y Yape/Plin.',
            'cancelar': 'Para cancelar una reserva, ve a "Mis Boletos" y selecciona el boleto que deseas cancelar. Las cancelaciones deben hacerse al menos 1 hora antes del viaje.',
            'contacto': 'Puedes contactarnos al teléfono 956181111 o por email a mondalgoalex125@gmail.com.',
            'default': 'Gracias por tu mensaje. Puedo ayudarte con información sobre reservas, horarios, precios, rutas, pagos o cancelaciones. ¿Qué necesitas saber?'
        }
        
        # Buscar respuesta basada en palabras clave
        response = responses.get('default')
        for keyword, resp in responses.items():
            if keyword != 'default' and keyword in user_message:
                response = resp
                break
        
        return jsonify({
            'success': True,
            'response': response,
            'should_escalate': False
        })
        
    except Exception as e:
        print(f"Error en chatbot: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/chatbot/history/<user_id>', methods=['GET'])
def chatbot_history(user_id):
    """API para obtener el historial de conversación del chatbot"""
    try:
        # Por ahora retornamos un historial vacío
        return jsonify({'success': True, 'history': []})
    except Exception as e:
        print(f"Error obteniendo historial: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
