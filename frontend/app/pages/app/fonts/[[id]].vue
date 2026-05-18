<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Подбор шрифтов — Guidio' })
</script>

<template>
  <ChatShell mode="fonts" title="Подбор шрифтов"
             description="Парные шрифты и примеры использования. Уточняйте настроение в диалоге."
             base-path="/app/fonts" />
</template>
