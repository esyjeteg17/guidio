<script setup lang="ts">
interface FontSpec {
	family: string
	google_fonts?: boolean
	category?: string
	weight?: number
	style?: string
	sample?: string
	available_weights?: number[]
}
interface FontPair {
	name: string
	heading: FontSpec
	body: FontSpec
	sample_title?: string
	sample_body?: string
	pangram?: string
	use_cases?: string[]
	mood?: string[]
	rationale?: string
}

const props = defineProps<{ pair: FontPair; index: number }>()

const categoryLabel: Record<string, string> = {
	serif: 'serif',
	'sans-serif': 'sans-serif',
	display: 'display',
	monospace: 'monospace',
	handwriting: 'handwritten',
}

const headingStack = computed(() =>
	props.pair.heading.category === 'sans-serif'
		? `'${props.pair.heading.family}', system-ui, sans-serif`
		: `'${props.pair.heading.family}', Georgia, serif`,
)
const bodyStack = computed(() =>
	props.pair.body.category === 'serif'
		? `'${props.pair.body.family}', Georgia, serif`
		: `'${props.pair.body.family}', system-ui, sans-serif`,
)

const defaultTitle = 'Живой заголовок'
const defaultBody =
	'Основной текст абзаца показывает, как пара работает в длинных текстах — баланс контраста и читаемости.'

function gfLink(family: string) {
	return `https://fonts.google.com/specimen/${encodeURIComponent(family.replace(/ /g, '+'))}`
}

function copy(text: string) {
	navigator.clipboard?.writeText(text)
}

const copiedWhich = ref<'' | 'h' | 'b'>('')
function copyFamily(which: 'h' | 'b', family: string) {
	copy(family)
	copiedWhich.value = which
	setTimeout(() => (copiedWhich.value = ''), 1200)
}

const sampleTitle = computed(() => props.pair.sample_title || defaultTitle)
const sampleBody = computed(() => props.pair.sample_body || defaultBody)

const headingWeight = ref(props.pair.heading.weight || 600)
const bodyWeight = ref(props.pair.body.weight || 400)
</script>

