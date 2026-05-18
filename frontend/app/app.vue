<script setup lang="ts">
import { useAuthStore } from '~/stores/auth'

const auth = useAuthStore()
await useAsyncData('auth-init', () => auth.bootstrap())
</script>

<template>
  <NuxtLayout>
    <NuxtPage />
  </NuxtLayout>
</template>
