<template>
  <header class="app-header">
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
  background: rgba(247, 244, 237, 0.92);
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
  border-bottom: 1px solid var(--color-border);
  margin-bottom: var(--spacing-xl);
}

.header-content {
  height: 60px;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  display: flex;
  align-items: center;
  gap: var(--spacing-sm);
  font-family: var(--font-family-serif);
  font-weight: 700;
  font-size: 1.25rem;
  margin-right: var(--spacing-xl);
  color: var(--color-text-primary);
  text-decoration: none;
}

.logo-icon {
  color: var(--color-accent-primary);
  font-size: 22px;
}

.logo-text {
  color: var(--color-text-primary);
  letter-spacing: 0.02em;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-xl);
}

.nav-links {
  display: flex;
  gap: var(--spacing-sm);
}

.nav-link {
  color: var(--color-text-secondary);
  font-size: 0.875rem;
  font-weight: 500;
  transition: color var(--transition-fast);
  padding: 6px 14px;
  border-radius: var(--radius-sm);
  text-decoration: none;
}

.nav-link:hover {
  color: var(--color-text-primary);
  background: var(--color-bg-tertiary);
}

.nav-link.active {
  color: var(--color-accent-primary);
  background: rgba(196, 30, 58, 0.06);
}

.github-link {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.875rem;
  color: var(--color-text-tertiary);
  transition: color var(--transition-fast);
  text-decoration: none;
}

.github-link:hover {
  color: var(--color-text-primary);
}

/* Responsive */
@media (max-width: 768px) {
  .header-content {
    height: 52px;
    padding: 0 var(--spacing-md);
  }

  .logo {
    font-size: 1rem;
    margin-right: var(--spacing-md);
  }

  .logo-icon {
    font-size: 18px;
  }

  .logo-text {
    display: none;
  }

  .header-actions {
    gap: var(--spacing-sm);
  }

  .nav-links {
    gap: 2px;
  }

  .nav-link {
    font-size: 0.75rem;
    padding: 4px 8px;
  }

  .github-link {
    font-size: 0.75rem;
  }
}

@media (max-width: 480px) {
  .logo-text {
    display: inline;
    font-size: 0.875rem;
  }

  .nav-link {
    font-size: 0.7rem;
    white-space: nowrap;
  }
}
</style>