<template>
	<article class="card overflow-hidden">
		<!-- Header -->
		<div class="px-6 pt-6 pb-5 border-b border-ink-100">
			<div class="flex items-start justify-between gap-4 flex-wrap">
				<div class="min-w-0">
					<h3
						class="font-display text-lg font-semibold text-ink-900 leading-tight"
					>
						{{ pair.heading.family }} + {{ pair.body.family }}
					</h3>
				</div>
				<div class="flex items-center gap-1.5 shrink-0">
					<span class="chip">{{
						categoryLabel[pair.heading.category || ''] ||
						pair.heading.category ||
						'serif'
					}}</span>
					<span class="text-ink-300">+</span>
					<span class="chip">{{
						categoryLabel[pair.body.category || ''] ||
						pair.body.category ||
						'sans-serif'
					}}</span>
				</div>
			</div>
		</div>

		<!-- Two font columns -->
		<div
			class="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-ink-100"
		>
			<!-- Heading font -->
			<div class="p-6 flex flex-col">
				<div class="flex items-center justify-between mb-3">
					<div>
						<div
							class="text-[10px] uppercase tracking-widest text-ink-400 mb-1"
						>
							Заголовок
						</div>
						<div class="text-sm font-medium text-ink-900">
							{{ pair.heading.family }}
						</div>
					</div>
					<div class="flex items-center gap-1">
						<button
							class="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-50 cursor-pointer transition-colors"
							:title="
								copiedWhich === 'h' ? 'Скопировано' : 'Копировать название'
							"
							@click="copyFamily('h', pair.heading.family)"
						>
							<svg
								v-if="copiedWhich !== 'h'"
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<rect x="9" y="9" width="12" height="12" rx="2" />
								<path d="M5 15V5a2 2 0 0 1 2-2h10" />
							</svg>
							<svg
								v-else
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2.4"
								class="text-emerald-500"
							>
								<path d="m5 12 5 5L20 7" />
							</svg>
						</button>
						<a
							v-if="pair.heading.google_fonts"
							:href="gfLink(pair.heading.family)"
							target="_blank"
							rel="noopener"
							class="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-50 transition-colors"
							title="Google Fonts"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M7 17 17 7M7 7h10v10" />
							</svg>
						</a>
					</div>
				</div>

				<!-- Big preview Aa -->
				<div
					:style="{ fontFamily: headingStack, fontWeight: headingWeight }"
					class="text-[96px] leading-none text-ink-900 mb-4 select-none"
				>
					Aa
				</div>

				<!-- Начертания -->
				<div
					v-if="pair.heading.available_weights?.length"
					class="mt-auto flex flex-wrap gap-1"
				>
					<span class="text-[10px] text-ink-400 mr-1 mt-1">Начертания:</span>
					<button
						v-for="w in pair.heading.available_weights"
						:key="w"
						:style="{ fontFamily: headingStack, fontWeight: w }"
						class="text-xs px-2 py-0.5 rounded-full transition-colors cursor-pointer"
						:class="
							headingWeight === w
								? 'bg-ink-900 text-white'
								: 'bg-ink-50 text-ink-600 hover:bg-ink-100'
						"
						@click="headingWeight = w"
					>
						{{ w }}
					</button>
				</div>
			</div>

			<!-- Body font -->
			<div class="p-6 flex flex-col">
				<div class="flex items-center justify-between mb-3">
					<div>
						<div
							class="text-[10px] uppercase tracking-widest text-ink-400 mb-1"
						>
							Основной текст
						</div>
						<div class="text-sm font-medium text-ink-900">
							{{ pair.body.family }}
						</div>
					</div>
					<div class="flex items-center gap-1">
						<button
							class="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-50 cursor-pointer transition-colors"
							:title="
								copiedWhich === 'b' ? 'Скопировано' : 'Копировать название'
							"
							@click="copyFamily('b', pair.body.family)"
						>
							<svg
								v-if="copiedWhich !== 'b'"
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<rect x="9" y="9" width="12" height="12" rx="2" />
								<path d="M5 15V5a2 2 0 0 1 2-2h10" />
							</svg>
							<svg
								v-else
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2.4"
								class="text-emerald-500"
							>
								<path d="m5 12 5 5L20 7" />
							</svg>
						</button>
						<a
							v-if="pair.body.google_fonts"
							:href="gfLink(pair.body.family)"
							target="_blank"
							rel="noopener"
							class="p-1.5 rounded-lg text-ink-400 hover:text-ink-700 hover:bg-ink-50 transition-colors"
							title="Google Fonts"
						>
							<svg
								width="13"
								height="13"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M7 17 17 7M7 7h10v10" />
							</svg>
						</a>
					</div>
				</div>

				<div
					:style="{ fontFamily: bodyStack, fontWeight: bodyWeight }"
					class="text-[72px] leading-none text-ink-900 mb-4 select-none"
				>
					Aa
				</div>

				<div
					v-if="pair.body.available_weights?.length"
					class="mt-auto flex flex-wrap gap-1"
				>
					<span class="text-[10px] text-ink-400 mr-1 mt-1">Начертания:</span>
					<button
						v-for="w in pair.body.available_weights"
						:key="w"
						:style="{ fontFamily: bodyStack, fontWeight: w }"
						class="text-xs px-2 py-0.5 rounded-full transition-colors cursor-pointer"
						:class="
							bodyWeight === w
								? 'bg-ink-900 text-white'
								: 'bg-ink-50 text-ink-600 hover:bg-ink-100'
						"
						@click="bodyWeight = w"
					>
						{{ w }}
					</button>
				</div>
			</div>
		</div>

		<!-- Live layout preview -->
		<div class="p-6 border-t border-ink-100 bg-ink-50/40">
			<div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">
				Живой макет
			</div>
			<div class="bg-white rounded-2xl p-7 ring-1 ring-ink-100">
				<div
					:style="{ fontFamily: headingStack, fontWeight: headingWeight }"
					class="text-[32px] leading-tight text-ink-900 mb-4"
				>
					{{ sampleTitle }}
				</div>
				<div
					:style="{ fontFamily: bodyStack, fontWeight: bodyWeight }"
					class="text-[15px] text-ink-800 leading-[1.7] mb-5 max-w-2xl"
				>
					{{ sampleBody }}
				</div>
				<button
					:style="{ fontFamily: bodyStack, fontWeight: 500 }"
					class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full bg-ink-900 text-white text-sm cursor-default"
				>
					Подробнее
					<svg
						width="13"
						height="13"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M5 12h14M13 6l6 6-6 6" />
					</svg>
				</button>
			</div>
		</div>

		<!-- Tags + rationale -->
		<div class="p-6 pt-5 space-y-4">
			<div
				v-if="pair.use_cases?.length"
				class="flex items-start gap-3 flex-wrap"
			>
				<span
					class="text-[11px] text-ink-400 uppercase tracking-wider mt-1 min-w-28"
					>Подходит для</span
				>
				<div class="flex flex-wrap gap-1.5">
					<span v-for="u in pair.use_cases" :key="u" class="chip">{{ u }}</span>
				</div>
			</div>
			<div v-if="pair.mood?.length" class="flex items-start gap-3 flex-wrap">
				<span
					class="text-[11px] text-ink-400 uppercase tracking-wider mt-1 min-w-28"
					>Характер</span
				>
				<div class="flex flex-wrap gap-1.5">
					<span
						v-for="m in pair.mood"
						:key="m"
						class="chip bg-accent-50 text-accent-700 ring-1 ring-accent-100"
						>{{ m }}</span
					>
				</div>
			</div>
			<div v-if="pair.rationale" class="flex items-start gap-3">
				<span
					class="text-[11px] text-ink-400 uppercase tracking-wider mt-1 min-w-28 shrink-0"
					>Почему подходит</span
				>
				<p class="text-sm text-ink-700 leading-relaxed">{{ pair.rationale }}</p>
			</div>
		</div>
	</article>
</template>
