<script setup lang="ts">
interface FontSpec {
	family: string
	google_fonts?: boolean
	category?: string
	weight?: number
	available_weights?: number[]
}
interface SummaryPayload {
	overview?: string
	direction?: string
	recommended_fonts?: {
		heading?: FontSpec
		body?: FontSpec
		rationale?: string
	}
	recommended_palette?: Array<{
		hex: string
		name?: string
		role?: string
		usage_percent?: number
	}>
	mood?: string[]
	key_principles?: string[]
	mockup?: {
		title?: string
		subtitle?: string
		body?: string
		cta?: string
	}
	next_steps?: string[]
}

const props = defineProps<{
	summary: SummaryPayload | null
	generatedAt: string | null
	loading?: boolean
}>()

const emit = defineEmits<{ regenerate: [] }>()

const roleLabel: Record<string, string> = {
	primary: 'основной',
	secondary: 'вторичный',
	accent: 'акцент',
	neutral: 'нейтральный',
	background: 'фон',
	text: 'текст',
}

const gfHref = computed(() => {
	const fonts = props.summary?.recommended_fonts
	if (!fonts) return ''
	const families = new Map<string, Set<number>>()
	for (const spec of [fonts.heading, fonts.body]) {
		if (!spec?.google_fonts || !spec.family) continue
		const set = families.get(spec.family) ?? new Set<number>()
		if (spec.weight) set.add(spec.weight)
		;(spec.available_weights || []).forEach(w => set.add(w))
		;[400, 500, 600, 700].forEach(w => set.add(w))
		families.set(spec.family, set)
	}
	if (!families.size) return ''
	const parts = [...families.entries()].map(([fam, weights]) => {
		const w = [...weights].sort((a, b) => a - b)
		return `family=${fam.replace(/ /g, '+')}:wght@${w.join(';')}`
	})
	return `https://fonts.googleapis.com/css2?${parts.join('&')}&display=swap`
})

useHead(() =>
	gfHref.value
		? {
				link: [
					{
						key: `summary-${gfHref.value}`,
						rel: 'stylesheet',
						href: gfHref.value,
					},
				],
			}
		: {},
)

const headingStack = computed(() => {
	const f = props.summary?.recommended_fonts?.heading
	if (!f) return 'Georgia, serif'
	return f.category === 'sans-serif'
		? `'${f.family}', system-ui, sans-serif`
		: `'${f.family}', Georgia, serif`
})
const bodyStack = computed(() => {
	const f = props.summary?.recommended_fonts?.body
	if (!f) return 'system-ui, sans-serif'
	return f.category === 'serif'
		? `'${f.family}', Georgia, serif`
		: `'${f.family}', system-ui, sans-serif`
})

const palette = computed(() => props.summary?.recommended_palette || [])

function paletteColor(role: string, fallback: string): string {
	const c = palette.value.find(x => x.role === role)
	return c?.hex || fallback
}

/* ----------------------- WCAG contrast helpers ----------------------- */
function hexToRgb(hex: string): [number, number, number] | null {
	const h = (hex || '').replace('#', '')
	if (h.length !== 6) return null
	const r = parseInt(h.slice(0, 2), 16)
	const g = parseInt(h.slice(2, 4), 16)
	const b = parseInt(h.slice(4, 6), 16)
	if ([r, g, b].some(Number.isNaN)) return null
	return [r, g, b]
}
/** Смешать два цвета (t=0 → a, t=1 → b). Для мягких подложек-surface. */
function mix(a: string, b: string, t: number): string {
	const ra = hexToRgb(a)
	const rb = hexToRgb(b)
	if (!ra || !rb) return a
	const m = ra.map((v, i) => Math.round(v + (rb[i] - v) * t))
	return '#' + m.map(v => v.toString(16).padStart(2, '0')).join('')
}
function relLuminance(hex: string): number {
	const rgb = hexToRgb(hex)
	if (!rgb) return 0
	const [r, g, b] = rgb.map(v => v / 255) as [number, number, number]
	const lin = (c: number) =>
		c <= 0.03928 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4)
	return 0.2126 * lin(r) + 0.7152 * lin(g) + 0.0722 * lin(b)
}
function contrastRatio(a: string, b: string): number {
	const la = relLuminance(a)
	const lb = relLuminance(b)
	const lighter = Math.max(la, lb)
	const darker = Math.min(la, lb)
	return (lighter + 0.05) / (darker + 0.05)
}
function pickReadable(
	background: string,
	candidates: string[],
	minRatio = 4.5,
): string {
	const valid = candidates.filter(Boolean)
	for (const c of valid) {
		if (contrastRatio(c, background) >= minRatio) return c
	}
	// Не нашли среди палитры — выбираем чёрный или белый.
	const black = '#0E1018'
	const white = '#FFFFFF'
	return contrastRatio(black, background) >= contrastRatio(white, background)
		? black
		: white
}

