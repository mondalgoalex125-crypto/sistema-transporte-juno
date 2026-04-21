#!/usr/bin/env python3
"""
Script simple para limpiar el sistema JUNO EXPRESS
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import firebase_admin
from firebase_admin import credentials, firestore

def limpiar_sistema():
    print("Iniciando limpieza del sistema JUNO EXPRESS...")
    
    try:
        # Inicializar Firebase si no esta inicializado
        if not firebase_admin._apps:
            cred_path = os.path.join(os.path.dirname(__file__), '..', 'juno-express-firebase-adminsdk-vhgr8-d4c4c8a3c9.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("Firebase inicializado con credenciales")
            else:
                firebase_admin.initialize_app()
                print("Firebase inicializado con credenciales por defecto")
        
        db = firestore.client()
        print("Conectado a Firestore")
    except Exception as e:
        print(f"Error: No se pudo conectar a Firestore: {e}")
        return False
    
    try:
        # 1. Eliminar todas las ventas
        print("\nEliminando todas las ventas...")
        ventas_ref = db.collection('ventas')
        ventas_docs = list(ventas_ref.stream())
        ventas_count = len(ventas_docs)
        
        for doc in ventas_docs:
            doc.reference.delete()
            
        print(f"Eliminadas {ventas_count} ventas")
        
        # 2. Eliminar todos los viajes
        print("\nEliminando todos los viajes...")
        viajes_ref = db.collection('viajes')
        viajes_docs = list(viajes_ref.stream())
        viajes_count = len(viajes_docs)
        
        for doc in viajes_docs:
            doc.reference.delete()
            
        print(f"Eliminados {viajes_count} viajes")
        
        # 3. Eliminar consultas
        print("\nEliminando consultas...")
        consultas_ref = db.collection('consultas')
        consultas_docs = list(consultas_ref.stream())
        consultas_count = len(consultas_docs)
        
        for doc in consultas_docs:
            doc.reference.delete()
            
        print(f"Eliminadas {consultas_count} consultas")
        
        # Mostrar resumen
        print(f"\nSistema limpiado exitosamente!")
        print(f"Ventas eliminadas: {ventas_count}")
        print(f"Viajes eliminados: {viajes_count}")
        print(f"Consultas eliminadas: {consultas_count}")
        
        # Verificar lo que se mantiene
        usuarios_count = len(list(db.collection('usuarios').stream()))
        rutas_count = len(list(db.collection('rutas').stream()))
        
        print(f"\nConservado:")
        print(f"Usuarios: {usuarios_count}")
        print(f"Rutas: {rutas_count}")
        
        print("\nEl sistema esta listo para empezar de cero!")
        return True
        
    except Exception as e:
        print(f"Error durante la limpieza: {e}")
        return False

if __name__ == "__main__":
    print("JUNO EXPRESS - Limpiador del Sistema")
    print("=" * 50)
    
    respuesta = input("Estas seguro de eliminar TODAS las ventas y viajes? (escribe SI): ")
    
    if respuesta.upper() == 'SI':
        if limpiar_sistema():
            print("\nListo! Tu sistema esta limpio y listo para usar")
        else:
            print("\nHubo un error durante la limpieza")
    else:
        print("\nOperacion cancelada")
