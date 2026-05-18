<script setup lang="ts"></script>

<template>
	<footer class="bg-ink-50 border-t border-ink-100 mt-20">
		<div
			class="max-w-[1240px] mx-auto px-6 py-14 grid grid-cols-1 md:grid-cols-4 gap-8"
		>
			<div class="md:col-span-2 space-y-3">
				<NuxtLink to="/" class="flex items-center">
					<img src="/full-logo.svg" alt="Guidio" class="h-8 w-auto" />
				</NuxtLink>
				<p class="text-sm text-ink-500 max-w-sm leading-relaxed">
					Ваш лучший помощник по подбору стилевых решений, шрифтов и мудбордов
					для современных проектов.
				</p>
			</div>

			<div class="md:pl-10">
				<h4 class="text-sm font-semibold text-ink-800 mb-3">Продукт</h4>
				<ul class="space-y-2 text-sm text-ink-500">
					<li>
						<NuxtLink to="/" class="hover:text-ink-800">Главная</NuxtLink>
					</li>
					<li>
						<NuxtLink to="/#features" class="hover:text-ink-800"
							>Возможности</NuxtLink
						>
					</li>
					<li>
						<NuxtLink to="/#how" class="hover:text-ink-800"
							>Как это работает</NuxtLink
						>
					</li>
					<li>
						<NuxtLink to="/#teams" class="hover:text-ink-800"
							>Командная работа</NuxtLink
						>
					</li>
				</ul>
			</div>

			<div class="md:pl-10">
				<h4 class="text-sm font-semibold text-ink-800 mb-3">Ресурсы</h4>
				<ul class="space-y-2 text-sm text-ink-500">
					<li>
						<NuxtLink to="/blog" class="hover:text-ink-800">Блог</NuxtLink>
					</li>
					<li>
						<NuxtLink to="/about" class="hover:text-ink-800"
							>О проекте</NuxtLink
						>
					</li>
					<li>
						<NuxtLink to="/contacts" class="hover:text-ink-800"
							>Контакты</NuxtLink
						>
					</li>
				</ul>
			</div>
		</div>
		<div class="border-t border-ink-100">
			<div
				class="max-w-[1240px] mx-auto px-6 py-5 text-xs text-ink-400 flex flex-wrap items-center justify-between gap-2"
			>
				<span
					>© {{ new Date().getFullYear() }} Guidio. Все права защищены.</span
				>
				<div class="flex gap-4 text-ink-400">
					<a
						href="https://t.me/guidio_team"
						target="_blank"
						rel="noopener"
						title="Telegram"
						class="hover:text-ink-800 transition-colors"
					>
						<svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
							<path
								d="M11.944 0A12 12 0 0 0 0 12a12 12 0 0 0 12 12 12 12 0 0 0 12-12A12 12 0 0 0 12 0a12 12 0 0 0-.056 0zm4.962 7.224c.1-.002.321.023.465.14a.506.506 0 0 1 .171.325c.016.093.036.306.02.472-.18 1.898-.962 6.502-1.36 8.627-.168.9-.499 1.201-.82 1.23-.696.065-1.225-.46-1.9-.902-1.056-.693-1.653-1.124-2.678-1.8-1.185-.78-.417-1.21.258-1.91.177-.184 3.247-2.977 3.307-3.23.007-.032.014-.15-.056-.212s-.174-.041-.249-.024c-.106.024-1.793 1.14-5.061 3.345-.48.33-.913.49-1.302.48-.428-.008-1.252-.241-1.865-.44-.752-.245-1.349-.374-1.297-.789.027-.216.325-.437.893-.663 3.498-1.524 5.83-2.529 6.998-3.014 3.332-1.386 4.025-1.627 4.476-1.635z"
							/>
						</svg>
					</a>
				</div>
			</div>
		</div>
	</footer>
</template>
