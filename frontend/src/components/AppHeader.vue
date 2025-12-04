<template>
  <header class="app-header glass-panel">
    <div class="container header-content">
      <router-link to="/" class="logo">
        <span class="material-icons logo-icon">change_history</span>
        <span class="logo-text">CatchTheDiff</span>
      </router-link>
      
      <div class="header-actions">
        <nav class="nav-links">
          <router-link to="/" class="nav-link" active-class="active">首頁</router-link>
          <router-link to="/recent" class="nav-link" active-class="active">變更紀錄</router-link>
          <router-link to="/stats" class="nav-link" active-class="active">統計資訊</router-link>
        </nav>
        
        <a href="https://github.com/qian403/CatchTheDiff" target="_blank" class="github-link">
          <span class="material-icons">code</span>
          GitHub
        </a>
      </div>
    </div>
  </header>
</template>

<script setup lang="ts">
// No logic needed for now
</script>

<style scoped>
.app-header {
  position: sticky;
  top: 0;
  z-index: var(--z-header);
  background: rgba(15, 23, 42, 0.8);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.05);
  margin-bottom: var(--spacing-xl);
}

.header-content {
  height: 64px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-weight: 700;
  font-size: 1.25rem;
  margin-right: var(--spacing-xl);
}

.logo-icon {
  color: var(--color-accent-primary);
  font-size: 24px;
}

.logo-text {
  background: var(--gradient-primary);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.nav-links {
  display: flex;
  gap: var(--spacing-lg);
}

.nav-link {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  transition: color var(--transition-fast);
  padding: 4px 0;
  position: relative;
}

.nav-link:hover {
  color: var(--color-text-primary);
}

.nav-link.active {
  color: var(--color-accent-primary);
}

.nav-link.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  width: 100%;
  height: 2px;
  background-color: var(--color-accent-primary);
  border-radius: var(--radius-full);
}

.github-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--color-text-secondary);
  transition: color var(--transition-fast);
}

.github-link:hover {
  color: var(--color-text-primary);
}
</style>
