"""
Sistema de Pagos Móviles para JUNO EXPRESS
Integración con Yape, Plin y otros métodos de pago móvil
"""

import requests
import json
import hashlib
import hmac
import uuid
from datetime import datetime, timedelta
from typing import Dict, Optional, Any
import logging
from flask import current_app

logger = logging.getLogger(__name__)

class MobilePaymentService:
    def __init__(self):
        self.yape_api_url = "https://api.yape.pe/v1"
        self.plin_api_url = "https://api.plin.pe/v1"
        self.yape_token = None
        self.plin_token = None
        
        # Configuración (en producción debería venir de variables de entorno)
        self.config = {
            'yape': {
                'client_id': 'yape_client_id',
                'client_secret': 'yape_client_secret',
                'merchant_id': 'juno_express_merchant',
                'webhook_secret': 'yape_webhook_secret'
            },
            'plin': {
                'client_id': 'plin_client_id', 
                'client_secret': 'plin_client_secret',
                'merchant_id': 'juno_express_merchant',
                'webhook_secret': 'plin_webhook_secret'
            }
        }
    
    def generate_payment_id(self) -> str:
        """Generar ID único para pago"""
        return f"JUNO_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
    
    def generate_signature(self, data: Dict, secret: str) -> str:
        """Generar firma HMAC para seguridad"""
        sorted_data = json.dumps(data, sort_keys=True, separators=(',', ':'))
        return hmac.new(
            secret.encode('utf-8'),
            sorted_data.encode('utf-8'),
            hashlib.sha256
        ).hexdigest()
    
    async def create_yape_payment(self, 
                                amount: float, 
                                phone_number: str,
                                user_id: str,
                                venta_id: str,
                                description: str = "Pago JUNO EXPRESS") -> Dict:
        """
        Crear pago con Yape
        """
        try:
            payment_id = self.generate_payment_id()
            
            payload = {
                'merchant_id': self.config['yape']['merchant_id'],
                'payment_id': payment_id,
                'amount': int(amount * 100),  # Yape trabaja con céntimos
                'currency': 'PEN',
                'phone_number': phone_number,
                'description': description,
                'callback_url': f"{current_app.config.get('BASE_URL', '')}/api/payments/yape/callback",
                'webhook_url': f"{current_app.config.get('BASE_URL', '')}/api/payments/yape/webhook",
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
                'metadata': {
                    'user_id': user_id,
                    'venta_id': venta_id,
                    'platform': 'juno_express'
                }
            }
            
            # Generar firma
            signature = self.generate_signature(payload, self.config['yape']['client_secret'])
            payload['signature'] = signature
            
            # Enviar petición a Yape API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.yape_token}'
            }
            
            response = requests.post(
                f"{self.yape_api_url}/payments",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'qr_code': result.get('qr_code'),
                    'expires_at': payload['expires_at'],
                    'payment_url': result.get('payment_url'),
                    'method': 'yape'
                }
            else:
                logger.error(f"Yape API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'Error al crear pago Yape',
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating Yape payment: {e}")
            return {
                'success': False,
                'error': 'Error al procesar pago Yape',
                'details': str(e)
            }
    
    async def create_plin_payment(self, 
                                amount: float, 
                                phone_number: str,
                                user_id: str,
                                venta_id: str,
                                description: str = "Pago JUNO EXPRESS") -> Dict:
        """
        Crear pago con Plin
        """
        try:
            payment_id = self.generate_payment_id()
            
            payload = {
                'merchant_id': self.config['plin']['merchant_id'],
                'payment_id': payment_id,
                'amount': int(amount * 100),  # Plin trabaja con céntimos
                'currency': 'PEN',
                'phone_number': phone_number,
                'description': description,
                'callback_url': f"{current_app.config.get('BASE_URL', '')}/api/payments/plin/callback",
                'webhook_url': f"{current_app.config.get('BASE_URL', '')}/api/payments/plin/webhook",
                'expires_at': (datetime.utcnow() + timedelta(minutes=15)).isoformat(),
                'metadata': {
                    'user_id': user_id,
                    'venta_id': venta_id,
                    'platform': 'juno_express'
                }
            }
            
            # Generar firma
            signature = self.generate_signature(payload, self.config['plin']['client_secret'])
            payload['signature'] = signature
            
            # Enviar petición a Plin API
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.plin_token}'
            }
            
            response = requests.post(
                f"{self.plin_api_url}/payments",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'payment_id': payment_id,
                    'qr_code': result.get('qr_code'),
                    'expires_at': payload['expires_at'],
                    'payment_url': result.get('payment_url'),
                    'method': 'plin'
                }
            else:
                logger.error(f"Plin API error: {response.status_code} - {response.text}")
                return {
                    'success': False,
                    'error': 'Error al crear pago Plin',
                    'details': response.text
                }
                
        except Exception as e:
            logger.error(f"Error creating Plin payment: {e}")
            return {
                'success': False,
                'error': 'Error al procesar pago Plin',
                'details': str(e)
            }
    
    def verify_yape_webhook(self, payload: Dict, signature: str) -> bool:
        """
        Verificar webhook de Yape
        """
        try:
            expected_signature = self.generate_signature(
                payload, 
                self.config['yape']['webhook_secret']
            )
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying Yape webhook: {e}")
            return False
    
    def verify_plin_webhook(self, payload: Dict, signature: str) -> bool:
        """
        Verificar webhook de Plin
        """
        try:
            expected_signature = self.generate_signature(
                payload, 
                self.config['plin']['webhook_secret']
            )
            return hmac.compare_digest(signature, expected_signature)
        except Exception as e:
            logger.error(f"Error verifying Plin webhook: {e}")
            return False
    
    async def check_payment_status(self, payment_id: str, method: str) -> Dict:
        """
        Verificar estado de pago
        """
        try:
            if method == 'yape':
                return await self._check_yape_status(payment_id)
            elif method == 'plin':
                return await self._check_plin_status(payment_id)
            else:
                return {'success': False, 'error': 'Método de pago no válido'}
        except Exception as e:
            logger.error(f"Error checking payment status: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _check_yape_status(self, payment_id: str) -> Dict:
        """Verificar estado de pago Yape"""
        try:
            headers = {
                'Authorization': f'Bearer {self.yape_token}'
            }
            
            response = requests.get(
                f"{self.yape_api_url}/payments/{payment_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'paid_at': result.get('paid_at'),
                    'transaction_id': result.get('transaction_id'),
                    'amount': result.get('amount') / 100  # Convertir a soles
                }
            else:
                return {'success': False, 'error': 'Error verificando pago'}
                
        except Exception as e:
            logger.error(f"Error checking Yape status: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _check_plin_status(self, payment_id: str) -> Dict:
        """Verificar estado de pago Plin"""
        try:
            headers = {
                'Authorization': f'Bearer {self.plin_token}'
            }
            
            response = requests.get(
                f"{self.plin_api_url}/payments/{payment_id}",
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'status': result.get('status'),
                    'paid_at': result.get('paid_at'),
                    'transaction_id': result.get('transaction_id'),
                    'amount': result.get('amount') / 100  # Convertir a soles
                }
            else:
                return {'success': False, 'error': 'Error verificando pago'}
                
        except Exception as e:
            logger.error(f"Error checking Plin status: {e}")
            return {'success': False, 'error': str(e)}
    
    async def refund_payment(self, payment_id: str, method: str, amount: float = None) -> Dict:
        """
        Procesar reembolso
        """
        try:
            if method == 'yape':
                return await self._refund_yape(payment_id, amount)
            elif method == 'plin':
                return await self._refund_plin(payment_id, amount)
            else:
                return {'success': False, 'error': 'Método de pago no válido'}
        except Exception as e:
            logger.error(f"Error processing refund: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _refund_yape(self, payment_id: str, amount: float = None) -> Dict:
        """Procesar reembolso Yape"""
        try:
            payload = {'payment_id': payment_id}
            if amount:
                payload['amount'] = int(amount * 100)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.yape_token}'
            }
            
            response = requests.post(
                f"{self.yape_api_url}/refunds",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'status': result.get('status')
                }
            else:
                return {'success': False, 'error': 'Error procesando reembolso'}
                
        except Exception as e:
            logger.error(f"Error processing Yape refund: {e}")
            return {'success': False, 'error': str(e)}
    
    async def _refund_plin(self, payment_id: str, amount: float = None) -> Dict:
        """Procesar reembolso Plin"""
        try:
            payload = {'payment_id': payment_id}
            if amount:
                payload['amount'] = int(amount * 100)
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.plin_token}'
            }
            
            response = requests.post(
                f"{self.plin_api_url}/refunds",
                json=payload,
                headers=headers,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'refund_id': result.get('refund_id'),
                    'status': result.get('status')
                }
            else:
                return {'success': False, 'error': 'Error procesando reembolso'}
                
        except Exception as e:
            logger.error(f"Error processing Plin refund: {e}")
            return {'success': False, 'error': str(e)}
    
    def get_payment_methods(self) -> Dict:
        """
        Obtener métodos de pago disponibles
        """
        return {
            'yape': {
                'name': 'Yape',
                'icon': '/static/images/yape-icon.png',
                'description': 'Paga instantáneamente con Yape',
                'fees': 0.0,  # Sin comisiones
                'limits': {
                    'min': 1.0,
                    'max': 500.0
                }
            },
            'plin': {
                'name': 'Plin',
                'icon': '/static/images/plin-icon.png',
                'description': 'Paga fácilmente con Plin',
                'fees': 0.0,  # Sin comisiones
                'limits': {
                    'min': 1.0,
                    'max': 500.0
                }
            }
        }
    
    def validate_phone_number(self, phone: str) -> bool:
        """
        Validar número de teléfono peruano
        """
        import re
        # Formato peruano: 9xxxxxxxx (9 dígitos empezando con 9)
        pattern = r'^9\d{8}$'
        return bool(re.match(pattern, phone))
    
    def format_amount(self, amount: float) -> str:
        """
        Formatear monto para mostrar
        """
        return f"S/. {amount:.2f}"
    
    async def get_payment_qr_code(self, payment_id: str, method: str) -> Optional[str]:
        """
        Obtener código QR para pago
        """
        try:
            status = await self.check_payment_status(payment_id, method)
            if status['success'] and status['status'] == 'pending':
                # Generar QR code (simulado para demo)
                return f"data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNkYPhfDwAChwGA60e6kgAAAABJRU5ErkJggg=="
            return None
        except Exception as e:
            logger.error(f"Error getting QR code: {e}")
            return None

# Instancia global del servicio
mobile_payment_service = MobilePaymentService()
