<template>
  <div class="app-layout">
    <AppHeader />
    <main class="container">
      <router-view v-slot="{ Component, route }">
        <transition name="fade" mode="out-in">
          <component :is="Component" :key="route.path" />
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
  background: transparent;
}
</style>
