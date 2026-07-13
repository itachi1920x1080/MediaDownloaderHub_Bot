<template>
  <div id="app">
    <nav class="navbar">
      <div class="logo" style="font-weight: 700; font-size: 1.25rem; color: var(--text-main);">
        MediaDownloader<span style="color: var(--primary-color);">Hub</span>
      </div>
      <div class="nav-links">
        <router-link to="/">Downloader</router-link>
        <router-link v-if="isLoggedIn" to="/history">History</router-link>
        <a v-if="isLoggedIn" href="#" @click.prevent="logout">Logout</a>
        <router-link v-if="!isLoggedIn" to="/login">Login</router-link>
        <router-link v-if="!isLoggedIn" to="/register">Register</router-link>
      </div>
    </nav>

    <router-view></router-view>
    <ChatWidget />
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ChatWidget from './components/ChatWidget.vue'

const router = useRouter()
const route = useRoute()
const isLoggedIn = ref(false)

const checkAuth = () => {
  const urlParams = new URLSearchParams(window.location.search)
  const tokenFromUrl = urlParams.get('token')
  const usernameFromUrl = urlParams.get('username')
  
  if (tokenFromUrl) {
    localStorage.setItem('token', tokenFromUrl)
    if (usernameFromUrl) {
      localStorage.setItem('username', usernameFromUrl)
    }
    // Clean up URL
    window.history.replaceState({}, document.title, window.location.pathname)
  }
  
  isLoggedIn.value = !!localStorage.getItem('token')
}

onMounted(checkAuth)

// Watch for route changes to update auth status
watch(() => route.path, checkAuth)

const logout = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('username')
  isLoggedIn.value = false
  router.push('/login')
}
</script>

<style scoped>
.logo {
  cursor: pointer;
}
</style>
