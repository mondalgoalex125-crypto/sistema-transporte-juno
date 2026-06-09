"""
Chatbot de Soporte para JUNO EXPRESS
Sistema inteligente de atención al cliente 24/7
"""

import json
import re
import datetime
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

class IntentType(Enum):
    GREETING = "greeting"
    BOOKING = "booking"
    PAYMENT = "payment"
    SCHEDULE = "schedule"
    ROUTES = "routes"
    PRICES = "prices"
    REFUND = "refund"
    SUPPORT = "support"
    COMPLAINT = "complaint"
    FAQ = "faq"
    UNKNOWN = "unknown"

@dataclass
class ChatIntent:
    intent: IntentType
    confidence: float
    entities: Dict[str, Any]
    response_template: str

@dataclass
class ChatMessage:
    user_id: str
    message: str
    timestamp: datetime.datetime
    intent: Optional[ChatIntent] = None
    response: Optional[str] = None
    session_id: str = ""

class ChatbotService:
    def __init__(self, firestore_db=None):
        self.firestore_db = firestore_db
        self.session_contexts = {}
        
        # Patrones de reconocimiento de intents
        self.intent_patterns = {
            IntentType.GREETING: [
                r'\b(hola|buenos días|buenas tardes|buenas noches|hey|hi|hello)\b',
                r'\b(saludos|qué tal|cómo estás)\b'
            ],
            IntentType.BOOKING: [
                r'\b(reservar|reserva|comprar|boleto|ticket|pasaje)\b',
                r'\b(quiero|necesito|deseo)\s+(reservar|comprar)\b',
                r'\b(hacer|realizar)\s+(una|una)\s+reserva\b'
            ],
            IntentType.PAYMENT: [
                r'\b(pagar|pago|precio|costo|tarifa)\b',
                r'\b(yape|plin|tarjeta|visa|mastercard)\b',
                r'\b(métodos|formas)\s+de\s+pago\b'
            ],
            IntentType.SCHEDULE: [
                r'\b(horario|horarios|salida|llegada|tiempo)\b',
                r'\b(¿cuándo|cuando)\s+(sale|llega|parte)\b',
                r'\b(¿a qué|a que)\s+(hora|horas)\b'
            ],
            IntentType.ROUTES: [
                r'\b(ruta|rutas|destino|destinos|trayecto)\b',
                r'\b(¿a dónde|a donde)\s+(van|viajan|llegan)\b',
                r'\b(¿desde dónde|desde donde)\s+(sale|parte)\b'
            ],
            IntentType.PRICES: [
                r'\b(¿cuánto|cuanto)\s+(cuesta|vale|costa)\b',
                r'\b(precio|precios|tarifa|tarifas)\b',
                r'\b(valor|costo)\b'
            ],
            IntentType.REFUND: [
                r'\b(devolver|devolución|reembolso|cancelar)\b',
                r'\b(devolución|reembolso)\s+de\s+dinero\b',
                r'\b(quiero|necesito)\s+(cancelar|devolver)\b'
            ],
            IntentType.SUPPORT: [
                r'\b(ayuda|soporte|asistencia|problema)\b',
                r'\b(¿me puedes ayudar|necesito ayuda)\b',
                r'\b(atención|cliente|servicio)\b'
            ],
            IntentType.COMPLAINT: [
                r'\b(queja|reclamo|mal|problema|error)\b',
                r'\b(estoy molesto|no estoy feliz|insatisfecho)\b',
                r'\b(mal servicio|mal trato|mala atención)\b'
            ]
        }
        
        # Plantillas de respuesta
        self.response_templates = {
            IntentType.GREETING: [
                "¡Hola! Soy el asistente virtual de JUNO EXPRESS. ¿En qué puedo ayudarte hoy?",
                "¡Bienvenido a JUNO EXPRESS! ¿Qué información necesitas sobre nuestros servicios?",
                "¡Saludos! Estoy aquí para ayudarte con tus viajes. ¿Qué buscas?"
            ],
            IntentType.BOOKING: [
                "Para hacer una reserva, necesito saber: ¿desde dónde viajas y hacia dónde? ¿Qué fecha prefieres?",
                "Puedo ayudarte a reservar. Por favor, indícame tu origen, destino y fecha de viaje.",
                "¡Claro que sí! Para reservar necesito: origen, destino y fecha. ¿Cuáles son tus planes?"
            ],
            IntentType.PAYMENT: [
                "Aceptamos varios métodos de pago: Yape, Plin, tarjetas Visa/Mastercard y efectivo en nuestras agencias.",
                "Puedes pagar de forma segura con Yape, Plin o tarjeta de crédito/débito. ¿Cuál prefieres?",
                "Te ofrecemos pagos móviles instantáneos con Yape y Plin, además de tarjetas y efectivo."
            ],
            IntentType.SCHEDULE: [
                "Nuestros horarios varían según la ruta. ¿Podrías indicarme origen y destino para darte información precisa?",
                "Para darte los horarios exactos, necesito saber tu ruta específica. ¿Desde dónde hacia dónde?",
                "Los horarios dependen del destino. ¿Cuál es tu ruta de interés?"
            ],
            IntentType.ROUTES: [
                "JUNO EXPRESS cubre rutas como Chincha-Pisco, Chincha-Ica, Pisco-Ica y más. ¿Qué ruta te interesa?",
                "Operamos principalmente en la costa: Chincha, Pisco, Ica, Barrio Chino. ¿A dónde quieres viajar?",
                "Nuestras rutas principales conectan Chincha, Pisco, Ica y Barrio Chino. ¿Cuál es tu destino?"
            ],
            IntentType.PRICES: [
                "Nuestros precios varían según la ruta: Chincha-Pisco S/.5.00, Chincha-Ica S/.10.00, Pisco-Ica S/.8.00. ¿Qué ruta consultas?",
                "Las tarifas van desde S/.5.00 hasta S/.10.00 dependiendo de la distancia. ¿Cuál es tu ruta?",
                "Te puedo dar precios exactos si me dices tu origen y destino. ¿Cuál es tu viaje?"
            ],
            IntentType.REFUND: [
                "Para devoluciones, puedes contactarnos al 988049035 o visitar nuestra agencia. ¿Cuál es el motivo de tu solicitud?",
                "Las devoluciones se procesan según nuestras políticas. ¿Podrías explicarme tu situación?",
                "Entiendo. Para ayudarte con una devolución, necesito más detalles sobre tu reserva. ¿Tienes el número de boleto?"
            ],
            IntentType.SUPPORT: [
                "Estoy aquí para ayudarte. ¿Cuál es tu consulta o problema específico?",
                "Puedo asistirte con reservas, horarios, pagos y más. ¿Qué necesitas saber?",
                "¡Claro! Soy tu asistente virtual. ¿En qué puedo ayudarte hoy?"
            ],
            IntentType.COMPLAINT: [
                "Lamento escuchar eso. Quiero ayudarte a resolver tu situación. ¿Podrías darme más detalles?",
                "Entiendo tu frustración. Permíteme ayudarte a solucionar esto. ¿Qué pasó exactamente?",
                "Aprecio que me informes. Para ayudarte mejor, necesito entender completamente el problema."
            ]
        }
        
        # Base de conocimiento FAQ
        self.faq_database = {
            "equipaje": {
                "question": "¿Puedo llevar equipaje?",
                "answer": "Sí, puedes llevar 1 maleta de mano y 1 equipaje de bodega sin costo adicional. El equipaje de mano no debe exceder 5kg y el de bodega 20kg."
            },
            "mascotas": {
                "question": "¿Puedo viajar con mascotas?",
                "answer": "Solo se permiten mascotas pequeñas en transportín, con un costo adicional de S/.10.00. Deben presentar certificado de salud."
            },
            "niños": {
                "question": "¿Hay descuentos para niños?",
                "answer": "Sí, niños de 3-11 años pagan el 50% del tarifa. Menores de 3 años viajan gratis si no ocupan asiento."
            },
            "cancelación": {
                "question": "¿Cómo cancelo mi reserva?",
                "answer": "Puedes cancelar hasta 2 horas antes del viaje con reembolso del 80%. Después de ese tiempo no hay reembolso."
            },
            "asientos": {
                "question": "¿Puedo elegir mi asiento?",
                "answer": "Sí, al reservar puedes seleccionar tu asiento preferido. Los asientos VIP tienen un costo adicional de S/.5.00."
            }
        }

    def detect_intent(self, message: str) -> ChatIntent:
        """
        Detectar el intent del mensaje del usuario
        """
        message_lower = message.lower()
        best_intent = IntentType.UNKNOWN
        best_confidence = 0.0
        entities = {}
        
        # Buscar coincidencias de patrones
        for intent, patterns in self.intent_patterns.items():
            confidence = 0.0
            matched_patterns = []
            
            for pattern in patterns:
                if re.search(pattern, message_lower, re.IGNORECASE):
                    confidence += 1.0
                    matched_patterns.append(pattern)
            
            if confidence > best_confidence:
                best_confidence = confidence / len(patterns)  # Normalizar
                best_intent = intent
                
                # Extraer entidades básicas
                entities = self.extract_entities(message_lower, intent)
        
        # Buscar en FAQ si es unknown
        if best_intent == IntentType.UNKNOWN:
            faq_match = self.search_faq(message_lower)
            if faq_match:
                best_intent = IntentType.FAQ
                entities['faq_topic'] = faq_match
        
        # Seleccionar plantilla de respuesta
        response_template = self.get_response_template(best_intent, entities)
        
        return ChatIntent(
            intent=best_intent,
            confidence=best_confidence,
            entities=entities,
            response_template=response_template
        )

    def extract_entities(self, message: str, intent: IntentType) -> Dict[str, Any]:
        """
        Extraer entidades del mensaje
        """
        entities = {}
        
        # Extraer ciudades/destinos
        cities = ['chincha', 'pisco', 'ica', 'barrio chino', 'yauca']
        for city in cities:
            if city in message:
                if 'origin' not in entities:
                    entities['origin'] = city
                else:
                    entities['destination'] = city
        
        # Extraer fechas
        date_patterns = [
            r'\b(hoy|mañana|pasado mañana)\b',
            r'\b(\d{1,2})[/\-](\d{1,2})[/\-](\d{4})\b',
            r'\b(\d{1,2})\s+de\s+(\w+)\s+de\s+(\d{4})\b'
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, message)
            if match:
                entities['date'] = match.group()
                break
        
        # Extraer cantidades/dinero
        money_pattern = r'\bs/\s*(\d+(?:\.\d+)?)\b'
        money_match = re.search(money_pattern, message)
        if money_match:
            entities['amount'] = float(money_match.group(1))
        
        # Extraer números de teléfono
        phone_pattern = r'\b9\d{8}\b'
        phone_match = re.search(phone_pattern, message)
        if phone_match:
            entities['phone'] = phone_match.group()
        
        return entities

    def search_faq(self, message: str) -> Optional[str]:
        """
        Buscar en base de conocimiento FAQ
        """
        message_words = set(message.split())
        
        best_match = None
        best_score = 0
        
        for topic, faq_data in self.faq_database.items():
            question_words = set(faq_data['question'].lower().split())
            answer_words = set(faq_data['answer'].lower().split())
            
            # Calcular similitud
            question_score = len(message_words & question_words) / len(message_words | question_words)
            answer_score = len(message_words & answer_words) / len(message_words | answer_words)
            
            total_score = (question_score + answer_score) / 2
            
            if total_score > best_score and total_score > 0.3:  # Umbral mínimo
                best_score = total_score
                best_match = topic
        
        return best_match

    def get_response_template(self, intent: IntentType, entities: Dict[str, Any]) -> str:
        """
        Obtener plantilla de respuesta personalizada
        """
        templates = self.response_templates.get(intent, ["No entiendo tu pregunta. ¿Podrías reformularla?"])
        
        # Seleccionar template aleatorio
        import random
        base_response = random.choice(templates)
        
        # Personalizar con entidades
        if intent == IntentType.FAQ and 'faq_topic' in entities:
            faq_data = self.faq_database[entities['faq_topic']]
            return f"{base_response}\n\n{faq_data['answer']}"
        
        if intent == IntentType.ROUTES and entities:
            route_info = self.format_route_info(entities)
            base_response += f"\n\n{route_info}"
        
        if intent == IntentType.PRICES and entities:
            price_info = self.format_price_info(entities)
            base_response += f"\n\n{price_info}"
        
        return base_response

    def format_route_info(self, entities: Dict[str, Any]) -> str:
        """
        Formatear información de rutas
        """
        if 'origin' in entities and 'destination' in entities:
            origin = entities['origin'].title()
            dest = entities['destination'].title()
            return f"La ruta {origin}-{dest} está disponible. ¿Necesitas horarios específicos?"
        elif 'origin' in entities:
            origin = entities['origin'].title()
            return f"Desde {origin} tenemos rutas a Pisco, Ica y Barrio Chino. ¿Cuál es tu destino?"
        elif 'destination' in entities:
            dest = entities['destination'].title()
            return f"Para llegar a {dest} tenemos salidas desde Chincha y Pisco. ¿Desde dónde partes?"
        else:
            return "Operamos en Chincha, Pisco, Ica y Barrio Chino. ¿Cuál es tu ruta de interés?"

    def format_price_info(self, entities: Dict[str, Any]) -> str:
        """
        Formatear información de precios
        """
        prices = {
            ('chincha', 'pisco'): 5.0,
            ('chincha', 'ica'): 10.0,
            ('pisco', 'ica'): 8.0,
            ('pisco', 'barrio chino'): 5.0,
            ('barrio chino', 'ica'): 5.0
        }
        
        if 'origin' in entities and 'destination' in entities:
            origin = entities['origin'].lower()
            dest = entities['destination'].lower()
            
            key = (origin, dest) if (origin, dest) in prices else (dest, origin)
            if key in prices:
                return f"El precio de {origin.title()}-{dest.title()} es S/. {prices[key]:.2f}"
        
        return "Nuestros precios van desde S/.5.00 hasta S/.10.00 dependiendo de la ruta."

    async def process_message(self, user_id: str, message: str, session_id: str = "") -> Dict[str, Any]:
        """
        Procesar mensaje del usuario
        """
        try:
            # Detectar intent
            intent = self.detect_intent(message)
            
            # Obtener contexto de sesión
            context = self.get_session_context(user_id, session_id)
            
            # Generar respuesta
            response = self.generate_response(intent, context)
            
            # Actualizar contexto
            self.update_session_context(user_id, session_id, message, intent, response)
            
            # Guardar conversación si hay base de datos
            if self.firestore_db:
                await self.save_conversation(user_id, session_id, message, response, intent)
            
            # Evaluar si necesita escalar a humano
            should_escalate = self.should_escalate_to_human(intent, context)
            
            return {
                'success': True,
                'response': response,
                'intent': intent.intent.value,
                'confidence': intent.confidence,
                'entities': intent.entities,
                'should_escalate': should_escalate,
                'session_id': session_id
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'success': False,
                'error': 'Error procesando tu mensaje',
                'response': 'Lo siento, tuve un problema entendiendo tu mensaje. ¿Podrías intentarlo de nuevo?'
            }

    def generate_response(self, intent: ChatIntent, context: Dict[str, Any]) -> str:
        """
        Generar respuesta basada en intent y contexto
        """
        response = intent.response_template
        
        # Añadir contexto de conversación
        if context.get('previous_intents'):
            prev_intent = context['previous_intents'][-1]
            if prev_intent == IntentType.BOOKING and intent.intent == IntentType.ROUTES:
                response += " Perfecto, ahora que sé tu ruta, ¿qué fecha prefieres para viajar?"
            elif prev_intent == IntentType.ROUTES and intent.intent == IntentType.SCHEDULE:
                response += " Excelente, con esa información te puedo dar los horarios exactos."
        
        # Añadir sugerencias de siguientes pasos
        if intent.intent == IntentType.BOOKING:
            response += "\n\nTambién puedo ayudarte con:\n- Horarios disponibles\n- Métodos de pago\n- Políticas de cancelación"
        elif intent.intent == IntentType.PAYMENT:
            response += "\n\n¿Te gustaría saber sobre:\n- Cómo usar Yape/Plin\n- Pagos con tarjeta\n- Políticas de reembolso?"
        
        return response

    def get_session_context(self, user_id: str, session_id: str) -> Dict[str, Any]:
        """
        Obtener contexto de sesión
        """
        key = f"{user_id}_{session_id}"
        return self.session_contexts.get(key, {
            'previous_intents': [],
            'entities_collected': {},
            'message_count': 0,
            'last_activity': datetime.datetime.now()
        })

    def update_session_context(self, user_id: str, session_id: str, message: str, intent: ChatIntent, response: str):
        """
        Actualizar contexto de sesión
        """
        key = f"{user_id}_{session_id}"
        context = self.get_session_context(user_id, session_id)
        
        context['previous_intents'].append(intent.intent)
        context['entities_collected'].update(intent.entities)
        context['message_count'] += 1
        context['last_activity'] = datetime.datetime.now()
        
        # Mantener solo últimos 5 intents
        if len(context['previous_intents']) > 5:
            context['previous_intents'] = context['previous_intents'][-5:]
        
        self.session_contexts[key] = context

    def should_escalate_to_human(self, intent: ChatIntent, context: Dict[str, Any]) -> bool:
        """
        Determinar si debe escalar a humano
        """
        # Escalar si hay quejas repetidas
        if intent.intent == IntentType.COMPLAINT:
            complaint_count = sum(1 for i in context.get('previous_intents', []) if i == IntentType.COMPLAINT)
            if complaint_count >= 2:
                return True
        
        # Escalar si no hay confianza alta después de 3 mensajes
        if context.get('message_count', 0) >= 3 and intent.confidence < 0.5:
            return True
        
        # Escalar si hay palabras clave de urgencia
        urgent_keywords = ['urgente', 'emergencia', 'inmediato', 'grave', 'serio']
        if any(keyword in intent.response_template.lower() for keyword in urgent_keywords):
            return True
        
        return False

    async def save_conversation(self, user_id: str, session_id: str, user_message: str, bot_response: str, intent: ChatIntent):
        """
        Guardar conversación en base de datos
        """
        try:
            if not self.firestore_db:
                return
            
            conversation_data = {
                'user_id': user_id,
                'session_id': session_id,
                'user_message': user_message,
                'bot_response': bot_response,
                'intent': intent.intent.value,
                'confidence': intent.confidence,
                'entities': intent.entities,
                'timestamp': datetime.datetime.utcnow(),
                'resolved': False
            }
            
            self.firestore_db.collection('chat_conversations').add(conversation_data)
            
        except Exception as e:
            logger.error(f"Error saving conversation: {e}")

    def get_conversation_history(self, user_id: str, session_id: str = "", limit: int = 10) -> List[Dict]:
        """
        Obtener historial de conversación
        """
        try:
            if not self.firestore_db:
                return []
            
            query = self.firestore_db.collection('chat_conversations')\
                .where('user_id', '==', user_id)\
                .order_by('timestamp', direction='DESCENDING')\
                .limit(limit)
            
            if session_id:
                query = query.where('session_id', '==', session_id)
            
            docs = query.get()
            return [doc.to_dict() for doc in docs]
            
        except Exception as e:
            logger.error(f"Error getting conversation history: {e}")
            return []

    def get_analytics_data(self, days: int = 7) -> Dict[str, Any]:
        """
        Obtener datos analíticos del chatbot
        """
        try:
            if not self.firestore_db:
                return {}
            
            start_date = datetime.datetime.utcnow() - datetime.timedelta(days=days)
            
            # Conversaciones totales
            conversations = self.firestore_db.collection('chat_conversations')\
                .where('timestamp', '>=', start_date)\
                .get()
            
            # Análisis de intents
            intent_counts = {}
            resolved_count = 0
            
            for doc in conversations:
                data = doc.to_dict()
                intent = data.get('intent', 'unknown')
                intent_counts[intent] = intent_counts.get(intent, 0) + 1
                
                if data.get('resolved', False):
                    resolved_count += 1
            
            total_conversations = len(conversations)
            
            return {
                'total_conversations': total_conversations,
                'resolved_conversations': resolved_count,
                'resolution_rate': (resolved_count / total_conversations * 100) if total_conversations > 0 else 0,
                'intent_distribution': intent_counts,
                'period_days': days
            }
            
        except Exception as e:
            logger.error(f"Error getting analytics data: {e}")
            return {}

# Instancia global del chatbot
chatbot_service = ChatbotService()
