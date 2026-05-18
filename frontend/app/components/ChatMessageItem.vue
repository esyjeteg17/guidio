<script setup lang="ts">
import { useApi } from '~/composables/useApi'
import type { ChatMessage } from '~/composables/useChat'

const props = defineProps<{
	message: ChatMessage
	mode: string
	projectId?: number | null
}>()
const api = useApi()

const modeLabel = computed(() => {
	if (props.mode === 'fonts') return 'Подбор шрифтов'
	if (props.mode === 'moodboard') return 'Генерация мудборда'
	return 'Подбор'
})

const reactionMap: Record<string, boolean | null> = {
	like: true,
	dislike: false,
}
const liked = ref<boolean | null>(
	props.message.reaction != null
		? (reactionMap[props.message.reaction] ?? null)
		: null,
)

async function toggleLike(val: boolean) {
	const next = liked.value === val ? null : val
	liked.value = next
	if (props.message.role !== 'assistant') return
	const reaction = next === true ? 'like' : next === false ? 'dislike' : ''
	try {
		await api.patch(`/ai/messages/${props.message.id}/reaction/`, { reaction })
	} catch {
		/* ignore */
	}
}
</script>

<template>
	<div>
		<!-- User message -->
		<div v-if="props.message.role === 'user'" class="flex justify-end">
			<div
				class="max-w-[80%] rounded-2xl bg-ink-100 text-ink-800 px-5 py-3 text-sm whitespace-pre-wrap"
			>
				{{ props.message.content }}
			</div>
		</div>

		<!-- Assistant message -->
		<div v-else class="flex justify-start">
			<div class="flex gap-3 max-w-full w-full">
				<div class="flex-1 card p-5 space-y-4 min-w-0">
					<div class="flex items-center gap-2 text-xs">
						<img src="/logo.svg" alt="" class="h-6 w-6" />
						<span class="font-semibold text-ink-900">Guidio AI</span>
						<span class="chip">{{ modeLabel }}</span>
					</div>

					<div class="text-sm text-ink-800 whitespace-pre-wrap leading-relaxed">
						{{ props.message.content }}
					</div>

					<template v-if="props.message.payload">
						<FontsResult
							v-if="
								props.mode === 'fonts' && props.message.payload.pairs?.length
							"
							:payload="props.message.payload"
						/>
						<MoodboardResult
							v-else-if="
								(props.mode === 'moodboard' || props.mode === 'colors') &&
								(props.message.payload.palette?.length ||
									props.message.payload.references?.length ||
									props.message.payload.theme)
							"
							:payload="props.message.payload"
							:project-id="props.projectId"
						/>
					</template>
				</div>

				<!-- Side actions -->
				<div class="flex flex-col gap-1 text-ink-400 shrink-0 pt-3">
					<button
						class="p-1.5 rounded-lg hover:bg-ink-50 transition-colors"
						:class="liked === true ? 'text-emerald-500' : 'hover:text-ink-700'"
						title="Нравится"
						@click="toggleLike(true)"
					>
						<svg
							width="15"
							height="15"
							viewBox="0 0 24 24"
							:fill="liked === true ? 'currentColor' : 'none'"
							stroke="currentColor"
							stroke-width="1.8"
						>
							<path
								d="M7 22V11M14 5.5 13 10h6.5a2 2 0 0 1 2 2.3l-1.1 7a2 2 0 0 1-2 1.7H7V11l5-9a2 2 0 0 1 2 2.5Z"
							/>
						</svg>
					</button>
					<button
						class="p-1.5 rounded-lg hover:bg-ink-50 transition-colors"
						:class="liked === false ? 'text-red-400' : 'hover:text-ink-700'"
						title="Не нравится"
						@click="toggleLike(false)"
					>
						<svg
							width="15"
							height="15"
							viewBox="0 0 24 24"
							:fill="liked === false ? 'currentColor' : 'none'"
							stroke="currentColor"
							stroke-width="1.8"
						>
							<path
								d="M17 2v11M10 18.5 11 14H4.5a2 2 0 0 1-2-2.3l1.1-7A2 2 0 0 1 5.6 3H17v11l-5 9a2 2 0 0 1-2-2.5Z"
							/>
						</svg>
					</button>
				</div>
			</div>
		</div>
	</div>
</template>
