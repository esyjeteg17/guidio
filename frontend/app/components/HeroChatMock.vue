<script setup lang="ts"></script>

<template>
  <div class="card p-4 sm:p-6 text-left shadow-card">
    <div class="flex items-center gap-3 pb-4 border-b border-ink-100">
      <img src="/logo.svg" alt="" class="h-8 w-8" />
      <div>
        <div class="text-sm font-semibold text-ink-800">Guidio</div>
        <div class="text-xs text-ink-400">AI-подбор стилевых решений</div>
      </div>
      <div class="ml-auto chip">online</div>
    </div>

    <div class="py-5 space-y-4">
      <div class="flex justify-end">
        <div class="max-w-[80%] rounded-2xl rounded-tr-sm bg-ink-900 text-white px-4 py-3 text-sm">
          Нужна типографика для лендинга про нейросети — современная, тёплая
        </div>
      </div>

      <div class="flex justify-start">
        <div class="max-w-[80%] rounded-2xl rounded-tl-sm bg-ink-100 text-ink-800 px-4 py-3 text-sm">
          Отличный запрос! Предлагаю пару <strong>Manrope + Inter</strong> и <strong>Space Grotesk + Unbounded</strong> — обе читаемы на экране и поддерживают кириллицу.
        </div>
      </div>

      <div class="grid sm:grid-cols-2 gap-3">
        <div class="rounded-xl p-4 bg-ink-50 ring-1 ring-ink-100">
          <div class="text-xs text-ink-400 mb-1">Заголовки</div>
          <div class="font-display text-2xl font-bold text-ink-900">Manrope</div>
          <div class="text-xs text-ink-400 mt-3 mb-1">Основной текст</div>
          <div class="text-base text-ink-800">Inter</div>
        </div>
        <div class="rounded-xl p-4 bg-gradient-to-br from-bloom-lilac/40 to-bloom-pink/40 ring-1 ring-white">
          <div class="text-xs text-ink-500 mb-1">Заголовки</div>
          <div class="font-display text-2xl font-bold text-ink-900">Unbounded</div>
          <div class="text-xs text-ink-500 mt-3 mb-1">Основной текст</div>
          <div class="text-base text-ink-800">Space Grotesk</div>
        </div>
      </div>
    </div>

    <div class="pt-3 border-t border-ink-100 flex items-center gap-2">
      <input disabled placeholder="Опишите свой проект…" class="input flex-1" />
      <button class="btn-primary !px-4" disabled>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <path d="M5 12h14M13 6l6 6-6 6" />
        </svg>
      </button>
    </div>
  </div>
</template>
