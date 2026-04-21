// Chatbot de Soporte para JUNO EXPRESS
class ChatbotManager {
    constructor() {
        this.isOpen = false;
        this.sessionId = this.generateSessionId();
        this.userId = this.getCurrentUserId();
        this.messageHistory = [];
        this.isTyping = false;
        this.init();
    }

    init() {
        this.createChatWidget();
        this.setupEventListeners();
        this.loadConversationHistory();
        console.log('Chatbot initialized');
    }

    generateSessionId() {
        return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    }

    getCurrentUserId() {
        return sessionStorage.getItem('user_id') || localStorage.getItem('user_id') || 'anonymous';
    }

    createChatWidget() {
        // Crear HTML del chatbot
        const chatHTML = `
            <div id="chatbot-widget" class="chatbot-widget">
                <!-- Botón flotante -->
                <div id="chatbot-toggle" class="chatbot-toggle">
                    <i class="fas fa-comments"></i>
                    <span class="chat-badge">1</span>
                </div>
                
                <!-- Ventana de chat -->
                <div id="chatbot-window" class="chatbot-window">
                    <!-- Header -->
                    <div class="chatbot-header">
                        <div class="chatbot-info">
                            <img src="/static/images/bus-icon.png" alt="JUNO EXPRESS" class="chatbot-avatar">
                            <div class="chatbot-details">
                                <h6 class="mb-0">Asistente JUNO</h6>
                                <small class="text-success">En línea</small>
                            </div>
                        </div>
                        <div class="chatbot-controls">
                            <button class="btn btn-sm btn-link" onclick="chatbotManager.minimizeChat()">
                                <i class="fas fa-minus"></i>
                            </button>
                            <button class="btn btn-sm btn-link" onclick="chatbotManager.closeChat()">
                                <i class="fas fa-times"></i>
                            </button>
                        </div>
                    </div>
                    
                    <!-- Messages area -->
                    <div id="chatbot-messages" class="chatbot-messages">
                        <div class="chatbot-welcome">
                            <div class="chatbot-message bot">
                                <div class="message-content">
                                    <p>¡Hola! Soy el asistente virtual de JUNO EXPRESS. ¿En qué puedo ayudarte hoy?</p>
                                </div>
                                <div class="message-time">Ahora</div>
                            </div>
                        </div>
                        
                        <!-- Quick actions -->
                        <div class="chatbot-quick-actions">
                            <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('Quiero hacer una reserva')">
                                <i class="fas fa-ticket-alt"></i> Hacer reserva
                            </button>
                            <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('¿Cuáles son los horarios?')">
                                <i class="fas fa-clock"></i> Horarios
                            </button>
                            <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('¿Cuánto cuesta?')">
                                <i class="fas fa-tag"></i> Precios
                            </button>
                            <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('Necesito ayuda')">
                                <i class="fas fa-question-circle"></i> Ayuda
                            </button>
                        </div>
                    </div>
                    
                    <!-- Typing indicator -->
                    <div id="typing-indicator" class="typing-indicator" style="display: none;">
                        <div class="typing-dots">
                            <span></span>
                            <span></span>
                            <span></span>
                        </div>
                        <small>Asistente está escribiendo...</small>
                    </div>
                    
                    <!-- Input area -->
                    <div class="chatbot-input">
                        <div class="input-group">
                            <input type="text" id="chatbot-input" class="form-control" placeholder="Escribe tu mensaje..." maxlength="500">
                            <button class="btn btn-primary" id="send-btn" onclick="chatbotManager.sendMessage()">
                                <i class="fas fa-paper-plane"></i>
                            </button>
                        </div>
                        <div class="chatbot-options">
                            <button class="btn btn-sm btn-outline-secondary" onclick="chatbotManager.clearChat()">
                                <i class="fas fa-trash"></i> Limpiar
                            </button>
                            <button class="btn btn-sm btn-outline-secondary" onclick="chatbotManager.emailChat()">
                                <i class="fas fa-envelope"></i> Enviar por email
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;

        // Agregar al body
        document.body.insertAdjacentHTML('beforeend', chatHTML);
        
        // Agregar estilos CSS
        this.addChatStyles();
    }

    addChatStyles() {
        const styles = `
            <style id="chatbot-styles">
                .chatbot-widget {
                    position: fixed;
                    bottom: 20px;
                    right: 20px;
                    z-index: 9999;
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
                }
                
                .chatbot-toggle {
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border: none;
                    cursor: pointer;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.15);
                    transition: all 0.3s ease;
                    position: relative;
                }
                
                .chatbot-toggle:hover {
                    transform: scale(1.1);
                    box-shadow: 0 6px 20px rgba(0,0,0,0.2);
                }
                
