from typing import Optional, Tuple, Dict, Any
from datetime import datetime

import firebase_admin
from firebase_admin import firestore


def _get_client(provided: Optional[firestore.Client] = None) -> firestore.Client:
    """Return a Firestore client. If not provided, use the default app client."""
    if provided is not None:
        return provided
    # Assumes firebase_admin.initialize_app() was already called in app startup
    return firestore.client()


def users_collection(client: Optional[firestore.Client] = None):
    return _get_client(client).collection("usuarios")


def rutas_collection(client: Optional[firestore.Client] = None):
    return _get_client(client).collection("rutas")


def viajes_collection(client: Optional[firestore.Client] = None):
    return _get_client(client).collection("viajes")


def ventas_collection(client: Optional[firestore.Client] = None):
    return _get_client(client).collection("ventas")


def get_user_by_email(email: str, client: Optional[firestore.Client] = None) -> Optional[Tuple[str, Dict[str, Any]]]:
    """Return (doc_id, data) for the first user with the given email, or None."""
    query = users_collection(client).where("email", "==", email).limit(1)
    results = list(query.stream())
    if not results:
        return None
    doc = results[0]
    return doc.id, doc.to_dict()


def create_user_doc(user_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    users_collection(client).document(str(user_id)).set(data)


def ensure_user_doc(user: Any, client: Optional[firestore.Client] = None) -> None:
    """Ensure a user document exists based on a SQLAlchemy user object.

    Expected user fields: id, nombre, email, telefono, rol, fecha_registro, password (hash).
    Stores password hash under 'password_hash'.
    """
    doc_ref = users_collection(client).document(str(user.id))
    snap = doc_ref.get()
    if not snap.exists:
        payload: Dict[str, Any] = {
            "nombre": getattr(user, "nombre", None),
            "email": getattr(user, "email", None),
            "telefono": getattr(user, "telefono", None),
            "rol": getattr(user, "rol", None),
            "fecha_registro": (getattr(user, "fecha_registro", None) or datetime.utcnow()).isoformat(),
            "password_hash": getattr(user, "password", None),
            "origen": "migracion-sqlite",
        }
        doc_ref.set(payload)


# ----- RUTAS -----
def create_ruta_doc(ruta_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    rutas_collection(client).document(str(ruta_id)).set(data)


# ----- VIAJES -----
def create_viaje_doc(viaje_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    viajes_collection(client).document(str(viaje_id)).set(data)


def list_upcoming_viajes(limit: int = 6, client: Optional[firestore.Client] = None):
    """Lista próximos viajes programados ordenados por fecha_salida.

    Nota: Para evitar índices compuestos, obtenemos todos los viajes programados
    y filtramos/ordenamos en cliente.
    """
    today = datetime.utcnow().date()
    col = viajes_collection(client)
    # Solo filtrar por estado para evitar índice compuesto
    q = col.where("estado", "==", "programado")
    docs = list(q.stream())
    items = []
    for d in docs:
        data = d.to_dict() or {}
        if data.get("asientos_disponibles", 0) <= 0:
            continue
        dt = data.get("fecha_salida")
        # Aceptar si la fecha del viaje es hoy o futura
        if hasattr(dt, 'date') and dt.date() < today:
            continue
        items.append(d)
    
    # Ordenar por fecha_salida en cliente
    items.sort(key=lambda x: x.to_dict().get("fecha_salida") or datetime.min)
    return items[:limit]


def search_viajes(origen: Optional[str], destino: Optional[str], fecha: Optional[datetime], client: Optional[firestore.Client] = None):
    """Busca viajes próximos. Filtra en cliente por fecha (>= hoy), origen/destino y fecha exacta opcional."""
    today = datetime.utcnow().date()
    col = viajes_collection(client)
    # Solo filtrar por estado para evitar índice compuesto
    q = col.where("estado", "==", "programado")
    docs = list(q.stream())
    res = []
    for d in docs:
        data = d.to_dict() or {}
        if data.get("asientos_disponibles", 0) <= 0:
            continue
        if origen and origen.lower() not in str(data.get("ruta_origen", "")).lower():
            continue
        if destino and destino.lower() not in str(data.get("ruta_destino", "")).lower():
            continue
        dt = data.get("fecha_salida")
        if hasattr(dt, 'date'):
            # Ocultar viajes pasados
            if dt.date() < today:
                continue
            if fecha and dt.date() != fecha.date():
                continue
        res.append(d)
    
    # Ordenar por fecha_salida en cliente
    res.sort(key=lambda x: x.to_dict().get("fecha_salida") or datetime.min)
    return res


# ----- VENTAS / ASIENTOS -----
def create_venta_doc(venta_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    ventas_collection(client).document(str(venta_id)).set(data)


def decrement_viaje_asientos(viaje_id: str, cantidad: int, client: Optional[firestore.Client] = None) -> None:
    """Disminuye asientos_disponibles del viaje en una transacción. Lanza excepción si no hay cupos."""
    db = _get_client(client)
    viaje_ref = db.collection('viajes').document(str(viaje_id))

    @firestore.transactional
    def _tx(tx: firestore.Transaction):
        snap = viaje_ref.get(transaction=tx)
        if not snap.exists:
            raise ValueError("Viaje no existe en Firestore")
        data = snap.to_dict() or {}
        disponibles = int(data.get('asientos_disponibles', 0))
        if disponibles < cantidad:
            raise ValueError("No hay suficientes asientos en Firestore")
        tx.update(viaje_ref, {
            'asientos_disponibles': disponibles - cantidad
        })

    _tx(db.transaction())


# ----- CONSULTAS DE VENTAS PARA REPORTES -----
def ventas_between(start: datetime, end: datetime, client: Optional[firestore.Client] = None):
    col = ventas_collection(client)
    q = col.where('fecha_compra', '>=', start).where('fecha_compra', '<', end).order_by('fecha_compra', direction=firestore.Query.DESCENDING)
    return list(q.stream())


def ventas_last_n_days(n: int, client: Optional[firestore.Client] = None):
    """Devuelve (labels_dd/mm, totals) para los últimos n días incluyendo hoy."""
    from datetime import timedelta
    today = datetime.utcnow().date()
    labels = []
    totals = []
    for i in range(n-1, -1, -1):
        day = today - timedelta(days=i)
        start = datetime(day.year, day.month, day.day)
        end = start + timedelta(days=1)
        docs = ventas_between(start, end, client)
        total_dia = sum(float(d.to_dict().get('total', 0)) for d in docs if d.to_dict().get('estado') == 'confirmado')
        labels.append(day.strftime('%d/%m'))
        totals.append(total_dia)
    return labels, totals


# ----- USUARIOS -----
def list_usuarios(client: Optional[firestore.Client] = None):
    return list(users_collection(client).stream())


def get_usuario_by_id(user_id: str, client: Optional[firestore.Client] = None):
    return users_collection(client).document(str(user_id)).get()


# ----- RUTAS -----
def list_rutas(client: Optional[firestore.Client] = None):
    return list(rutas_collection(client).stream())


# ----- VIAJES UTILS -----
def get_viaje_by_id(viaje_id: str, client: Optional[firestore.Client] = None):
    return viajes_collection(client).document(str(viaje_id)).get()


def update_viaje_fields(viaje_id: str, fields: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    viajes_collection(client).document(str(viaje_id)).update(fields)


def list_viajes_ordered(limit: int = 50, client: Optional[firestore.Client] = None):
    return list(viajes_collection(client).order_by('fecha_salida').limit(limit).stream())


def count_collection(col_name: str, client: Optional[firestore.Client] = None) -> int:
    # Firestore no tiene count() sin agregación; aproximamos leyendo ids en lotes pequeños si es necesario
    # Para colecciones pequeñas/medianas está bien; para grandes usar COUNT agregations (no en Admin SDK clásico)
    return sum(1 for _ in _get_client(client).collection(col_name).stream())


# ----- VENTAS POR USUARIO -----
def list_ventas_by_user(user_id: str, client: Optional[firestore.Client] = None):
    # Evitar índice compuesto: filtrar por usuario_id y ordenar en cliente
    docs = list(ventas_collection(client).where('usuario_id', '==', user_id).stream())
    docs.sort(key=lambda d: (d.to_dict() or {}).get('fecha_compra') or datetime.min, reverse=True)
    return docs


# ----- CONSULTAS (SOPORTE) -----
def consultas_collection(client: Optional[firestore.Client] = None):
    return _get_client(client).collection('consultas')


def create_consulta_doc(doc_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    consultas_collection(client).document(str(doc_id)).set(data)


def list_consultas_by_user(user_id: str, client: Optional[firestore.Client] = None):
    # Evitar índice compuesto: filtrar por usuario_id y ordenar en cliente
    docs = list(consultas_collection(client).where('usuario_id', '==', user_id).stream())
    docs.sort(key=lambda d: (d.to_dict() or {}).get('fecha_consulta') or datetime.min, reverse=True)
    return docs


def list_all_consultas(client: Optional[firestore.Client] = None):
    q = consultas_collection(client).order_by('fecha_consulta', direction=firestore.Query.DESCENDING)
    return list(q.stream())


def respond_consulta(consulta_id: str, respuesta: str, client: Optional[firestore.Client] = None) -> None:
    consultas_collection(client).document(str(consulta_id)).update({
        'respuesta': respuesta,
        'estado': 'respondida',
        'fecha_respuesta': datetime.utcnow(),
    })


def get_user_by_id(user_id: str, client: Optional[firestore.Client] = None):
    """Get user document by ID"""
    return users_collection(client).document(str(user_id)).get()


def update_user_profile(user_id: str, data: Dict[str, Any], client: Optional[firestore.Client] = None) -> None:
    """Update user profile data"""
    users_collection(client).document(str(user_id)).update(data)
