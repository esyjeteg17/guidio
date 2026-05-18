<script setup lang="ts">
import { useApi } from '~/composables/useApi'

interface CreatedProject {
	id: number
	kind: string
}

const props = withDefaults(
	defineProps<{
		open: boolean
		defaultKind?: 'fonts' | 'moodboard' | 'mixed'
		title?: string
		description?: string
	}>(),
	{
		defaultKind: 'fonts',
		title: 'Новый проект',
		description: 'Название можно изменить позже.',
	},
)

const emit = defineEmits<{
	(e: 'update:open', value: boolean): void
	(e: 'created', project: CreatedProject): void
}>()

const api = useApi()

const name = ref('Новый проект')
const creating = ref(false)
const error = ref<string | null>(null)
const inputRef = ref<HTMLInputElement | null>(null)

function close() {
	if (creating.value) return
	emit('update:open', false)
}

async function submit() {
	const trimmed = name.value.trim() || 'Новый проект'
	creating.value = true
	error.value = null
	try {
		const created = await api.post<CreatedProject>('/projects/', {
			name: trimmed,
			kind: props.defaultKind,
		})
		emit('created', created)
		emit('update:open', false)
	} catch (e: any) {
		error.value = e?.data?.detail || 'Не удалось создать проект'
	} finally {
		creating.value = false
	}
}

watch(
	() => props.open,
	async v => {
		if (!v) return
		name.value = 'Новый проект'
		error.value = null
		await nextTick()
		inputRef.value?.select()
	},
)
</script>

<template>
	<div
		v-if="open"
		class="fixed inset-0 z-50 bg-ink-900/40 backdrop-blur-sm flex items-center justify-center p-4"
		@click.self="close"
	>
		<div class="card w-full max-w-sm p-6">
			<h3 class="font-display text-xl font-semibold text-ink-900 mb-1">
				{{ title }}
			</h3>
			<p class="text-xs text-ink-500 mb-5">{{ description }}</p>
			<input
				ref="inputRef"
				v-model="name"
				class="w-full text-sm rounded-xl bg-ink-50 px-4 py-3 ring-1 ring-ink-200 focus:outline-none focus:ring-accent-400 text-ink-900"
				placeholder="Новый проект"
				@keydown.enter="submit"
				@keydown.esc="close"
			/>
			<p v-if="error" class="text-sm text-red-500 mt-2">{{ error }}</p>
			<div class="flex gap-2 mt-4 justify-end">
				<button class="btn-secondary" :disabled="creating" @click="close">
					Отмена
				</button>
				<button
					class="btn-accent rounded-full!"
					:disabled="creating"
					@click="submit"
				>
					{{ creating ? 'Создаём…' : 'Создать' }}
				</button>
			</div>
		</div>
	</div>
</template>
