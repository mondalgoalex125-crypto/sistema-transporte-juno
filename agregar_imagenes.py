#!/usr/bin/env python3
"""
Script para agregar las imágenes reales al sistema JUNO EXPRESS
"""

import os
import shutil

def agregar_imagenes():
    """Instrucciones para agregar las imágenes reales"""
    
    print("🖼️  JUNO EXPRESS - Agregar Imágenes Reales")
    print("=" * 50)
    
    images_dir = "static/images"
    
    print(f"\n📁 Directorio de imágenes: {images_dir}")
    
    required_images = {
        "bus-hero.jpg": "Imagen principal del bus (1920x1080px recomendado)",
        "chincha.jpg": "Imagen de Chincha - arquitectura colonial (800x600px)",
        "pisco.jpg": "Imagen de Pisco - playa y costa (800x600px)", 
        "ica.jpg": "Imagen de Ica - oasis y dunas (800x600px)"
    }
    
    print("\n🎯 Imágenes necesarias:")
    for filename, description in required_images.items():
        filepath = os.path.join(images_dir, filename)
        status = "✅ Existe" if os.path.exists(filepath) and os.path.getsize(filepath) > 0 else "❌ Falta"
        print(f"   {status} {filename} - {description}")
    
    print(f"\n📋 Instrucciones:")
    print(f"1. Guarda las imágenes reales en la carpeta: {os.path.abspath(images_dir)}")
    print(f"2. Usa exactamente estos nombres de archivo:")
    for filename in required_images.keys():
        print(f"   - {filename}")
    print(f"3. Formatos soportados: JPG, JPEG, PNG, WebP")
    print(f"4. Reinicia el servidor Flask para ver los cambios")
    
    print(f"\n🚀 Una vez agregadas las imágenes:")
    print(f"   - La página principal mostrará las imágenes reales")
    print(f"   - Los colores y gradientes actuarán como fallback")
    print(f"   - El diseño se verá profesional y atractivo")
    
    print(f"\n💡 Tip: Puedes usar herramientas como:")
    print(f"   - Photoshop/GIMP para redimensionar")
    print(f"   - TinyPNG para optimizar el tamaño")
    print(f"   - Unsplash/Pexels para imágenes de stock si es necesario")

if __name__ == "__main__":
    agregar_imagenes()