                .chat-badge {
                    position: absolute;
                    top: -5px;
                    right: -5px;
                    background: #ff4444;
                    color: white;
                    border-radius: 50%;
                    width: 20px;
                    height: 20px;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 11px;
                    font-weight: bold;
                }
                
                .chatbot-window {
                    position: absolute;
                    bottom: 80px;
                    right: 0;
                    width: 380px;
                    height: 500px;
                    background: white;
                    border-radius: 12px;
                    box-shadow: 0 8px 32px rgba(0,0,0,0.12);
                    display: none;
                    flex-direction: column;
                    overflow: hidden;
                    border: 1px solid #e0e0e0;
                }
                
                .chatbot-window.open {
                    display: flex;
                    animation: slideUp 0.3s ease;
                }
                
                .chatbot-window.minimized {
                    height: 60px;
                }
                
                .chatbot-header {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    padding: 15px;
                    display: flex;
                    align-items: center;
                    justify-content: space-between;
                }
                
                .chatbot-info {
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .chatbot-avatar {
                    width: 40px;
                    height: 40px;
                    border-radius: 50%;
                    border: 2px solid white;
                }
                
                .chatbot-details h6 {
                    font-size: 14px;
                    font-weight: 600;
                }
                
                .chatbot-controls {
                    display: flex;
                    gap: 5px;
                }
                
                .chatbot-controls .btn {
                    color: white;
                    padding: 2px 8px;
                }
                
                .chatbot-messages {
                    flex: 1;
                    overflow-y: auto;
                    padding: 15px;
                    background: #f8f9fa;
                }
                
                .chatbot-message {
                    margin-bottom: 15px;
                    display: flex;
                    align-items: flex-end;
                    gap: 8px;
                }
                
                .chatbot-message.user {
                    flex-direction: row-reverse;
                }
                
                .chatbot-message.bot .message-content {
                    background: white;
                    border: 1px solid #e0e0e0;
                    border-radius: 18px 18px 18px 4px;
                    padding: 10px 15px;
                    max-width: 80%;
                }
                
                .chatbot-message.user .message-content {
                    background: linear-gradient(135deg, var(--primary-color), var(--secondary-color));
                    color: white;
                    border-radius: 18px 18px 4px 18px;
                    padding: 10px 15px;
                    max-width: 80%;
                }
                
                .message-content p {
                    margin: 0;
                    font-size: 14px;
                    line-height: 1.4;
                }
                
                .message-time {
                    font-size: 11px;
                    color: #999;
                    margin-top: 4px;
                }
                
                .chatbot-message.user .message-time {
                    text-align: right;
                }
                
                .chatbot-quick-actions {
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 8px;
                    margin-top: 15px;
                    margin-bottom: 15px;
                }
                
                .quick-action-btn {
                    padding: 8px 12px;
                    border: 1px solid #ddd;
                    background: white;
                    border-radius: 20px;
                    font-size: 12px;
                    cursor: pointer;
                    transition: all 0.2s ease;
                    display: flex;
                    align-items: center;
                    gap: 5px;
                }
                
                .quick-action-btn:hover {
                    background: var(--primary-color);
                    color: white;
                    border-color: var(--primary-color);
                }
                
                .typing-indicator {
                    padding: 10px 15px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                }
                
                .typing-dots {
                    display: flex;
                    gap: 4px;
                }
                
                .typing-dots span {
                    width: 8px;
                    height: 8px;
                    border-radius: 50%;
                    background: #999;
                    animation: typing 1.4s infinite;
                }
                
                .typing-dots span:nth-child(2) {
                    animation-delay: 0.2s;
                }
                
                .typing-dots span:nth-child(3) {
                    animation-delay: 0.4s;
                }
                
                .chatbot-input {
                    padding: 15px;
                    background: white;
                    border-top: 1px solid #e0e0e0;
                }
                
                .chatbot-options {
                    display: flex;
                    gap: 8px;
                    margin-top: 8px;
                    justify-content: center;
                }
                
                @keyframes slideUp {
                    from {
                        opacity: 0;
                        transform: translateY(20px);
                    }
                    to {
                        opacity: 1;
                        transform: translateY(0);
                    }
                }
                
                @keyframes typing {
                    0%, 60%, 100% {
                        opacity: 0.3;
                    }
                    30% {
                        opacity: 1;
                    }
                }
                
                /* Responsive */
                @media (max-width: 480px) {
                    .chatbot-widget {
                        bottom: 10px;
                        right: 10px;
                    }
                    
                    .chatbot-window {
                        width: calc(100vw - 40px);
                        right: -10px;
                        height: 450px;
                    }
                    
                    .chatbot-quick-actions {
                        grid-template-columns: 1fr;
                    }
                }
            </style>
        `;

        document.head.insertAdjacentHTML('beforeend', styles);
    }

    setupEventListeners() {
        // Toggle chat
        document.getElementById('chatbot-toggle').addEventListener('click', () => {
            this.toggleChat();
        });

        // Enter key para enviar mensaje
        document.getElementById('chatbot-input').addEventListener('keypress', (e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                this.sendMessage();
            }
        });

        // Auto-resize de input
        document.getElementById('chatbot-input').addEventListener('input', (e) => {
            this.autoResizeInput(e.target);
        });
    }

    toggleChat() {
        const window = document.getElementById('chatbot-window');
        const toggle = document.getElementById('chatbot-toggle');
        
        this.isOpen = !this.isOpen;
        
        if (this.isOpen) {
            window.classList.add('open');
            toggle.style.display = 'none';
            document.getElementById('chatbot-input').focus();
            this.hideBadge();
        } else {
            window.classList.remove('open');
            toggle.style.display = 'flex';
        }
    }

    minimizeChat() {
        const window = document.getElementById('chatbot-window');
        window.classList.toggle('minimized');
    }

    closeChat() {
        this.isOpen = false;
        document.getElementById('chatbot-window').classList.remove('open');
        document.getElementById('chatbot-toggle').style.display = 'flex';
    }

    async sendMessage() {
        const input = document.getElementById('chatbot-input');
        const message = input.value.trim();
        
        if (!message || this.isTyping) return;
        
        // Agregar mensaje del usuario
        this.addMessage(message, 'user');
        
        // Limpiar input
        input.value = '';
        this.autoResizeInput(input);
        
        // Mostrar indicador de escritura
        this.showTypingIndicator();
        
        try {
            // Enviar al backend
            const response = await fetch('/api/chatbot/message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: this.userId,
                    message: message,
                    session_id: this.sessionId
                })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Agregar respuesta del bot
                this.addMessage(result.response, 'bot');
                
                // Evaluar si necesita escalar
                if (result.should_escalate) {
                    this.showEscalationOption();
                }
            } else {
                this.addMessage('Lo siento, tuve un problema entendiendo tu mensaje. ¿Podrías intentarlo de nuevo?', 'bot');
            }
            
        } catch (error) {
            console.error('Error sending message:', error);
            this.addMessage('Lo siento, hay un problema de conexión. Por favor, intenta más tarde.', 'bot');
        } finally {
            this.hideTypingIndicator();
        }
    }

    sendQuickMessage(message) {
        document.getElementById('chatbot-input').value = message;
        this.sendMessage();
    }

    addMessage(content, sender) {
        const messagesContainer = document.getElementById('chatbot-messages');
        const welcomeDiv = messagesContainer.querySelector('.chatbot-welcome');
        const quickActions = messagesContainer.querySelector('.chatbot-quick-actions');
        
        // Ocultar welcome y quick actions después del primer mensaje
        if (this.messageHistory.length === 0) {
            if (welcomeDiv) welcomeDiv.style.display = 'none';
            if (quickActions) quickActions.style.display = 'none';
        }
        
        const messageDiv = document.createElement('div');
        messageDiv.className = `chatbot-message ${sender}`;
        
        const messageContent = document.createElement('div');
        messageContent.className = 'message-content';
        messageContent.innerHTML = `<p>${this.escapeHtml(content)}</p>`;
        
        const messageTime = document.createElement('div');
        messageTime.className = 'message-time';
        messageTime.textContent = this.formatTime(new Date());
        
        messageDiv.appendChild(messageContent);
        messageDiv.appendChild(messageTime);
        
        messagesContainer.appendChild(messageDiv);
        
        // Guardar en historial
        this.messageHistory.push({
            content: content,
            sender: sender,
            timestamp: new Date()
        });
        
        // Scroll al bottom
        this.scrollToBottom();
    }

    showTypingIndicator() {
        this.isTyping = true;
        document.getElementById('typing-indicator').style.display = 'flex';
        this.scrollToBottom();
    }

    hideTypingIndicator() {
        this.isTyping = false;
        document.getElementById('typing-indicator').style.display = 'none';
    }

    showEscalationOption() {
        const escalationDiv = document.createElement('div');
        escalationDiv.className = 'chatbot-escalation';
        escalationDiv.innerHTML = `
            <div class="alert alert-info">
                <i class="fas fa-user-headset me-2"></i>
                <strong>¿Necesitas ayuda humana?</strong><br>
                <small>Puedo conectarte con un agente de soporte.</small>
                <div class="mt-2">
                    <button class="btn btn-sm btn-primary" onclick="chatbotManager.escalateToHuman()">
                        <i class="fas fa-phone me-1"></i> Hablar con agente
                    </button>
                    <button class="btn btn-sm btn-outline-secondary" onclick="chatbotManager.continueWithBot()">
                        Continuar con asistente
                    </button>
                </div>
            </div>
        `;
        
        document.getElementById('chatbot-messages').appendChild(escalationDiv);
        this.scrollToBottom();
    }

    escalateToHuman() {
        this.addMessage('Conectándote con un agente de soporte...', 'bot');
        
        // Aquí iría la lógica para conectar con agente humano
        setTimeout(() => {
            this.addMessage('Un agente te atenderá en unos momentos. Mientras tanto, ¿hay algo más en lo que pueda ayudarte?', 'bot');
        }, 2000);
    }

    continueWithBot() {
        const escalationDiv = document.querySelector('.chatbot-escalation');
        if (escalationDiv) {
            escalationDiv.remove();
        }
        
        this.addMessage('Perfecto, continuaré ayudándote. ¿Qué más necesitas saber?', 'bot');
    }

    clearChat() {
        if (confirm('¿Estás seguro de que quieres limpiar el chat?')) {
            const messagesContainer = document.getElementById('chatbot-messages');
            messagesContainer.innerHTML = `
                <div class="chatbot-welcome">
                    <div class="chatbot-message bot">
                        <div class="message-content">
                            <p>¡Hola! Soy el asistente virtual de JUNO EXPRESS. ¿En qué puedo ayudarte hoy?</p>
                        </div>
                        <div class="message-time">Ahora</div>
                    </div>
                </div>
                <div class="chatbot-quick-actions">
                    <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('Quiero hacer una reserva')">
                        <i class="fas fa-ticket-alt"></i> Hacer reserva
                    </button>
                    <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('¿Cuáles son los horarios?')">
                        <i class="fas fa-clock"></i> Horarios
                    </button>
                    <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('¿Cuánto cuesta?')">
                        <i class="fas fa-tag"></i> Precios
                    </button>
                    <button class="quick-action-btn" onclick="chatbotManager.sendQuickMessage('Necesito ayuda')">
                        <i class="fas fa-question-circle"></i> Ayuda
                    </button>
                </div>
            `;
            
            this.messageHistory = [];
            this.sessionId = this.generateSessionId();
        }
    }

    emailChat() {
        const chatContent = this.messageHistory
            .map(msg => `${msg.sender === 'user' ? 'Tú' : 'Asistente'}: ${msg.content}`)
            .join('\n\n');
        
        const subject = 'Conversación con Asistente JUNO EXPRESS';
        const body = `Conversación del ${new Date().toLocaleDateString()}:\n\n${chatContent}`;
        
        const mailtoLink = `mailto:mondalgoalex125@gmail.com?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
        window.open(mailtoLink);
    }

