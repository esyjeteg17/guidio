<script setup lang="ts">
const props = defineProps<{ mode: string }>()

const modeLabel = computed(() => {
	if (props.mode === 'fonts') return 'Подбор шрифтов'
	if (props.mode === 'moodboard') return 'Генерация мудборда'
	return 'Подбор'
})

const phases: Record<string, string[]> = {
	fonts: [
		'Анализируем ваш запрос…',
		'Подбираем контрастные пары…',
		'Проверяем кириллическую поддержку…',
		'Оформляем ответ…',
	],
	moodboard: [
		'Анализируем ваш запрос…',
		'Собираем визуальное направление…',
		'Подбираем палитру и референсы…',
		'Оформляем ответ…',
	],
	default: ['Анализируем ваш запрос…', 'Формируем ответ…', 'Почти готово…'],
}

const currentPhase = ref(0)
let timer: ReturnType<typeof setInterval> | null = null

function getPhases() {
	return phases[props.mode] ?? phases.default!
}

onMounted(() => {
	timer = setInterval(() => {
		const list = getPhases()
		currentPhase.value = Math.min(currentPhase.value + 1, list.length - 1)
	}, 3200)
})
onBeforeUnmount(() => {
	if (timer) clearInterval(timer)
})

const phaseText = computed(() => {
	const list = getPhases()
	return list[currentPhase.value] ?? list[0] ?? ''
})
</script>

<template>
	<div class="flex justify-start">
		<div class="flex gap-3 w-full">
			<div class="flex-1 card p-5 space-y-4 min-w-0">
				<!-- Header -->
				<div class="flex items-center gap-2 text-xs">
					<img src="/logo.svg" alt="" class="h-6 w-6 pulse-dot rounded-md" />
					<span class="font-semibold text-ink-900">Guidio AI</span>
					<span class="chip">{{ modeLabel }}</span>
				</div>

				<!-- Phase -->
				<div class="flex items-center gap-3 text-sm text-ink-600">
					<div class="typing-dots flex gap-1"><span /><span /><span /></div>
					<Transition
						mode="out-in"
						enter-active-class="transition duration-200"
						enter-from-class="opacity-0 translate-y-1"
						leave-active-class="transition duration-150"
						leave-to-class="opacity-0 -translate-y-1"
					>
						<span :key="phaseText">{{ phaseText }}</span>
					</Transition>
				</div>

				<!-- Fonts skeleton -->
				<div v-if="mode === 'fonts'" class="space-y-3">
					<div class="card-flat p-5 space-y-4">
						<div class="flex items-center justify-between">
							<div class="h-3 w-32 rounded shimmer" />
							<div class="h-4 w-20 rounded-full shimmer" />
						</div>
						<div class="grid md:grid-cols-2 gap-3">
							<div class="card-flat p-4 space-y-3">
								<div class="h-3 w-20 rounded shimmer" />
								<div class="h-4 w-28 rounded shimmer" />
								<div class="h-16 w-20 rounded-lg shimmer" />
								<div class="h-3 w-full rounded shimmer" />
								<div class="h-3 w-5/6 rounded shimmer" />
								<div class="flex gap-1 pt-1">
									<div class="h-5 w-8 rounded-full shimmer" />
									<div class="h-5 w-8 rounded-full shimmer" />
									<div class="h-5 w-8 rounded-full shimmer" />
								</div>
							</div>
							<div class="card-flat p-4 space-y-3">
								<div class="h-3 w-24 rounded shimmer" />
								<div class="h-4 w-28 rounded shimmer" />
								<div class="h-14 w-16 rounded-lg shimmer" />
								<div class="h-3 w-full rounded shimmer" />
								<div class="h-3 w-4/5 rounded shimmer" />
								<div class="flex gap-1 pt-1">
									<div class="h-5 w-8 rounded-full shimmer" />
									<div class="h-5 w-8 rounded-full shimmer" />
								</div>
							</div>
						</div>
					</div>
				</div>

				<!-- Moodboard skeleton -->
				<div v-else-if="mode === 'moodboard'" class="space-y-4">
					<div class="grid grid-cols-2 md:grid-cols-3 gap-2.5">
						<div
							v-for="i in 6"
							:key="i"
							class="aspect-4/3 rounded-2xl shimmer"
							:style="{ animationDelay: `${i * 80}ms` }"
						/>
					</div>
					<div class="space-y-2">
						<div class="flex gap-1.5">
							<div
								v-for="i in 5"
								:key="i"
								class="flex-1 aspect-square rounded-xl shimmer"
								:style="{ animationDelay: `${i * 100}ms` }"
							/>
						</div>
						<div class="h-2 rounded-full shimmer" />
					</div>
					<div class="flex flex-wrap gap-1.5">
						<div
							v-for="i in 4"
							:key="i"
							class="h-6 w-16 rounded-full shimmer"
						/>
					</div>
				</div>

				<!-- Generic skeleton -->
				<div v-else class="space-y-2">
					<div class="h-3 w-full rounded shimmer" />
					<div class="h-3 w-5/6 rounded shimmer" />
					<div class="h-3 w-3/4 rounded shimmer" />
				</div>
			</div>
		</div>
	</div>
</template>
