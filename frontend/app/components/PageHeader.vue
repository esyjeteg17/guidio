<script setup lang="ts">
interface Crumb {
	label: string
	to?: string
	maxWidth?: string
}

defineProps<{
	crumbs: Crumb[]
}>()
</script>

<template>
	<div
		class="sticky top-0 z-10 px-4 sm:px-6 lg:px-8 py-3 sm:py-4 border-b border-[#dfdfdf] bg-[#fdfdfd] flex items-center gap-2 text-sm flex-wrap min-h-16"
	>
		<template v-for="(c, i) in crumbs" :key="i">
			<svg
				v-if="i > 0"
				width="14"
				height="14"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				class="text-ink-400"
			>
				<path d="m9 6 6 6-6 6" />
			</svg>
			<NuxtLink
				v-if="c.to"
				:to="c.to"
				class="text-ink-500 hover:text-ink-800 truncate"
				:style="c.maxWidth ? { maxWidth: c.maxWidth } : { maxWidth: '200px' }"
			>
				{{ c.label }}
			</NuxtLink>
			<span
				v-else
				class="font-medium text-ink-900 truncate"
				:style="c.maxWidth ? { maxWidth: c.maxWidth } : undefined"
			>
				{{ c.label }}
			</span>
		</template>

		<template v-if="$slots.trailing">
			<svg
				width="14"
				height="14"
				viewBox="0 0 24 24"
				fill="none"
				stroke="currentColor"
				stroke-width="2"
				class="text-ink-400"
			>
				<path d="m9 6 6 6-6 6" />
			</svg>
			<slot name="trailing" />
		</template>

		<div class="flex-1" />

		<slot name="actions" />
	</div>
</template>
