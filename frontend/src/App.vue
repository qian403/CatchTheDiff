<template>
  <div class="app-layout">
    <AppHeader />
    <main class="container">
      <router-view v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </router-view>
    </main>
  </div>
</template>

<script setup lang="ts">
import AppHeader from './components/AppHeader.vue';
</script>

<style>
.app-layout {
  min-height: 100vh;
  background-color: var(--color-bg-primary);
}
</style>
