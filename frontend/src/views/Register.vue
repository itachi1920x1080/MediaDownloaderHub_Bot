<template>
  <div class="glass-panel" style="max-width: 400px; margin: 4rem auto;">
    <h2 style="text-align: center; margin-bottom: 2rem;">Register</h2>
    
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <form @submit.prevent="handleRegister">
      <div>
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted);">Username</label>
        <input type="text" v-model="username" required placeholder="Choose a username" />
      </div>
      
      <div>
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted);">Password</label>
        <input type="password" v-model="password" required placeholder="Choose a password" />
      </div>
      
      <button type="submit" class="btn" style="width: 100%; margin-top: 1rem;" :disabled="loading">
        {{ loading ? 'Registering...' : 'Register' }}
      </button>
    </form>
    
    <div style="margin: 1.5rem 0; text-align: center; position: relative;">
      <hr style="border: 0; border-top: 1px solid var(--glass-border);" />
      <span style="position: absolute; top: -10px; left: 50%; transform: translateX(-50%); background: var(--glass-bg); padding: 0 10px; color: var(--text-muted); font-size: 0.9rem;">OR</span>
    </div>
    
    <a href="http://127.0.0.1:5000/api/auth/google/login" class="btn btn-secondary" style="width: 100%; display: flex; align-items: center; justify-content: center; gap: 10px; text-decoration: none; padding: 0.75rem;">
      <svg width="18" height="18" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><path fill="#EA4335" d="M24 9.5c3.54 0 6.71 1.22 9.21 3.6l6.85-6.85C35.9 2.38 30.47 0 24 0 14.62 0 6.51 5.38 2.56 13.22l7.98 6.19C12.43 13.7 17.74 9.5 24 9.5z"/><path fill="#4285F4" d="M46.98 24.55c0-1.57-.15-3.09-.38-4.55H24v9.02h12.94c-.58 2.96-2.26 5.48-4.78 7.18l7.73 6c4.51-4.18 7.09-10.36 7.09-17.65z"/><path fill="#FBBC05" d="M10.53 28.59c-.48-1.45-.76-2.99-.76-4.59s.27-3.14.76-4.59l-7.98-6.19C.92 16.46 0 20.12 0 24c0 3.88.92 7.54 2.56 10.78l7.97-6.19z"/><path fill="#34A853" d="M24 48c6.48 0 11.93-2.13 15.89-5.81l-7.73-6c-2.15 1.45-4.92 2.3-8.16 2.3-6.26 0-11.57-4.22-13.47-9.91l-7.98 6.19C6.51 42.62 14.62 48 24 48z"/></svg>
      Continue with Google
    </a>
    
    <p style="text-align: center; margin-top: 1.5rem; color: var(--text-muted);">
      Already have an account? <router-link to="/login" style="color: var(--primary-color);">Login</router-link>
    </p>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const username = ref('')
const password = ref('')
const error = ref('')
const success = ref('')
const loading = ref(false)

const handleRegister = async () => {
  error.value = ''
  success.value = ''
  loading.value = true
  
  try {
    const res = await fetch('http://127.0.0.1:5000/api/auth/register', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ username: username.value, password: password.value })
    })
    
    const data = await res.json()
    
    if (!res.ok) {
      throw new Error(data.error || 'Registration failed')
    }
    
    success.value = 'Registration successful! Redirecting to login...'
    setTimeout(() => {
      router.push('/login')
    }, 1500)
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
}
</script>
