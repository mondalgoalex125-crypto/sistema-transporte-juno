"""
Sincronización histórica de ventas desde SQL a Firestore y ajuste de asientos en viajes.
Uso:
    python scripts/sync_firestore.py [--mode sql_to_firestore|firestore_repair]

Requisitos:
- Debes tener configuradas las credenciales de Firebase Admin (como en app.py).
- Ejecuta desde la raíz del proyecto (donde está app.py).
"""
from __future__ import annotations

import sys
from collections import defaultdict
from datetime import datetime
import argparse
import os

# Asegurar imports relativos al proyecto
try:
    # Añadir el directorio padre (raíz del proyecto) al sys.path
    CURRENT_DIR = os.path.dirname(__file__)
    PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DIR, os.pardir))
    if PROJECT_ROOT not in sys.path:
        sys.path.insert(0, PROJECT_ROOT)
    # Importa la app para inicializar Firebase y el contexto de SQLAlchemy
    from app import app, db, Venta, Viaje, Ruta, firestore_db
    from services.firestore_repo import (
        create_venta_doc,
        decrement_viaje_asientos,
    )
except Exception as e:
    print(f"Error importando app y servicios: {e}")
    sys.exit(1)


def sync_ventas_y_asientos() -> None:
    if firestore_db is None:
        print("Firestore no está inicializado. Aborta.")
        sys.exit(2)

    with app.app_context():
        print("Leyendo ventas desde SQL...")
        ventas_sql = Venta.query.order_by(Venta.id.asc()).all()
        print(f"Ventas encontradas en SQL: {len(ventas_sql)}")

        # Acumulador por viaje para ajuste de asientos
        vendidos_por_viaje = defaultdict(int)

        # Primero subimos ventas (idempotente: actualiza si existe)
        subidas = 0
        errores = 0
        for v in ventas_sql:
            data = {
                'usuario_id': v.usuario_id,
                'viaje_id': v.viaje_id,
                'cantidad_boletos': v.cantidad_boletos,
                'total': float(v.total),
                'fecha_compra': v.fecha_compra or datetime.utcnow(),
                'estado': v.estado,
                'metodo_pago': v.metodo_pago,
            }
            try:
                create_venta_doc(v.id, data, firestore_db)
                subidas += 1
                if v.estado == 'confirmado':
                    vendidos_por_viaje[v.viaje_id] += int(v.cantidad_boletos or 0)
            except Exception as e:
                errores += 1
                print(f"Error subiendo venta {v.id} a Firestore: {e}")

        print(f"Ventas subidas/actualizadas en Firestore: {subidas}. Errores: {errores}")

        # Luego, ajustar asientos por viaje según ventas confirmadas
        print("Ajustando asientos en viajes (Firestore)...")
        ajustados = 0
        fallas_ajuste = 0
        for viaje_id, vendidos in vendidos_por_viaje.items():
            # Obtenemos totales desde SQL (fuente actual) para calcular disponibles
            viaje_sql = Viaje.query.get(viaje_id)
            if not viaje_sql:
                print(f"Viaje {viaje_id} no existe en SQL; se intenta solo decremento relativo")
                # Como fallback, intentamos decrementar relativo
                try:
                    decrement_viaje_asientos(viaje_id, vendidos, firestore_db)
                    ajustados += 1
                except Exception as e:
                    fallas_ajuste += 1
                    print(f"Error ajustando (relativo) viaje {viaje_id}: {e}")
                continue

            # Calcular asientos_disponibles = asientos_totales - vendidos
            try:
                # Intento transaccional: leer doc, calcular y setear valor absoluto
                doc_ref = firestore_db.collection('viajes').document(str(viaje_id))
                snap = doc_ref.get()
                if not snap.exists:
                    print(f"Doc viaje {viaje_id} no existe en Firestore, se crea uno mínimo para ajustar.")
                    # Crear con info básica de SQL
                    ruta = Ruta.query.get(viaje_sql.ruta_id)
                    doc_ref.set({
                        'ruta_id': viaje_sql.ruta_id,
                        'ruta_origen': getattr(ruta, 'origen', None),
                        'ruta_destino': getattr(ruta, 'destino', None),
                        'precio': getattr(ruta, 'precio', None),
                        'fecha_salida': viaje_sql.fecha_salida,
                        'hora_salida': viaje_sql.hora_salida,
                        'asientos_totales': viaje_sql.asientos_totales,
                        'asientos_disponibles': max(0, int(viaje_sql.asientos_totales) - int(vendidos)),
                        'estado': viaje_sql.estado,
                    })
                else:
                    data = snap.to_dict() or {}
                    totales = int(data.get('asientos_totales') or viaje_sql.asientos_totales or 0)
                    disponibles = max(0, totales - int(vendidos))
                    doc_ref.update({'asientos_disponibles': disponibles})
                ajustados += 1
            except Exception as e:
                fallas_ajuste += 1
                print(f"Error ajustando asientos del viaje {viaje_id}: {e}")

        print(f"Viajes ajustados: {ajustados}. Fallas de ajuste: {fallas_ajuste}")
        print("Sincronización histórica completada.")


def firestore_repair() -> None:
    """Recalcula asientos_disponibles usando SOLO datos en Firestore.

    - Agrupa ventas confirmadas en Firestore por viaje_id.
    - Recorre viajes y actualiza asientos_disponibles = asientos_totales - vendidos.
    - No requiere SQL. Útil si ya operas 100% en Firestore.
    """
    if firestore_db is None:
        print("Firestore no está inicializado. Aborta.")
        sys.exit(2)

    print("Leyendo ventas (Firestore) para agregación...")
    ventas_docs = list(firestore_db.collection('ventas').stream())
    vendidos_por_viaje = defaultdict(int)
    for d in ventas_docs:
        data = d.to_dict() or {}
        if data.get('estado') == 'confirmado':
            viaje_id = data.get('viaje_id')
            vendidos_por_viaje[str(viaje_id)] += int(data.get('cantidad_boletos') or 0)

    print(f"Viajes con ventas registradas: {len(vendidos_por_viaje)}")
    print("Ajustando asientos en 'viajes' (Firestore)...")
    ajustados = 0
    fallas = 0
    viajes_docs = list(firestore_db.collection('viajes').stream())
    for v in viajes_docs:
        vid = v.id
        data = v.to_dict() or {}
        totales = int(data.get('asientos_totales') or 0)
        if totales <= 0:
            continue
        vendidos = int(vendidos_por_viaje.get(str(vid), 0))
        disponibles = max(0, totales - vendidos)
        try:
            v.reference.update({'asientos_disponibles': disponibles})
            ajustados += 1
        except Exception as e:
            fallas += 1
            print(f"Error actualizando viaje {vid}: {e}")

    print(f"Ajustes completados. Viajes actualizados: {ajustados}. Fallas: {fallas}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Sincronización histórica y reparación en Firestore')
    parser.add_argument('--mode', choices=['sql_to_firestore', 'firestore_repair'], default='sql_to_firestore')
    args = parser.parse_args()

    if args.mode == 'sql_to_firestore':
        sync_ventas_y_asientos()
    else:
        firestore_repair()
