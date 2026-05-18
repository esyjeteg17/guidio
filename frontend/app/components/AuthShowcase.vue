<script setup lang="ts">
const palette = ['#0e1018', '#4f5dff', '#f6cfe4', '#c8f0e0', '#fdf5ec']
</script>

<template>
  <div class="relative h-full overflow-hidden bloom-right">
    <!-- декоративная сетка из тонких засечек -->
    <svg class="absolute inset-0 w-full h-full opacity-[0.05] pointer-events-none" aria-hidden="true">
      <defs>
        <pattern id="authGrid" width="56" height="56" patternUnits="userSpaceOnUse">
          <path d="M56 0H0V56" fill="none" stroke="currentColor" stroke-width="0.6" />
        </pattern>
      </defs>
      <rect width="100%" height="100%" fill="url(#authGrid)" class="text-ink-900" />
    </svg>

    <div class="relative h-full flex flex-col justify-between p-12 xl:p-16">
      <!-- Top: бренд -->
      <div class="text-sm text-ink-500">
        <span class="inline-flex items-center gap-2">
          <span class="relative flex h-1.5 w-1.5">
            <span class="absolute inline-flex h-full w-full rounded-full bg-accent-400 opacity-60 animate-ping" />
            <span class="relative inline-flex rounded-full h-1.5 w-1.5 bg-accent-500" />
          </span>
          Guidio · AI помощник для дизайнеров
        </span>
      </div>

      <!-- Center: большая буква + плавающие карточки -->
      <div class="flex-1 relative flex items-center justify-center">
        <!-- главный типографический объект -->
        <div class="relative select-none">
          <div class="font-display text-ink-900 leading-none text-[180px] xl:text-[220px]">Aa</div>
          <span class="hand absolute -bottom-4 right-0" style="font-size: 72px; line-height: 1;">стиль</span>

          <!-- тонкая направляющая вокруг буквы -->
          <svg class="absolute -top-6 -left-8 text-ink-300/70" width="40" height="40" viewBox="0 0 40 40" fill="none" aria-hidden="true">
            <path d="M2 20C2 10 10 2 20 2" stroke="currentColor" stroke-width="1" stroke-dasharray="2 4" stroke-linecap="round" />
          </svg>
          <svg class="absolute -bottom-2 -right-12 text-ink-300/70" width="48" height="24" viewBox="0 0 48 24" fill="none" aria-hidden="true">
            <path d="M2 22C14 22 22 12 46 2" stroke="currentColor" stroke-width="1" stroke-dasharray="2 4" stroke-linecap="round" />
          </svg>
        </div>

        <!-- карточка: палитра -->
        <div class="absolute top-4 left-0 xl:-left-4 card px-4 py-3 float-chip" style="transform: rotate(-4deg);">
          <div class="text-[11px] text-ink-500 mb-2 tracking-wide uppercase">Палитра</div>
          <div class="flex items-center gap-1.5">
            <span
              v-for="c in palette"
              :key="c"
              class="h-5 w-5 rounded-full ring-1 ring-black/5"
              :style="{ background: c }"
            />
          </div>
        </div>

        <!-- карточка: шрифтовая пара -->
        <div class="absolute bottom-6 right-0 xl:-right-6 card px-4 py-3 float-chip float-chip-delay-2" style="transform: rotate(3deg);">
          <div class="text-[11px] text-ink-500 mb-1 tracking-wide uppercase">Шрифтовая пара</div>
          <div class="flex items-baseline gap-3">
            <span class="font-display text-2xl text-ink-900 leading-none">Lora</span>
            <span class="text-[11px] text-ink-400">+</span>
            <span class="text-lg font-medium text-ink-900 leading-none">Inter</span>
          </div>
        </div>

      </div>

      <!-- Bottom: тэглайн + мини-пруф -->
      <div class="flex items-end justify-between gap-6">
        <div class="max-w-md">
          <div class="font-display text-2xl xl:text-3xl font-semibold text-ink-900 leading-snug">
            Инструмент выбора <br />
            <span class="text-ink-500">стилевых решений</span>
          </div>
        </div>

        <div class="hidden xl:flex items-center gap-2 text-[11px] text-ink-500">
          <span class="h-px w-8 bg-ink-300" />
          для дизайнеров, арт-директоров и студий
        </div>
      </div>
    </div>
  </div>
</template>
