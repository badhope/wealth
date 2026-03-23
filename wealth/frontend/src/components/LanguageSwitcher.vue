<template>
  <div class="language-switcher">
    <button
      class="lang-btn"
      :class="{ active: locale === 'en' }"
      @click="setLocale('en')"
    >
      <span class="lang-icon">🇺🇸</span>
      <span class="lang-text">EN</span>
    </button>
    <button
      class="lang-btn"
      :class="{ active: locale === 'zh' }"
      @click="setLocale('zh')"
    >
      <span class="lang-icon">🇨🇳</span>
      <span class="lang-text">中文</span>
    </button>
  </div>
</template>

<script setup>
import { useI18n } from 'vue-i18n'

const { locale } = useI18n()

const setLocale = (lang) => {
  locale.value = lang
  localStorage.setItem('locale', lang)
  document.documentElement.setAttribute('lang', lang)
}
</script>

<style scoped>
.language-switcher {
  display: flex;
  gap: 4px;
  background: var(--bg-card);
  padding: 4px;
  border-radius: var(--radius-md);
}

.lang-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  border: none;
  background: transparent;
  color: var(--text-secondary);
  font-size: 13px;
  font-weight: 500;
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: var(--transition);
}

.lang-btn:hover {
  background: var(--bg-card-hover);
  color: var(--text-primary);
}

.lang-btn.active {
  background: var(--primary);
  color: white;
}

.lang-icon {
  font-size: 16px;
}

.lang-text {
  font-weight: 600;
}
</style>
