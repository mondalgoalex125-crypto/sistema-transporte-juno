"""
Chatbot Inteligente - JUNO EXPRESS (Versión Mejorada)
"""

import re
import datetime
import random
from typing import Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# =========================
# ENUMS ESTRUCTURA
# =========================
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

# =========================
# SERVICIO CHATBOT
# =========================
class ChatbotService:

    def __init__(self):
        self.session_contexts = {}

        # -------------------------
        # PATRONES
        # -------------------------
        self.intent_patterns = {
            IntentType.GREETING: [r'hola|buenos|hey'],
            IntentType.BOOKING: [r'reservar|comprar|pasaje'],
            IntentType.PAYMENT: [r'pagar|yape|plin|tarjeta'],
            IntentType.SCHEDULE: [r'horario|hora|sale'],
            IntentType.ROUTES: [r'ruta|destino|viaje'],
            IntentType.PRICES: [r'precio|cuesta|costo'],
            IntentType.REFUND: [r'devolucion|cancelar'],
            IntentType.SUPPORT: [r'ayuda|soporte'],
            IntentType.COMPLAINT: [r'queja|mal|error']
        }

        # -------------------------
        # RESPUESTAS
        # -------------------------
        self.responses = {
            IntentType.GREETING: "¡Hola! 👋 Soy el asistente de JUNO EXPRESS. ¿En qué puedo ayudarte?",
            IntentType.BOOKING: "Te ayudaré a reservar tu viaje 🚌",
            IntentType.PAYMENT: "Aceptamos Yape, Plin, tarjetas y efectivo 💳",
            IntentType.SCHEDULE: "Nuestros horarios dependen de la ruta ⏰",
            IntentType.ROUTES: "Tenemos rutas Chincha, Pisco, Ica 📍",
            IntentType.PRICES: "Los precios van desde S/.5 hasta S/.10 💰",
            IntentType.COMPLAINT: "Lamento lo ocurrido 😔 Cuéntame más detalles",
            IntentType.UNKNOWN: "No entendí bien 😅 ¿Puedes explicarlo de otra forma?"
        }

        # -------------------------
        # FAQ
        # -------------------------
        self.faq = {
            "equipaje": "Puedes llevar 1 maleta y 1 equipaje de mano.",
            "mascotas": "Se permiten mascotas pequeñas con costo adicional.",
            "niños": "Niños pagan tarifa reducida."
        }

    # =========================
    # INTENT DETECTION MEJORADO
    # =========================
    def detect_intent(self, message: str) -> ChatIntent:
        msg = message.lower()
        scores = {}

        for intent, patterns in self.intent_patterns.items():
            score = 0
            for p in patterns:
                if re.search(p, msg):
                    score += 2

            for word in msg.split():
                if any(word in p for p in patterns):
                    score += 1

            scores[intent] = score

        best_intent = max(scores, key=scores.get)
        confidence = scores[best_intent] / 5

        if confidence < 0.3:
            best_intent = IntentType.UNKNOWN

        entities = self.extract_entities(msg)

        return ChatIntent(
            intent=best_intent,
            confidence=confidence,
            entities=entities,
            response_template=self.responses.get(best_intent, "")
        )

    # =========================
    # ENTIDADES
    # =========================
    def extract_entities(self, message: str):
        entities = {}

        cities = ["chincha", "pisco", "ica"]
        for c in cities:
            if c in message:
                if "origin" not in entities:
                    entities["origin"] = c
                else:
                    entities["destination"] = c

        return entities

    # =========================
    # RESPUESTAS HUMANAS
    # =========================
    def humanize(self, text: str):
        variations = [
            text,
            text + " 😊",
            "Claro, te ayudo. " + text
        ]
        return random.choice(variations)

    # =========================
    # FAQ
    # =========================
    def search_faq(self, message: str):
        for key in self.faq:
            if key in message:
                return self.faq[key]
        return None

    # =========================
    # DETECTAR FRUSTRACIÓN
    # =========================
    def detect_frustration(self, message: str):
        return any(x in message for x in ["mal", "pésimo", "error"])

    # =========================
    # CONTEXTO
    # =========================
    def get_context(self, user_id):
        return self.session_contexts.get(user_id, {
            "flow": None,
            "data": {}
        })

    def update_context(self, user_id, context):
        self.session_contexts[user_id] = context

    # =========================
    # FLUJO CONVERSACIONAL
    # =========================
    def handle_flow(self, context):
        data = context["data"]

        if "origin" not in data:
            return "¿Desde qué ciudad viajas?"
        if "destination" not in data:
            return "¿A qué destino deseas ir?"
        
        context["flow"] = None
        return f"Perfecto ✅ Viaje de {data['origin']} a {data['destination']} registrado."

    # =========================
    # PROCESAR MENSAJE
    # =========================
    def process_message(self, user_id: str, message: str):
        context = self.get_context(user_id)

        # Detectar frustración
        if self.detect_frustration(message):
            return {
                "response": "Te comunicaré con un asesor humano 👨‍💼",
                "escalate": True
            }

        # FAQ
        faq = self.search_faq(message)
        if faq:
            return {"response": faq}

        intent = self.detect_intent(message)

        # Activar flujo reserva
        if intent.intent == IntentType.BOOKING:
            context["flow"] = "booking"
            context["data"] = {}

        # Guardar entidades
        context["data"].update(intent.entities)

        # Flujo activo
        if context.get("flow") == "booking":
            response = self.handle_flow(context)
        else:
            response = self.humanize(intent.response_template)

        self.update_context(user_id, context)

        return {
            "response": response,
            "intent": intent.intent.value,
            "confidence": intent.confidence
        }


# =========================
# INSTANCIA GLOBAL
# =========================
chatbot = ChatbotService()
