<template>
  <div class="glass-panel" style="max-width: 900px; margin: 2rem auto;">
    <h2 style="margin-bottom: 2rem;">Download History</h2>
    
    <div v-if="loading" style="text-align: center; color: var(--text-muted);">
      Loading history...
    </div>
    
    <div v-else-if="error" class="alert alert-error">
      {{ error }}
    </div>
    
    <div v-else-if="history.length === 0" style="text-align: center; color: var(--text-muted); padding: 3rem 0;">
      No download history found.
    </div>
    
    <div v-else>
      <div v-for="item in history" :key="item.id" class="history-card">
        <div class="history-info">
          <h4 style="margin: 0 0 0.5rem 0; color: var(--text-main);">{{ item.title }}</h4>
          <a :href="item.url" target="_blank" style="color: var(--primary-color); font-size: 0.9rem; text-decoration: none; word-break: break-all;">
            {{ item.url }}
          </a>
          <div style="display: flex; gap: 1rem; margin-top: 0.75rem; font-size: 0.85rem; color: var(--text-muted);">
            <span style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px; text-transform: uppercase;">
              {{ item.format }}
            </span>
            <span v-if="item.quality" style="background: rgba(255,255,255,0.1); padding: 0.2rem 0.5rem; border-radius: 4px;">
              {{ item.quality === 'best' ? 'Best Quality' : item.quality + 'p' }}
            </span>
            <span>{{ new Date(item.timestamp).toLocaleString() }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const history = ref([])
const loading = ref(true)
const error = ref('')

onMounted(async () => {
  const token = localStorage.getItem('token')
  if (!token) {
    router.push('/login')
    return
  }
  
  try {
    const res = await fetch('http://127.0.0.1:5000/api/history/', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (!res.ok) {
      if (res.status === 401) {
        localStorage.removeItem('token')
        router.push('/login')
        return
      }
      throw new Error('Failed to fetch history')
    }
    
    history.value = await res.json()
  } catch (err) {
    error.value = err.message
  } finally {
    loading.value = false
  }
})
</script>

<style scoped>
.history-card {
  background: rgba(15, 23, 42, 0.4);
  border: 1px solid var(--glass-border);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 1rem;
  transition: transform 0.2s ease, background 0.2s ease;
}

.history-card:hover {
  transform: translateX(4px);
  background: rgba(15, 23, 42, 0.6);
}
</style>
