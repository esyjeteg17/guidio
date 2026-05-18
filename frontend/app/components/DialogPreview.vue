<script setup lang="ts">
const recent = [
  'Технологичный бренд',
  'Шрифт для эко-стартапа',
  'Мудборд fashion-концеп...',
]
</script>

<template>
  <div class="card overflow-hidden">
    <div class="grid lg:grid-cols-[240px_1fr]">
      <!-- Mock sidebar -->
      <aside class="bg-ink-50/60 border-r border-ink-100 p-3 text-xs flex flex-col gap-3">
        <div class="relative">
          <svg class="absolute left-2.5 top-1/2 -translate-y-1/2 text-ink-400" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>
          <div class="w-full rounded-lg bg-white px-7 py-2 text-ink-400 ring-1 ring-ink-100">Поиск по проектам...</div>
        </div>
        <div class="w-full rounded-lg bg-white px-3 py-2 text-ink-700 ring-1 ring-ink-200 flex items-center gap-1.5">
          <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 5v14M5 12h14"/></svg>
          Новый подбор
          <span class="ml-auto text-ink-400">▾</span>
        </div>

        <div>
          <div class="text-[9px] font-semibold tracking-widest text-ink-400 uppercase mb-1.5 mt-1">Рабочее пространство</div>
          <div class="space-y-0.5">
            <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-md bg-ink-100 text-ink-900">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>
              Стартовая страница
            </div>
            <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-ink-500">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 7a2 2 0 0 1 2-2h5l2 2h7a2 2 0 0 1 2 2v9a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2Z"/></svg>
              Мои проекты
            </div>
            <div class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-ink-500">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="9" cy="8" r="3"/><path d="M3 20v-1a6 6 0 0 1 12 0v1"/></svg>
              Команда
            </div>
          </div>
        </div>

        <div>
          <div class="text-[9px] font-semibold tracking-widest text-ink-400 uppercase mb-1.5 mt-1">Недавние сессии</div>
          <div class="space-y-0.5">
            <div v-for="r in recent" :key="r" class="flex items-center gap-1.5 px-2 py-1.5 rounded-md text-ink-500">
              <svg width="11" height="11" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a4 4 0 0 1-4 4H8l-5 3V6a4 4 0 0 1 4-4h10a4 4 0 0 1 4 4Z"/></svg>
              <span class="truncate">{{ r }}</span>
            </div>
          </div>
        </div>
      </aside>

      <!-- Mock main -->
      <div class="p-8 lg:p-12">
        <div class="text-center mb-8">
          <h3 class="font-display text-2xl font-semibold text-ink-900">Что вы хотите создать сегодня?</h3>
          <p class="mt-3 text-sm text-ink-500 max-w-md mx-auto">Вы можете выбрать готовый сценарий работы или просто описать задачу своими словами.</p>
        </div>

        <div class="grid sm:grid-cols-2 gap-4 max-w-[640px] mx-auto">
          <button class="card-flat p-4 text-left group hover:shadow-soft transition-shadow">
            <div class="aspect-[5/3] rounded-xl bg-ink-50 flex items-center justify-center mb-4 relative overflow-hidden">
              <div class="absolute left-6 top-6 h-10 w-7 rounded-md bg-linear-to-br from-bloom-lilac to-bloom-peri rotate-[-10deg]" />
              <div class="absolute left-14 top-10 h-12 w-10 rounded-md bg-linear-to-br from-accent-300 to-accent-500" />
              <div class="absolute right-6 top-6 h-10 w-10 rounded-md bg-linear-to-br from-bloom-pink to-accent-400 rotate-[12deg]" />
              <div class="absolute left-1/2 bottom-4 -translate-x-1/2 h-7 w-7 rounded-full bg-white ring-2 ring-accent-400 flex items-center justify-center text-accent-600">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="9"/><circle cx="8" cy="10" r="1.3" fill="currentColor"/><circle cx="16" cy="10" r="1.3" fill="currentColor"/><circle cx="12" cy="16" r="1.3" fill="currentColor"/></svg>
              </div>
            </div>
            <div class="font-display font-semibold text-ink-900">Генерация мудборда</div>
            <div class="text-xs text-ink-500 mt-1 leading-relaxed">Соберите визуальное направление, референсы и цветовую палитру по краткому описанию вашего проекта.</div>
          </button>

          <button class="card-flat p-4 text-left group hover:shadow-soft transition-shadow">
            <div class="aspect-[5/3] rounded-xl bg-ink-50 flex items-center justify-center mb-4 relative">
              <span class="font-display text-[72px] leading-none text-ink-800 mr-1">A</span>
              <span class="font-display italic text-[68px] leading-none text-accent-500">a</span>
              <span class="chip-white absolute bottom-3 right-3 !py-1 !px-2 !text-[10px] gap-1">
                <svg width="10" height="10" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M4 7V5h16v2M9 5v14M9 19h6M15 5v14"/></svg>
                AI Подбор
              </span>
            </div>
            <div class="font-display font-semibold text-ink-900">Подбор шрифтов</div>
            <div class="text-xs text-ink-500 mt-1 leading-relaxed">Найдите идеальную типографику под характер, стиль и настроение вашего бренда за пару секунд.</div>
          </button>
        </div>

        <div class="mt-6 max-w-[640px] mx-auto card-flat px-4 py-3 flex items-center gap-3">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" class="text-accent-500"><path d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z"/></svg>
          <div class="flex-1 text-sm text-ink-400">Опишите задачу своими словами…</div>
          <button class="h-8 w-8 rounded-full bg-accent-500 text-white flex items-center justify-center">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2"><path d="M12 19V5M5 12l7-7 7 7"/></svg>
          </button>
        </div>
      </div>
    </div>
  </div>
</template>
