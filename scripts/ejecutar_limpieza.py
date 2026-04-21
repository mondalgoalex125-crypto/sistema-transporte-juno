#!/usr/bin/env python3
"""
Script para ejecutar la limpieza del sistema via API
"""

import requests
import json

def ejecutar_limpieza():
    """Ejecuta la limpieza del sistema via API"""
    
    print("JUNO EXPRESS - Limpieza del Sistema")
    print("=" * 50)
    
    # Confirmar
    respuesta = input("¿Estás seguro de eliminar TODAS las ventas y viajes? (escribe SI): ")
    
    if respuesta.upper() != 'SI':
        print("Operación cancelada")
        return
    
    try:
        # URL del servidor local
        url = "http://127.0.0.1:5000/admin/limpiar-sistema"
        
        print("\nEjecutando limpieza...")
        
        # Hacer petición POST (sin autenticación por simplicidad)
        response = requests.post(url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                print("\n✅ ¡Sistema limpiado exitosamente!")
                print(f"📊 Eliminadas: {data['eliminado']['ventas']} ventas")
                print(f"🚌 Eliminados: {data['eliminado']['viajes']} viajes") 
                print(f"💬 Eliminadas: {data['eliminado']['consultas']} consultas")
                print(f"👥 Conservados: {data['conservado']['usuarios']} usuarios")
                print(f"🛣️  Conservadas: {data['conservado']['rutas']} rutas")
                print(f"\n🎉 {data['message']}")
            else:
                print(f"❌ Error: {data.get('error', 'Error desconocido')}")
        else:
            print(f"❌ Error HTTP {response.status_code}: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Error: No se pudo conectar al servidor Flask")
        print("   Asegúrate de que el servidor esté ejecutándose en http://127.0.0.1:5000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    ejecutar_limpieza()
