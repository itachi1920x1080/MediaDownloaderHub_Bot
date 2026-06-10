<script setup>
import DownloaderForm from './components/DownloaderForm.vue'
import ChatWidget from './components/ChatWidget.vue'
</script>

<template>
  <div class="app-container animate-fade-in">
    <header class="header text-center">
      <h1>Media Downloader</h1>
      <p class="subtitle">Download your favorite media effortlessly and securely.</p>
    </header>
    
    <main class="main-content">
      <DownloaderForm />
    </main>
    
    <footer class="footer text-center">
      <p>&copy; 2026 Media Downloader Hub</p>
    </footer>

    <ChatWidget />
  </div>
</template>

<style scoped>
.app-container {
  width: 100%;
  max-width: 600px;
  padding: 2rem;
  margin: 0 auto;
}

.text-center {
  text-align: center;
}

.header {
  margin-bottom: 2rem;
}

.subtitle {
  color: var(--text-muted);
  font-size: 1.1rem;
}

.main-content {
  margin-bottom: 2rem;
}

.footer {
  color: var(--text-muted);
  font-size: 0.9rem;
  opacity: 0.7;
}
</style>