const colors = computed(() => {
	const bg = paletteColor('background', '#ffffff')
	// Кандидаты на цвет основного текста — в порядке приоритета.
	const textCandidates = [
		paletteColor('text', ''),
		paletteColor('primary', ''),
		paletteColor('secondary', ''),
		paletteColor('accent', ''),
		paletteColor('neutral', ''),
	]
	const text = pickReadable(bg, textCandidates)
	// Кандидаты на цвет заголовка-акцента: сначала primary, потом другие
	// "выразительные" цвета. Тоже фильтруем по контрасту.
	const headingCandidates = [
		paletteColor('primary', ''),
		paletteColor('accent', ''),
		paletteColor('secondary', ''),
		paletteColor('text', ''),
	]
	const primary = pickReadable(bg, headingCandidates, 3.0) // AA Large для крупного title

	// Подбираем два РАЗНЫХ выразительных цвета (accent / secondary) из палитры,
	// не совпадающих с фоном и заголовком — чтобы в макете работал не один цвет.
	const used = new Set([bg.toLowerCase(), primary.toLowerCase()])
	const distinct = (roles: string[]): string => {
		for (const r of roles) {
			const h = paletteColor(r, '')
			if (h && !used.has(h.toLowerCase())) {
				used.add(h.toLowerCase())
				return h
			}
		}
		for (const c of palette.value) {
			const h = c.hex
			if (h && !used.has(h.toLowerCase())) {
				used.add(h.toLowerCase())
				return h
			}
		}
		return primary
	}
	const accent = distinct(['accent', 'secondary', 'primary'])
	const secondary = distinct(['secondary', 'accent', 'neutral'])

	// Мягкая подложка для карточек: нейтральный цвет, если он заметно отличается
	// от фона, иначе лёгкий тон фона в сторону текста.
	const neutralRaw = paletteColor('neutral', '')
	const surface =
		neutralRaw && contrastRatio(neutralRaw, bg) >= 1.12
			? neutralRaw
			: mix(bg, text, 0.06)

	// Читаемый текст поверх каждого «цветного» блока (CTA/кнопки/плашки).
	const onColor = (c: string) => pickReadable(c, [bg, '#FFFFFF', '#0E1018'], 3.5)
	return {
		background: bg,
		text,
		primary,
		onPrimary: onColor(primary),
		accent,
		onAccent: onColor(accent),
		secondary,
		onSecondary: onColor(secondary),
		surface,
		onSurface: pickReadable(surface, [text, '#0E1018', '#FFFFFF']),
		neutral: neutralRaw || '#eef0f4',
	}
})

function formatDate(s: string | null) {
	if (!s) return ''
	return new Date(s).toLocaleString('ru-RU', {
		day: 'numeric',
		month: 'long',
		hour: '2-digit',
		minute: '2-digit',
	})
}

function isDark(hex: string): boolean {
	const h = (hex || '').replace('#', '')
	if (h.length !== 6) return false
	const r = parseInt(h.slice(0, 2), 16)
	const g = parseInt(h.slice(2, 4), 16)
	const b = parseInt(h.slice(4, 6), 16)
	return (0.299 * r + 0.587 * g + 0.114 * b) / 255 < 0.55
}

const copiedHex = ref('')
function copyHex(hex: string) {
	navigator.clipboard?.writeText(hex)
	copiedHex.value = hex
	setTimeout(() => {
		if (copiedHex.value === hex) copiedHex.value = ''
	}, 1200)
}

