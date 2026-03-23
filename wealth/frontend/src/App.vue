<script setup>
import { RouterView } from 'vue-router'
import AppHeader from './components/AppHeader.vue'
import ToastNotification from './components/ToastNotification.vue'
import LoadingSpinner from './components/LoadingSpinner.vue'
</script>

<template>
  <div id="app">
    <AppHeader />
    <main class="main-content">
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>
    <ToastNotification />
  </div>
</template>

<style lang="scss">
#app {
  min-height: 100vh;
  background: #0a0e17;
}

.main-content {
  min-height: calc(100vh - 64px);
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@media (max-width: 768px) {
  .main-content {
    padding: 16px;
  }
}
</style>
