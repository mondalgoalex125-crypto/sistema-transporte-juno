"""
Sistema de Notificaciones Push para JUNO EXPRESS
Maneja notificaciones push, emails y SMS
"""

import json
import requests
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import firebase_admin
from firebase_admin import messaging
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class NotificationService:
    def __init__(self, firestore_db=None):
        self.firestore_db = firestore_db
        self.firebase_app = None
        
        # Inicializar Firebase Messaging si está disponible
        try:
            if firebase_admin.get_app():
                self.firebase_app = firebase_admin.get_app()
        except ValueError:
            logger.warning("Firebase Admin no inicializado para notificaciones push")
    
    async def send_push_notification(self, 
                                   user_id: str, 
                                   title: str, 
                                   body: str, 
                                   data: Optional[Dict] = None,
                                   image_url: Optional[str] = None) -> bool:
        """
        Enviar notificación push a un usuario específico
        """
        try:
            # Obtener tokens del usuario desde Firestore
            user_tokens = await self.get_user_tokens(user_id)
            
            if not user_tokens:
                logger.warning(f"No tokens found for user {user_id}")
                return False
            
            # Crear mensaje
            message = messaging.Message(
                notification=messaging.Notification(
                    title=title,
                    body=body,
                    image=image_url
                ),
                data=data or {},
                android=messaging.AndroidConfig(
                    priority='high',
                    notification=messaging.AndroidNotification(
                        icon='/static/images/bus-icon.png',
                        color='#FF8C00',
                        sound='default',
                        click_action='FLUTTER_NOTIFICATION_CLICK'
                    )
                ),
                apns=messaging.APNSConfig(
                    payload=messaging.APNSPayload(
                        aps=messaging.Aps(
                            sound='default',
                            badge=1,
                            content_available=True
                        )
                    )
                ),
                webpush=messaging.WebpushConfig(
                    notification=messaging.WebpushNotification(
                        icon='/static/images/bus-icon.png',
                        badge='/static/images/badge.png',
                        vibrate=[100, 50, 100],
                        actions=[
                            {
                                "action": "explore",
                                "title": "Ver Detalles"
                            },
                            {
                                "action": "close", 
                                "title": "Cerrar"
                            }
                        ]
                    )
                )
            )
            
            # Enviar a cada token
            success_count = 0
            failed_tokens = []
            
            for token in user_tokens:
                try:
                    message.token = token
                    response = messaging.send(message)
                    success_count += 1
                    logger.info(f"Push notification sent to {token}: {response}")
                except Exception as e:
                    failed_tokens.append(token)
                    logger.error(f"Failed to send push to {token}: {e}")
            
            # Limpiar tokens fallidos
            if failed_tokens:
                await self.remove_invalid_tokens(user_id, failed_tokens)
            
            return success_count > 0
            
        except Exception as e:
            logger.error(f"Error sending push notification: {e}")
            return False
    
    async def send_bulk_notification(self, 
                                    user_ids: List[str], 
                                    title: str, 
                                    body: str, 
                                    data: Optional[Dict] = None) -> int:
        """
        Enviar notificación a múltiples usuarios
        """
        success_count = 0
        
        for user_id in user_ids:
            if await self.send_push_notification(user_id, title, body, data):
                success_count += 1
        
        return success_count
    
    async def get_user_tokens(self, user_id: str) -> List[str]:
        """
        Obtener tokens de notificación de un usuario
        """
        try:
            if not self.firestore_db:
                return []
            
            user_doc = self.firestore_db.collection('users').document(user_id).get()
            if user_doc.exists:
                user_data = user_doc.to_dict()
                return user_data.get('notification_tokens', [])
            return []
        except Exception as e:
            logger.error(f"Error getting user tokens: {e}")
            return []
    
    async def register_token(self, user_id: str, token: str) -> bool:
        """
        Registrar token de notificación para un usuario
        """
        try:
            if not self.firestore_db:
                return False
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                tokens = user_data.get('notification_tokens', [])
                
                # Evitar duplicados
                if token not in tokens:
                    tokens.append(token)
                    user_ref.update({
                        'notification_tokens': tokens,
                        'last_token_update': datetime.utcnow()
                    })
            else:
                # Crear documento de usuario si no existe
                user_ref.set({
                    'notification_tokens': [token],
                    'last_token_update': datetime.utcnow()
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Error registering token: {e}")
            return False
    
    async def remove_invalid_tokens(self, user_id: str, invalid_tokens: List[str]) -> bool:
        """
        Remover tokens inválidos de un usuario
        """
        try:
            if not self.firestore_db:
                return False
            
            user_ref = self.firestore_db.collection('users').document(user_id)
            user_doc = user_ref.get()
            
            if user_doc.exists:
                user_data = user_doc.to_dict()
                tokens = user_data.get('notification_tokens', [])
                
                # Filtrar tokens inválidos
                valid_tokens = [token for token in tokens if token not in invalid_tokens]
                
                user_ref.update({
                    'notification_tokens': valid_tokens,
                    'last_token_update': datetime.utcnow()
                })
            
            return True
            
        except Exception as e:
            logger.error(f"Error removing invalid tokens: {e}")
            return False
    
    def send_travel_reminder(self, user_id: str, viaje_data: Dict) -> bool:
        """
        Enviar recordatorio de viaje
        """
        title = "Recordatorio de Viaje - JUNO EXPRESS"
        body = f"Tu viaje a {viaje_data.get('destino')} sale en 2 horas. ¡No te quedes!"
        
        data = {
            "type": "travel_reminder",
            "viaje_id": viaje_data.get('id'),
            "origen": viaje_data.get('origen'),
            "destino": viaje_data.get('destino'),
            "fecha_salida": viaje_data.get('fecha_salida'),
            "hora_salida": viaje_data.get('hora_salida')
        }
        
        return self.send_push_notification(user_id, title, body, data)
    
    def send_booking_confirmation(self, user_id: str, booking_data: Dict) -> bool:
        """
        Enviar confirmación de reserva
        """
        title = "Reserva Confirmada - JUNO EXPRESS"
        body = f"Tu reserva a {booking_data.get('destino')} está confirmada. Boletos: {booking_data.get('cantidad_boletos')}"
        
        data = {
            "type": "booking_confirmation",
            "venta_id": booking_data.get('venta_id'),
            "viaje_id": booking_data.get('viaje_id'),
            "origen": booking_data.get('origen'),
            "destino": booking_data.get('destino'),
            "cantidad_boletos": str(booking_data.get('cantidad_boletos')),
            "total": str(booking_data.get('total'))
        }
        
        return self.send_push_notification(user_id, title, body, data)
    
    def send_payment_notification(self, user_id: str, payment_data: Dict) -> bool:
        """
        Enviar notificación de pago
        """
        title = "Pago Recibido - JUNO EXPRESS"
        body = f"Tu pago de S/. {payment_data.get('monto')} ha sido procesado exitosamente"
        
        data = {
            "type": "payment_confirmation",
            "payment_id": payment_data.get('payment_id'),
            "monto": str(payment_data.get('monto')),
            "metodo": payment_data.get('metodo'),
            "venta_id": payment_data.get('venta_id')
        }
        
        return self.send_push_notification(user_id, title, body, data)
    
    def send_route_update(self, user_ids: List[str], route_data: Dict) -> int:
        """
        Enviar actualización de ruta a múltiples usuarios
        """
        title = "Actualización de Ruta - JUNO EXPRESS"
        body = f"La ruta {route_data.get('origen')} - {route_data.get('destino')} ha sido actualizada"
        
        data = {
            "type": "route_update",
            "ruta_id": route_data.get('ruta_id'),
            "origen": route_data.get('origen'),
            "destino": route_data.get('destino'),
            "cambio": route_data.get('cambio')
        }
        
        return self.send_bulk_notification(user_ids, title, body, data)
    
    def send_promotional_notification(self, user_ids: List[str], promo_data: Dict) -> int:
        """
        Enviar notificación promocional
        """
        title = promo_data.get('title', 'Oferta Especial - JUNO EXPRESS')
        body = promo_data.get('body', 'Descubre nuestras ofertas especiales')
        
        data = {
            "type": "promotion",
            "promo_id": promo_data.get('promo_id'),
            "discount": str(promo_data.get('discount', '')),
            "valid_until": promo_data.get('valid_until', ''),
            "code": promo_data.get('code', '')
        }
        
        return self.send_bulk_notification(user_ids, title, body, data)
    
    def schedule_notification(self, 
                             user_id: str, 
                             title: str, 
                             body: str, 
                             scheduled_time: datetime,
                             data: Optional[Dict] = None) -> str:
        """
        Programar notificación para enviar más tarde
        """
        try:
            if not self.firestore_db:
                return ""
            
            notification_id = f"notif_{int(datetime.utcnow().timestamp())}"
            
            notification_data = {
                'user_id': user_id,
                'title': title,
                'body': body,
                'data': data or {},
                'scheduled_time': scheduled_time,
                'status': 'scheduled',
                'created_at': datetime.utcnow()
            }
            
            self.firestore_db.collection('scheduled_notifications').document(notification_id).set(notification_data)
            
            return notification_id
            
        except Exception as e:
            logger.error(f"Error scheduling notification: {e}")
            return ""
    
    async def send_scheduled_notifications(self) -> int:
        """
        Enviar notificaciones programadas
        """
        try:
            if not self.firestore_db:
                return 0
            
            now = datetime.utcnow()
            scheduled_docs = self.firestore_db.collection('scheduled_notifications')\
                .where('scheduled_time', '<=', now)\
                .where('status', '==', 'scheduled')\
                .get()
            
            sent_count = 0
            
            for doc in scheduled_docs:
                notification_data = doc.to_dict()
                
                # Enviar notificación
                success = await self.send_push_notification(
                    notification_data['user_id'],
                    notification_data['title'],
                    notification_data['body'],
                    notification_data.get('data')
                )
                
                if success:
                    # Marcar como enviada
                    doc.reference.update({
                        'status': 'sent',
                        'sent_at': now
                    })
                    sent_count += 1
                else:
                    # Marcar como fallida
                    doc.reference.update({
                        'status': 'failed',
                        'failed_at': now
                    })
            
            return sent_count
            
        except Exception as e:
            logger.error(f"Error sending scheduled notifications: {e}")
            return 0

# Instancia global del servicio
notification_service = NotificationService()