/* ----------------------- PDF export ----------------------- */
const summaryRef = ref<HTMLElement | null>(null)
const exportingPdf = ref(false)

async function exportPdf() {
	const root = summaryRef.value
	if (!root || exportingPdf.value) return
	exportingPdf.value = true
	let isolation: HTMLDivElement | null = null
	try {
		const [{ default: html2canvas }, { default: jsPDF }] = await Promise.all([
			import('html2canvas-pro'),
			import('jspdf'),
		])
		try {
			if ((document as any).fonts?.ready) await (document as any).fonts.ready
		} catch {
			/* ignore */
		}

		// Клонируем сводку в off-screen контейнер с явным БЕЛЫМ фоном на КАЖДОМ
		// уровне, чтобы клетка прозрачности из PDF-вьюера не светилась через
		// "пустые" области (Tailwind часто оставляет прозрачные родители —
		// .card-flat, layout grid без bg). Снимаем сам контейнер целиком, а не
		// клон, чтобы белый фон контейнера гарантированно попал в snimok.
		const FIXED_WIDTH = Math.max(960, root.offsetWidth)
		isolation = document.createElement('div')
		isolation.style.cssText = [
			'position:absolute',
			'left:0',
			'top:-99999px',
			`width:${FIXED_WIDTH}px`,
			'background-color:#ffffff',
			'padding:24px',
			'margin:0',
			'box-sizing:border-box',
			'pointer-events:none',
			'overflow:visible',
		].join(';')
		isolation.classList.add('guidio-pdf-iso')
		// Глобально гасим тени — drop-shadow вокруг card-flat дают серые
		// артефакты в PDF. Inset-обводки (Tailwind `ring-*`) при этом тоже
		// пропадают, но это сознательный компромисс ради чистого фона.
		const shadowKill = document.createElement('style')
		shadowKill.textContent = `
			.guidio-pdf-iso *, .guidio-pdf-iso *::before, .guidio-pdf-iso *::after {
				box-shadow: none !important;
				text-shadow: none !important;
				filter: none !important;
			}
		`
		isolation.appendChild(shadowKill)
		const clone = root.cloneNode(true) as HTMLElement
		clone.style.width = `${FIXED_WIDTH - 48}px`
		clone.style.maxWidth = 'none'
		clone.style.margin = '0'
		clone.style.backgroundColor = '#ffffff'
		// В PDF не идут: «Живой макет» и «Принципы + Следующие шаги».
		// Они помечены атрибутом `data-pdf-hide` в шаблоне.
		clone
			.querySelectorAll<HTMLElement>('[data-pdf-hide]')
			.forEach(el => el.remove())
		isolation.appendChild(clone)
		document.body.appendChild(isolation)

		// Прозрачные / полупрозрачные фоны заменяем на их СПЛОШНОЙ эквивалент,
		// скомпозиченный с белым подложкой. Так "Живой макет" с bg-ink-50/40
		// сохраняет свой мягкий оттенок, а полностью прозрачные блоки
		// получают чистый белый. SVG/IMG/BUTTON/SPAN/A/PATH/INPUT — не трогаем.
		const SAFE_TAGS = new Set([
			'DIV',
			'SECTION',
			'ARTICLE',
			'ASIDE',
			'HEADER',
			'FOOTER',
			'MAIN',
			'NAV',
			'UL',
			'OL',
			'LI',
			'FIGURE',
			'FIGCAPTION',
			'P',
			'H1',
			'H2',
			'H3',
			'H4',
			'H5',
			'H6',
		])

		// Canvas-based парсер: понимает ЛЮБОЙ валидный CSS-цвет (rgba, oklch,
		// color(srgb ...), hwb, lab, color-mix). Заливаем сначала белым, потом
		// сверху сам цвет — получаем RGB после композитинга на белом.
		// Возвращает [r, g, b] или null если цвет считается прозрачным.
		const probeCanvas = document.createElement('canvas')
		probeCanvas.width = 1
		probeCanvas.height = 1
		const probeCtx = probeCanvas.getContext('2d', { willReadFrequently: true })

		const compositeOnWhite = (color: string): string | null => {
			if (!color) return null
			if (color === 'transparent') return '#ffffff'
			if (!probeCtx) return null
			// Очистка: заливаем чисто-белым.
			probeCtx.clearRect(0, 0, 1, 1)
			probeCtx.fillStyle = '#ffffff'
			probeCtx.fillRect(0, 0, 1, 1)
			// Накладываем целевой цвет — браузер сделает композит за нас.
			try {
				probeCtx.fillStyle = color
			} catch {
				return null
			}
			probeCtx.fillRect(0, 0, 1, 1)
			const d = probeCtx.getImageData(0, 0, 1, 1).data
			return `rgb(${d[0]}, ${d[1]}, ${d[2]})`
		}

		// Проверяет — фон полностью прозрачен (без композита).
		const isFullyTransparent = (color: string): boolean => {
			if (!color || color === 'transparent') return true
			if (!probeCtx) return false
			// На прозрачной канве пиксель должен иметь alpha=0.
			probeCtx.clearRect(0, 0, 1, 1)
			try {
				probeCtx.fillStyle = color
			} catch {
				return false
			}
			probeCtx.fillRect(0, 0, 1, 1)
			const d = probeCtx.getImageData(0, 0, 1, 1).data
			return d[3] === 0
		}

		const all = isolation.querySelectorAll<HTMLElement>('*')
		for (const el of all) {
			if (!SAFE_TAGS.has(el.tagName)) continue
			// Свотчи палитры и кнопки с inline-фоном/градиентом — не трогаем.
			if (el.style.backgroundColor || el.style.background) continue
			const computed = window.getComputedStyle(el)
			// Если есть картинка/градиент в backgroundImage — не трогаем.
			if (computed.backgroundImage && computed.backgroundImage !== 'none') continue
			const bg = computed.backgroundColor
			if (isFullyTransparent(bg)) {
				el.style.backgroundColor = '#ffffff'
				continue
			}
			// Полупрозрачные фоны (`bg-ink-50/40` и т.п.) композитим
			// в сплошной RGB поверх белого через canvas — html2canvas-pro
			// иначе теряет оттенок. Для непрозрачных вернётся та же строка.
			const composed = compositeOnWhite(bg)
			if (composed) {
				el.style.backgroundColor = composed
			}
		}

		// Подождём 2 кадра, чтобы все styles применились и layout стабилизировался.
		await new Promise(resolve =>
			requestAnimationFrame(() => requestAnimationFrame(() => resolve(null))),
		)

		const canvas = await html2canvas(isolation, {
			scale: 2,
			useCORS: true,
			backgroundColor: '#ffffff',
			logging: false,
			width: FIXED_WIDTH,
			height: isolation.scrollHeight,
			windowWidth: FIXED_WIDTH,
			windowHeight: Math.max(isolation.scrollHeight, window.innerHeight),
		})

		const pdf = new jsPDF({ unit: 'mm', format: 'a4', orientation: 'portrait' })
		const pageWidth = pdf.internal.pageSize.getWidth()
		const pageHeight = pdf.internal.pageSize.getHeight()
		const margin = 10
		const usableWidth = pageWidth - margin * 2
		const usableHeight = pageHeight - margin * 2
		const imgWidth = usableWidth
		const imgHeight = (canvas.height * imgWidth) / canvas.width
		// PNG, чтобы избежать JPEG-артефактов и compression noise; белый
		// фон уже зашит в canvas через backgroundColor.
		const dataUrl = canvas.toDataURL('image/png')

		// Заливаем каждую страницу белым перед addImage — защита от прозрачности PDF.
		const fillPageWhite = () => {
			pdf.setFillColor(255, 255, 255)
			pdf.rect(0, 0, pageWidth, pageHeight, 'F')
		}

		let heightLeft = imgHeight
		let position = margin
		fillPageWhite()
		pdf.addImage(dataUrl, 'PNG', margin, position, imgWidth, imgHeight, undefined, 'FAST')
		heightLeft -= usableHeight
		while (heightLeft > 0) {
			position = margin - (imgHeight - heightLeft)
			pdf.addPage()
			fillPageWhite()
			pdf.addImage(dataUrl, 'PNG', margin, position, imgWidth, imgHeight, undefined, 'FAST')
			heightLeft -= usableHeight
		}

		const stamp = new Date()
			.toISOString()
			.slice(0, 16)
			.replace('T', '_')
			.replace(':', '-')
		const direction = props.summary?.direction || 'guidio'
		const filename = `guidio_${direction.replace(/[^а-яА-Яa-zA-Z0-9_-]+/g, '-')}_${stamp}.pdf`
		pdf.save(filename)
	} catch (e) {
		console.error('PDF export failed', e)
	} finally {
		if (isolation && isolation.parentNode) {
			isolation.parentNode.removeChild(isolation)
		}
		exportingPdf.value = false
	}
}
</script>

