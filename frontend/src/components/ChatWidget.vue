<script setup>
import { ref, nextTick } from 'vue';

const isOpen = ref(false);
const messages = ref([
  { id: 1, text: "Hello! How can I help you?", sender: 'bot' }
]);
const inputMessage = ref('');
const isTyping = ref(false);
const messagesContainer = ref(null);

const toggleChat = () => {
  isOpen.value = !isOpen.value;
  if (isOpen.value) {
    scrollToBottom();
  }
};

const scrollToBottom = async () => {
  await nextTick();
  if (messagesContainer.value) {
    messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight;
  }
};

const sendMessage = async () => {
  if (!inputMessage.value.trim()) return;

  const userMsg = inputMessage.value;
  messages.value.push({ id: Date.now(), text: userMsg, sender: 'user' });
  inputMessage.value = '';
  isTyping.value = true;
  scrollToBottom();

  try {
    let apiUrl = import.meta.env.VITE_APP_CHAT_API_URL || import.meta.env.VITE_APP_API_URL || import.meta.env.VITE_API_URL || 'https://media-downloader-hub-bot-m42q.vercel.app';
    if (apiUrl.endsWith('/')) {
      apiUrl = apiUrl.slice(0, -1);
    }
    const response = await fetch(`${apiUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ message: userMsg })
    });
    
    const data = await response.json();
    messages.value.push({ id: Date.now() + 1, text: data.reply, sender: 'bot' });
  } catch (error) {
    messages.value.push({ id: Date.now() + 1, text: "Sorry, I'm having trouble connecting right now.", sender: 'bot', isError: true });
  } finally {
    isTyping.value = false;
    scrollToBottom();
  }
};
</script>

<template>
  <div class="chat-widget-wrapper">
    <!-- Chat Window -->
    <transition name="slide-fade">
      <div v-if="isOpen" class="chat-window glass">
        <div class="chat-header">
          <h3>Assistant</h3>
          <button @click="toggleChat" class="close-btn" aria-label="Close Chat">&times;</button>
        </div>
        
        <div class="chat-messages" ref="messagesContainer">
          <div v-for="msg in messages" :key="msg.id" 
               :class="['message', msg.sender === 'user' ? 'user-message' : 'bot-message', { 'error-message': msg.isError }]">
            {{ msg.text }}
          </div>
          
          <div v-if="isTyping" class="message bot-message typing-indicator">
            <span></span><span></span><span></span>
          </div>
        </div>
        
        <div class="chat-input-area">
          <input 
            v-model="inputMessage" 
            @keyup.enter="sendMessage"
            type="text" 
            placeholder="Type your message..." 
            class="chat-input"
            :disabled="isTyping"
          />
          <button @click="sendMessage" class="send-btn" :disabled="!inputMessage.trim() || isTyping">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </transition>

    <!-- Floating Toggle Button -->
    <button class="chat-toggle-btn" @click="toggleChat" :class="{ 'is-open': isOpen }">
      <svg v-if="!isOpen" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path>
      </svg>
      <svg v-else viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
        <line x1="18" y1="6" x2="6" y2="18"></line>
        <line x1="6" y1="6" x2="18" y2="18"></line>
      </svg>
    </button>
  </div>
</template>

<style scoped>
.chat-widget-wrapper {
  position: fixed;
  bottom: 2rem;
  right: 2rem;
  z-index: 9999;
  display: flex;
  flex-direction: column;
  align-items: flex-end;
}

.chat-toggle-btn {
  width: 60px;
  height: 60px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  border: none;
  cursor: pointer;
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}

.chat-toggle-btn svg {
  width: 28px;
  height: 28px;
}

.chat-toggle-btn:hover {
  transform: scale(1.1);
  background: var(--primary-hover);
  box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6);
}

.chat-toggle-btn.is-open {
  background: var(--surface);
  border: 1px solid var(--surface-border);
  color: var(--text-muted);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
}

.chat-toggle-btn.is-open:hover {
  color: white;
}

.chat-window {
  width: 350px;
  height: 500px;
  max-height: calc(100vh - 120px);
  margin-bottom: 1rem;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.chat-header {
  padding: 1rem 1.5rem;
  border-bottom: 1px solid var(--surface-border);
  display: flex;
  justify-content: space-between;
  align-items: center;
  background: rgba(30, 41, 59, 0.8);
}

.chat-header h3 {
  font-size: 1.1rem;
  font-weight: 600;
  margin: 0;
  background: -webkit-linear-gradient(45deg, var(--primary), var(--secondary));
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
}

.close-btn {
  background: none;
  border: none;
  color: var(--text-muted);
  font-size: 1.5rem;
  cursor: pointer;
  transition: color 0.2s;
  line-height: 1;
}

.close-btn:hover {
  color: var(--error);
}

.chat-messages {
  flex: 1;
  padding: 1.5rem;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* Custom scrollbar for messages */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}
.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--surface-border);
  border-radius: 10px;
}

.message {
  padding: 0.75rem 1rem;
  border-radius: 14px;
  max-width: 85%;
  word-wrap: break-word;
  line-height: 1.4;
  font-size: 0.95rem;
}

.user-message {
  align-self: flex-end;
  background: var(--primary);
  color: white;
  border-bottom-right-radius: 4px;
}

.bot-message {
  align-self: flex-start;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid var(--surface-border);
  border-bottom-left-radius: 4px;
}

.error-message {
  border-color: var(--error);
  color: #fca5a5;
}

.chat-input-area {
  padding: 1rem;
  border-top: 1px solid var(--surface-border);
  display: flex;
  gap: 0.5rem;
  background: rgba(30, 41, 59, 0.5);
}

.chat-input {
  flex: 1;
  background: rgba(0, 0, 0, 0.2);
  border: 1px solid var(--surface-border);
  border-radius: 20px;
  padding: 0.75rem 1rem;
  color: var(--text-main);
  font-family: inherit;
  font-size: 0.95rem;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: var(--primary);
}

.send-btn {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--primary);
  color: white;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  transition: all 0.2s;
}

.send-btn svg {
  width: 18px;
  height: 18px;
  transform: translateX(-1px) translateY(1px);
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.send-btn:disabled {
  background: var(--surface-border);
  color: var(--text-muted);
  cursor: not-allowed;
}

/* Typing Indicator */
.typing-indicator {
  display: flex;
  gap: 4px;
  padding: 1rem;
  align-items: center;
  width: fit-content;
}

.typing-indicator span {
  width: 6px;
  height: 6px;
  background-color: var(--text-muted);
  border-radius: 50%;
  animation: typing 1.4s infinite both;
}

.typing-indicator span:nth-child(1) { animation-delay: 0s; }
.typing-indicator span:nth-child(2) { animation-delay: 0.2s; }
.typing-indicator span:nth-child(3) { animation-delay: 0.4s; }

@keyframes typing {
  0%, 80%, 100% { transform: scale(0); opacity: 0.5; }
  40% { transform: scale(1); opacity: 1; }
}

/* Transitions */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from,
.slide-fade-leave-to {
  transform: translateY(20px) scale(0.95);
  opacity: 0;
}

@media (max-width: 480px) {
  .chat-window {
    width: calc(100vw - 2rem);
    height: 400px;
  }
}
</style>
