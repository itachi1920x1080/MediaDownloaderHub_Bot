<script setup>
import { ref } from 'vue'

const url = ref('')
const loading = ref(false)
const message = ref('')
const error = ref(false)

const handleDownload = async () => {
  if (!url.value) {
    message.value = 'សូមបញ្ចូលតំណភ្ជាប់វីដេអូ / Please enter a video URL'
    error.value = true
    return
  }

  loading.value = true
  message.value = ''
  error.value = false

  try {
    const API_URL = import.meta.env.VITE_APP_API_URL || ''
    const response = await fetch(`${API_URL}/api/downloader`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ url: url.value })
    })

    const data = await response.json()

    if (!response.ok || data.status === 'error') {
      throw new Error(data.message || 'Something went wrong')
    }

    message.value = data.message
    error.value = false
    url.value = '' // clear on success
  } catch (err) {
    message.value = err.message
    error.value = true
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="form-card glass">
    <form @submit.prevent="handleDownload" class="form-container">
      <div class="input-group">
        <input 
          v-model="url" 
          type="url" 
          placeholder="Paste video URL here..." 
          class="url-input"
          :disabled="loading"
        />
      </div>
      
      <button 
        type="submit" 
        class="submit-btn" 
        :disabled="loading"
      >
        <span v-if="loading" class="spinner animate-spin"></span>
        <span v-else>Download</span>
      </button>
    </form>

    <Transition name="fade">
      <div v-if="message" :class="['status-message', error ? 'error-msg' : 'success-msg']">
        {{ message }}
      </div>
    </Transition>
  </div>
</template>

<style scoped>
.form-card {
  padding: 2rem;
}

.form-container {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.input-group {
  position: relative;
  width: 100%;
}

.url-input {
  width: 100%;
  padding: 1rem 1.5rem;
  border-radius: 12px;
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid rgba(255, 255, 255, 0.1);
  color: var(--text-main);
  font-size: 1rem;
  outline: none;
  transition: all 0.3s ease;
}

.url-input:focus {
  border-color: var(--primary);
  box-shadow: 0 0 0 2px rgba(139, 92, 246, 0.2);
  background: rgba(15, 23, 42, 0.8);
}

.url-input::placeholder {
  color: var(--text-muted);
}

.submit-btn {
  width: 100%;
  padding: 1rem;
  border-radius: 12px;
  background: linear-gradient(135deg, var(--primary), var(--secondary));
  color: white;
  font-size: 1.1rem;
  font-weight: 600;
  border: none;
  cursor: pointer;
  transition: transform 0.2s ease, box-shadow 0.2s ease;
  display: flex;
  justify-content: center;
  align-items: center;
}

.submit-btn:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 15px rgba(139, 92, 246, 0.4);
}

.submit-btn:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

.spinner {
  width: 20px;
  height: 20px;
  border: 3px solid rgba(255,255,255,0.3);
  border-radius: 50%;
  border-top-color: white;
  display: inline-block;
}

.status-message {
  margin-top: 1.5rem;
  padding: 1rem;
  border-radius: 8px;
  text-align: center;
  font-size: 0.95rem;
  font-weight: 500;
}

.error-msg {
  background: rgba(239, 68, 68, 0.1);
  color: #fca5a5;
  border: 1px solid rgba(239, 68, 68, 0.2);
}

.success-msg {
  background: rgba(16, 185, 129, 0.1);
  color: #6ee7b7;
  border: 1px solid rgba(16, 185, 129, 0.2);
}

/* Transitions */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>
