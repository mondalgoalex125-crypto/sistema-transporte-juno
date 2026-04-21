#!/usr/bin/env python3
"""
Script para limpiar/resetear el sistema JUNO EXPRESS
Elimina ventas, viajes y consultas para empezar de cero
Mantiene usuarios y rutas básicas
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Importar la configuración de Firebase desde app.py
import firebase_admin
from firebase_admin import credentials, firestore

def limpiar_sistema():
    """Limpia todas las colecciones del sistema excepto usuarios y rutas"""
    
    print("🧹 Iniciando limpieza del sistema JUNO EXPRESS...")
    
    try:
        # Inicializar Firebase si no está inicializado
        if not firebase_admin._apps:
            # Usar las mismas credenciales que app.py
            cred_path = os.path.join(os.path.dirname(__file__), '..', 'juno-express-firebase-adminsdk-vhgr8-d4c4c8a3c9.json')
            if os.path.exists(cred_path):
                cred = credentials.Certificate(cred_path)
                firebase_admin.initialize_app(cred)
                print("✅ Firebase inicializado con credenciales")
            else:
                firebase_admin.initialize_app()
                print("✅ Firebase inicializado con credenciales por defecto")
        
        # Obtener cliente de Firestore
        db = firestore.client()
        print("✅ Conectado a Firestore")
    except Exception as e:
        print(f"❌ Error: No se pudo conectar a Firestore: {e}")
        return False
    
    try:
        # 1. Eliminar todas las ventas
        print("\n📊 Eliminando todas las ventas...")
        ventas_ref = db.collection('ventas')
        ventas_docs = ventas_ref.stream()
        ventas_count = 0
        
        for doc in ventas_docs:
            doc.reference.delete()
            ventas_count += 1
            
        print(f"✅ Eliminadas {ventas_count} ventas")
        
        # 2. Eliminar todos los viajes programados
        print("\n🚌 Eliminando todos los viajes programados...")
        viajes_ref = db.collection('viajes')
        viajes_docs = viajes_ref.stream()
        viajes_count = 0
        
        for doc in viajes_docs:
            doc.reference.delete()
            viajes_count += 1
            
        print(f"✅ Eliminados {viajes_count} viajes")
        
        # 3. Eliminar todas las consultas de atención al cliente
        print("\n💬 Eliminando consultas de atención al cliente...")
        consultas_ref = db.collection('consultas')
        consultas_docs = consultas_ref.stream()
        consultas_count = 0
        
        for doc in consultas_docs:
            doc.reference.delete()
            consultas_count += 1
            
        print(f"✅ Eliminadas {consultas_count} consultas")
        
        # 4. Mostrar lo que se mantiene
        print("\n🔒 Manteniendo intacto:")
        
        # Contar usuarios
        usuarios_ref = db.collection('usuarios')
        usuarios_count = len(list(usuarios_ref.stream()))
        print(f"   👥 {usuarios_count} usuarios (admin y pasajeros)")
        
        # Contar rutas
        rutas_ref = db.collection('rutas')
        rutas_count = len(list(rutas_ref.stream()))
        print(f"   🛣️  {rutas_count} rutas configuradas")
        
        print(f"\n🎉 ¡Sistema limpiado exitosamente!")
        print(f"📈 Resumen:")
        print(f"   • Ventas eliminadas: {ventas_count}")
        print(f"   • Viajes eliminados: {viajes_count}")
        print(f"   • Consultas eliminadas: {consultas_count}")
        print(f"   • Usuarios conservados: {usuarios_count}")
        print(f"   • Rutas conservadas: {rutas_count}")
        
        print(f"\n✨ El sistema está listo para empezar de cero")
        print(f"🚀 Puedes crear nuevos viajes y empezar a vender boletos")
        
        return True
        
    except Exception as e:
        print(f"❌ Error durante la limpieza: {e}")
        return False

def confirmar_limpieza():
    """Pide confirmación antes de limpiar"""
    print("⚠️  ADVERTENCIA: Esta acción eliminará TODOS los datos de:")
    print("   • 📊 Ventas realizadas")
    print("   • 🚌 Viajes programados") 
    print("   • 💬 Consultas de clientes")
    print()
    print("🔒 Se mantendrán:")
    print("   • 👥 Usuarios (admin y pasajeros)")
    print("   • 🛣️  Rutas configuradas")
    print()
    
    respuesta = input("¿Estás seguro de que quieres continuar? (escribe 'SI' para confirmar): ")
    
    if respuesta.upper() == 'SI':
        return True
    else:
        print("❌ Operación cancelada")
        return False

if __name__ == "__main__":
    print("🧹 JUNO EXPRESS - Limpiador del Sistema")
    print("=" * 50)
    
    if confirmar_limpieza():
        if limpiar_sistema():
            print("\n🎯 ¡Listo! Tu sistema está limpio y listo para usar")
        else:
            print("\n💥 Hubo un error durante la limpieza")
    else:
        print("\n👋 Operación cancelada por el usuario")