    async loadConversationHistory() {
        try {
            const response = await fetch(`/api/chatbot/history/${this.userId}?session_id=${this.sessionId}&limit=10`);
            if (response.ok) {
                const history = await response.json();
                
                // Cargar mensajes previos
                history.reverse().forEach(msg => {
                    this.addMessage(msg.user_message, 'user');
                    this.addMessage(msg.bot_response, 'bot');
                });
            }
        } catch (error) {
            console.error('Error loading conversation history:', error);
        }
    }

    scrollToBottom() {
        const messagesContainer = document.getElementById('chatbot-messages');
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }

    autoResizeInput(input) {
        input.style.height = 'auto';
        input.style.height = Math.min(input.scrollHeight, 100) + 'px';
    }

    formatTime(date) {
        return date.toLocaleTimeString('es-PE', {
            hour: '2-digit',
            minute: '2-digit'
        });
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    showBadge() {
        const badge = document.querySelector('.chat-badge');
        if (badge && !this.isOpen) {
            badge.style.display = 'flex';
        }
    }

    hideBadge() {
        const badge = document.querySelector('.chat-badge');
        if (badge) {
            badge.style.display = 'none';
        }
    }

    // Métodos públicos
    openChat() {
        if (!this.isOpen) {
            this.toggleChat();
        }
    }

    closeChatWidget() {
        const widget = document.getElementById('chatbot-widget');
        if (widget) {
            widget.remove();
        }
        const styles = document.getElementById('chatbot-styles');
        if (styles) {
            styles.remove();
        }
    }
}

// Inicializar cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    window.chatbotManager = new ChatbotManager();
    
    // Exponer globalmente
    window.ChatbotManager = ChatbotManager;
});

// Exportar para módulos
if (typeof module !== 'undefined' && module.exports) {
    module.exports = ChatbotManager;
}
