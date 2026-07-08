<template>
  <div class="glass-panel" style="max-width: 700px; margin: 2rem auto;">
    <h2 style="text-align: center; margin-bottom: 2rem; background: linear-gradient(90deg, #ec4899, #6366f1); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">Universal Video Downloader</h2>
    
    <div v-if="error" class="alert alert-error">{{ error }}</div>
    <div v-if="success" class="alert alert-success">{{ success }}</div>
    
    <form @submit.prevent="startDownload">
      <div style="margin-bottom: 1.5rem;">
        <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted);">Media URL (YouTube, TikTok, Instagram, etc.)</label>
        <input type="url" v-model="url" required placeholder="https://www.youtube.com/watch?v=..." />
      </div>
      
      <div style="display: flex; gap: 1rem; margin-bottom: 1.5rem;">
        <div style="flex: 1;">
          <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted);">Format</label>
          <select v-model="format">
            <option value="mp4">Video (MP4)</option>
            <option value="mp3">Audio (MP3)</option>
          </select>
        </div>
        
        <div style="flex: 1;" v-if="format === 'mp4'">
          <label style="display: block; margin-bottom: 0.5rem; color: var(--text-muted);">Quality</label>
          <select v-model="quality">
            <option value="best">Best Available</option>
            <option value="2160">4K (2160p)</option>
            <option value="1080">Full HD (1080p)</option>
            <option value="720">HD (720p)</option>
            <option value="480">SD (480p)</option>
            <option value="360">Low (360p)</option>
          </select>
        </div>
      </div>
      
      <div style="margin-bottom: 1.5rem;">
        <label style="display: flex; align-items: center; cursor: pointer;">
          <input type="checkbox" v-model="isPlaylist" style="width: auto; margin: 0 0.5rem 0 0;" />
          <span style="color: var(--text-muted);">Download entire playlist (if applicable)</span>
        </label>
      </div>
      
      <button type="submit" class="btn" style="width: 100%; font-size: 1.1rem; padding: 1rem;" :disabled="downloading">
        {{ downloading ? 'Initializing...' : 'Download Now' }}
      </button>
    </form>
    
    <!-- Progress Area -->
    <div v-if="taskStatus !== 'idle'" style="margin-top: 2rem; padding-top: 2rem; border-top: 1px solid var(--glass-border);">
      <h3 style="margin-bottom: 1rem;">Status: <span style="color: var(--primary-color); text-transform: capitalize;">{{ taskStatus }}</span></h3>
      
      <div v-if="taskStatus === 'downloading' || taskStatus === 'queued'">
        <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
          <span>{{ progressPercent.toFixed(1) }}%</span>
          <span v-if="speed" style="color: var(--text-muted);">{{ speed }}</span>
        </div>
        <div class="progress-container">
          <div class="progress-bar" :style="{ width: progressPercent + '%' }"></div>
        </div>
      </div>
      
      <div v-if="taskStatus === 'success' && files.length > 0" style="margin-top: 1.5rem;">
        <h4>Files Ready:</h4>
        <ul style="list-style: none; padding: 0; margin-top: 1rem;">
          <li v-for="file in files" :key="file" style="margin-bottom: 0.5rem;">
            <a :href="`http://127.0.0.1:5000/api/download_file/${encodeURIComponent(file)}`" target="_blank" class="btn btn-secondary" style="display: block; text-decoration: none;">
              ⬇️ Download {{ file }}
            </a>
          </li>
        </ul>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const url = ref('')
const format = ref('mp4')
const quality = ref('best')
const isPlaylist = ref(false)

const downloading = ref(false)
const error = ref('')
const success = ref('')

const taskStatus = ref('idle')
const progressPercent = ref(0)
const speed = ref('')
const files = ref([])
let eventSource = null

const startDownload = async () => {
  error.value = ''
  success.value = ''
  downloading.value = true
  taskStatus.value = 'queued'
  progressPercent.value = 0
  speed.value = ''
  files.value = []
  
  if (eventSource) {
    eventSource.close()
  }

  const token = localStorage.getItem('token')
  const headers = { 'Content-Type': 'application/json' }
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }

  try {
    const res = await fetch('http://127.0.0.1:5000/api/downloader', {
      method: 'POST',
      headers,
      body: JSON.stringify({
        url: url.value,
        format: format.value,
        quality: quality.value,
        is_playlist: isPlaylist.value
      })
    })

    const data = await res.json()
    if (!res.ok) {
      throw new Error(data.error || 'Failed to start download')
    }

    const taskId = data.task_id
    listenToProgress(taskId)
    
  } catch (err) {
    error.value = err.message
    downloading.value = false
    taskStatus.value = 'error'
  }
}

const listenToProgress = (taskId) => {
  eventSource = new EventSource(`http://127.0.0.1:5000/api/progress/${taskId}`)
  
  eventSource.onmessage = (event) => {
    const data = JSON.parse(event.data)
    
    taskStatus.value = data.status
    if (data.percent !== undefined) progressPercent.value = data.percent
    if (data.speed !== undefined) speed.value = data.speed
    
    if (data.status === 'success') {
      success.value = 'Download complete!'
      files.value = data.files || []
      downloading.value = false
      eventSource.close()
    } else if (data.status === 'error') {
      error.value = data.message || 'An error occurred during download.'
      downloading.value = false
      eventSource.close()
    }
  }
  
  eventSource.onerror = () => {
    if (taskStatus.value !== 'success' && taskStatus.value !== 'error') {
      error.value = 'Connection to server lost.'
      taskStatus.value = 'error'
      downloading.value = false
    }
    eventSource.close()
  }
}
</script>
