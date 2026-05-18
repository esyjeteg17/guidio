<script setup lang="ts">
definePageMeta({ layout: 'app', middleware: 'auth' })
useHead({ title: 'Мудборд — Guidio' })
</script>

<template>
  <ChatShell mode="moodboard" title="Мудборд"
             description="Концепция + референсы + палитра. Опишите проект — сгенерируем направление."
             base-path="/app/moodboard" />
</template>