<template>
	<section class="space-y-4 min-w-0">
		<div class="flex items-start justify-between gap-4 flex-wrap">
			<div>
				<h2 class="font-display text-xl font-semibold text-ink-900">
					Итоговые рекомендации
				</h2>
				<p class="text-xs text-ink-500 mt-1">
					AI собирает итог по всем сессиям проекта: шрифтовая пара, палитра и
					живой макет.
				</p>
			</div>
			<div
				class="basis-full order-3 flex items-start gap-2.5 rounded-xl bg-accent-50/70 ring-1 ring-accent-100 px-3.5 py-2.5"
			>
				<svg
					class="text-accent-600 mt-0.5 shrink-0"
					width="14"
					height="14"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<circle cx="12" cy="12" r="9" />
					<path d="M12 8v5M12 16h.01" />
				</svg>
				<p class="text-[12px] text-ink-700 leading-relaxed">
					Подбор учитывает ваши реакции в чате:
					<span class="font-medium text-emerald-700">👍 лайк</span>
					— такие варианты приоритетны;
					<span class="font-medium text-rose-700">👎 дизлайк</span>
					— используется как антипример. Чем больше реакций вы поставите в
					сессиях шрифтов и мудбордов, тем точнее будет итог.
				</p>
			</div>
			<div class="flex items-center gap-2 flex-wrap">
				<button
					v-if="props.summary"
					class="btn-secondary btn-sm"
					:disabled="exportingPdf || props.loading"
					@click="exportPdf"
					title="Сохранить итоговые рекомендации в PDF"
				>
					<svg
						v-if="!exportingPdf"
						width="12"
						height="12"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4M7 10l5 5 5-5M12 15V3" />
					</svg>
					<svg
						v-else
						class="animate-spin"
						width="12"
						height="12"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
					>
						<path d="M21 12a9 9 0 1 1-6.7-8.7" />
					</svg>
					{{ exportingPdf ? 'Готовим PDF…' : 'Сохранить PDF' }}
				</button>
				<button
					class="btn-secondary btn-sm"
					:disabled="props.loading"
					@click="emit('regenerate')"
				>
					<svg
						width="12"
						height="12"
						viewBox="0 0 24 24"
						fill="none"
						stroke="currentColor"
						stroke-width="2"
						:class="props.loading ? 'animate-spin' : ''"
					>
						<path d="M3 12a9 9 0 1 0 3-6.7L3 8V3" />
					</svg>
					{{
						props.loading
							? 'Генерируем…'
							: props.summary
								? 'Обновить сводку'
								: 'Сгенерировать сводку'
					}}
				</button>
			</div>
		</div>

		<!-- Empty state -->
		<div
			v-if="!props.summary && !props.loading"
			class="card-flat p-10 text-center"
		>
			<div
				class="h-12 w-12 rounded-2xl bg-linear-to-br from-[#4373E4] to-[#4373E4] text-white mx-auto flex items-center justify-center mb-4"
			>
				<svg
					width="20"
					height="20"
					viewBox="0 0 24 24"
					fill="none"
					stroke="currentColor"
					stroke-width="2"
				>
					<path
						d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z"
					/>
				</svg>
			</div>
			<div class="font-display text-base font-semibold text-ink-900">
				Сгенерируйте финальный вариант
			</div>
			<p class="text-sm text-ink-500 mt-1 max-w-md mx-auto">
				Guidio соберёт из ваших сессий рекомендованную шрифтовую пару, палитру и
				покажет живой макет.
			</p>
		</div>

		<div
			v-else-if="props.loading && !props.summary"
			class="card-flat p-10 text-center text-sm text-ink-400"
		>
			Готовим рекомендации…
		</div>

		<div
			v-else-if="props.summary"
			ref="summaryRef"
			class="card overflow-hidden"
		>
			<!-- Overview -->
			<div class="p-6 border-b border-ink-100">
				<div class="flex items-start justify-between gap-4 flex-wrap">
					<div class="flex-1 min-w-0">
						<div
							v-if="props.summary.direction"
							class="text-[10px] uppercase tracking-widest text-accent-600 mb-1"
						>
							{{ props.summary.direction }}
						</div>
						<p
							v-if="props.summary.overview"
							class="text-sm text-ink-800 leading-relaxed max-w-2xl"
						>
							{{ props.summary.overview }}
						</p>
						<div
							v-if="props.summary.mood?.length"
							class="flex flex-wrap gap-1.5 mt-3"
						>
							<span
								v-for="m in props.summary.mood"
								:key="m"
								class="chip bg-accent-50 text-accent-700 ring-1 ring-accent-100"
								>{{ m }}</span
							>
						</div>
					</div>
					<div
						v-if="props.generatedAt"
						class="text-[11px] text-ink-400 shrink-0"
					>
						{{ formatDate(props.generatedAt) }}
					</div>
				</div>
			</div>

			<!-- Fonts + Palette -->
			<div
				class="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-ink-100"
			>
				<!-- Recommended fonts -->
				<div v-if="props.summary.recommended_fonts" class="p-6 space-y-4">
					<div class="text-[10px] uppercase tracking-widest text-ink-400">
						Шрифтовая пара
					</div>

					<div class="space-y-3">
						<div
							v-if="props.summary.recommended_fonts.heading"
							class="card-flat p-4"
						>
							<div class="text-[10px] text-ink-400 mb-1">Заголовок</div>
							<div
								:style="{
									fontFamily: headingStack,
									fontWeight:
										props.summary.recommended_fonts.heading.weight || 600,
								}"
								class="text-2xl text-ink-900 leading-tight"
							>
								{{ props.summary.recommended_fonts.heading.family }}
							</div>
						</div>
						<div
							v-if="props.summary.recommended_fonts.body"
							class="card-flat p-4"
						>
							<div class="text-[10px] text-ink-400 mb-1">Основной текст</div>
							<div
								:style="{
									fontFamily: bodyStack,
									fontWeight:
										props.summary.recommended_fonts.body.weight || 400,
								}"
								class="text-base text-ink-900"
							>
								{{ props.summary.recommended_fonts.body.family }} ·
								{{ props.summary.recommended_fonts.body.weight || 400 }}
							</div>
						</div>
					</div>

					<p
						v-if="props.summary.recommended_fonts.rationale"
						class="text-xs text-ink-500 leading-relaxed"
					>
						{{ props.summary.recommended_fonts.rationale }}
					</p>
				</div>

				<!-- Recommended palette -->
				<div v-if="palette.length" class="p-6 space-y-3">
					<div class="text-[10px] uppercase tracking-widest text-ink-400">
						Палитра
					</div>

					<div class="grid grid-cols-5 gap-1.5">
						<button
							v-for="c in palette.slice(0, 5)"
							:key="c.hex"
							class="card-flat overflow-hidden text-left cursor-pointer"
							@click="copyHex(c.hex)"
							:title="`Скопировать ${c.hex}`"
						>
							<div
								class="relative aspect-square"
								:style="{ background: c.hex }"
							>
								<div
									v-if="copiedHex === c.hex"
									class="absolute inset-0 flex items-center justify-center"
									:class="isDark(c.hex) ? 'text-white' : 'text-ink-900'"
								>
									<svg
										width="14"
										height="14"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2.5"
									>
										<path d="m5 12 5 5L20 7" />
									</svg>
								</div>
							</div>
							<div class="px-2 py-1.5">
								<div
									v-if="c.role"
									class="text-[9px] uppercase tracking-wider text-ink-400 truncate"
								>
									{{ roleLabel[c.role] || c.role }}
								</div>
								<div class="text-[10px] font-mono text-ink-700 truncate">
									{{ c.hex.toUpperCase() }}
								</div>
							</div>
						</button>
					</div>

					<div
						v-if="palette.length"
						class="flex h-1.5 rounded-full overflow-hidden ring-1 ring-ink-100"
					>
						<div
							v-for="c in palette"
							:key="`pp-${c.hex}`"
							:style="{
								background: c.hex,
								width: `${Math.max(5, c.usage_percent || 100 / palette.length)}%`,
							}"
						/>
					</div>
				</div>
			</div>

			<!-- Live mockup -->
			<div
				v-if="props.summary.mockup"
				data-pdf-hide
				class="p-6 bg-ink-50/40 border-t border-ink-100"
			>
				<div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">
					Живой макет
				</div>
				<div
					class="rounded-2xl ring-1 ring-ink-100 overflow-hidden"
					:style="{ background: colors.background, color: colors.text }"
				>
					<!-- Hero bar using primary color -->
					<div
						class="h-1.5"
						:style="{
							background: `linear-gradient(90deg, ${colors.primary}, ${colors.accent})`,
						}"
					/>

					<div class="p-6 sm:p-10">
						<div class="flex items-center justify-between gap-3 mb-6">
							<div class="flex items-center gap-2 min-w-0">
								<span
									class="inline-flex items-center justify-center h-8 w-8 rounded-xl shrink-0"
									:style="{
										background: colors.primary,
										color: colors.onPrimary,
									}"
								>
									<svg
										width="16"
										height="16"
										viewBox="0 0 24 24"
										fill="none"
										stroke="currentColor"
										stroke-width="2.5"
									>
										<path
											d="M12 3 13.5 9.5 20 11 13.5 12.5 12 19 10.5 12.5 4 11 10.5 9.5Z"
										/>
									</svg>
								</span>
								<span
									:style="{ fontFamily: bodyStack, fontWeight: 600 }"
									class="text-sm truncate"
									>{{ props.summary.direction || 'Проект' }}</span
								>
							</div>
							<span
								v-if="props.summary.mood?.length"
								:style="{
									fontFamily: bodyStack,
									fontWeight: 600,
									background: colors.accent,
									color: colors.onAccent,
								}"
								class="text-[11px] px-2.5 py-1 rounded-full shrink-0"
								>{{ props.summary.mood[0] }}</span
							>
						</div>

						<h3
							:style="{
								fontFamily: headingStack,
								fontWeight:
									props.summary.recommended_fonts?.heading?.weight || 700,
								color: colors.primary,
							}"
							class="text-[28px] sm:text-[44px] leading-[1.1] mb-3 wrap-break-word"
						>
							{{ props.summary.mockup.title }}
						</h3>

						<p
							v-if="props.summary.mockup.subtitle"
							:style="{
								fontFamily: bodyStack,
								fontWeight: 500,
								color: colors.text,
							}"
							class="text-[16px] sm:text-[18px] leading-[1.5] mb-5 max-w-xl opacity-70 wrap-break-word"
						>
							{{ props.summary.mockup.subtitle }}
						</p>

						<p
							v-if="props.summary.mockup.body"
							:style="{
								fontFamily: bodyStack,
								fontWeight: 400,
								color: colors.text,
							}"
							class="text-[15px] leading-[1.7] mb-7 max-w-xl opacity-80"
						>
							{{ props.summary.mockup.body }}
						</p>

						<div class="flex items-center gap-3 flex-wrap">
							<button
								:style="{
									fontFamily: bodyStack,
									fontWeight: 500,
									background: colors.primary,
									color: colors.onPrimary,
								}"
								class="inline-flex items-center gap-2 px-5 py-2.5 rounded-full text-sm cursor-default"
							>
								{{ props.summary.mockup.cta || 'Подробнее' }}
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
							<button
								:style="{
									fontFamily: bodyStack,
									fontWeight: 500,
									color: colors.onAccent,
									background: colors.accent,
								}"
								class="inline-flex items-center px-5 py-2.5 rounded-full text-sm cursor-default"
							>
								Узнать больше
							</button>
						</div>

						<!-- Фичи-плитки: задействуют surface / secondary / accent палитры -->
						<div class="mt-9 grid grid-cols-3 gap-2.5">
							<div
								class="rounded-xl px-3.5 py-3"
								:style="{ background: colors.surface, color: colors.onSurface }"
							>
								<div
									:style="{ fontFamily: headingStack, fontWeight: 600 }"
									class="text-lg leading-none"
								>
									Aa
								</div>
								<div
									:style="{ fontFamily: bodyStack }"
									class="text-[11px] mt-1.5 truncate"
								>
									{{ props.summary.recommended_fonts?.heading?.family || 'Заголовки' }}
								</div>
							</div>
							<div
								class="rounded-xl px-3.5 py-3"
								:style="{ background: colors.secondary, color: colors.onSecondary }"
							>
								<div
									:style="{ fontFamily: bodyStack, fontWeight: 700 }"
									class="text-lg leading-none"
								>
									{{ palette.length }}
								</div>
								<div
									:style="{ fontFamily: bodyStack }"
									class="text-[11px] mt-1.5"
								>
									цвета в системе
								</div>
							</div>
							<div
								class="rounded-xl px-3.5 py-3"
								:style="{ background: colors.accent, color: colors.onAccent }"
							>
								<div
									:style="{ fontFamily: bodyStack, fontWeight: 600 }"
									class="text-sm leading-tight truncate"
								>
									{{ props.summary.mood?.[1] || props.summary.mood?.[0] || 'Акцент' }}
								</div>
								<div
									:style="{ fontFamily: bodyStack }"
									class="text-[11px] mt-1.5"
								>
									характер
								</div>
							</div>
						</div>

						<!-- Палитра «в деле» — все цвета как сплошные плитки -->
						<div class="mt-2.5 flex items-center gap-1.5">
							<span
								v-for="c in palette.slice(0, 6)"
								:key="`tile-${c.hex}`"
								class="h-6 flex-1 rounded-md"
								:style="{ background: c.hex }"
								:title="c.name || c.hex"
							/>
						</div>
					</div>
				</div>

			</div>

			<!-- Principles + next steps -->
			<div
				v-if="
					props.summary.key_principles?.length ||
					props.summary.next_steps?.length
				"
				data-pdf-hide
				class="grid md:grid-cols-2 divide-y md:divide-y-0 md:divide-x divide-ink-100 border-t border-ink-100"
			>
				<div v-if="props.summary.key_principles?.length" class="p-6">
					<div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">
						Принципы
					</div>
					<ul class="space-y-2">
						<li
							v-for="(p, i) in props.summary.key_principles"
							:key="i"
							class="flex items-start gap-2.5"
						>
							<span
								class="h-4 w-4 rounded-full bg-accent-50 text-accent-600 text-[10px] font-semibold flex items-center justify-center shrink-0 mt-0.5"
							>
								{{ i + 1 }}
							</span>
							<span class="text-sm text-ink-700 leading-relaxed">{{ p }}</span>
						</li>
					</ul>
				</div>
				<div v-if="props.summary.next_steps?.length" class="p-6">
					<div class="text-[10px] uppercase tracking-widest text-ink-400 mb-3">
						Следующие шаги
					</div>
					<ul class="space-y-2">
						<li
							v-for="(s, i) in props.summary.next_steps"
							:key="i"
							class="flex items-start gap-2.5"
						>
							<svg
								class="text-accent-500 mt-0.5 shrink-0"
								width="14"
								height="14"
								viewBox="0 0 24 24"
								fill="none"
								stroke="currentColor"
								stroke-width="2"
							>
								<path d="M5 12h14M13 6l6 6-6 6" />
							</svg>
							<span class="text-sm text-ink-700 leading-relaxed">{{ s }}</span>
						</li>
					</ul>
				</div>
			</div>
		</div>
	</section>
</template>
