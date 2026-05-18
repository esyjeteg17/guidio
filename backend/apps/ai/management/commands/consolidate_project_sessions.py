from collections import defaultdict

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.ai.models import ChatSession


class Command(BaseCommand):
    help = (
        "Схлопывает дубликаты сессий внутри проекта: для каждой тройки "
        "(user, project, mode) оставляет одну сессию (самую свежую), переносит "
        "в неё сообщения из остальных и удаляет дубли."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Только показать, что было бы сделано, без записи в БД.",
        )

    def handle(self, *args, **options):
        dry_run = options["dry_run"]

        sessions = ChatSession.objects.exclude(project__isnull=True).order_by(
            "user_id", "project_id", "mode", "-updated_at",
        )

        groups: dict[tuple[int, int, str], list[ChatSession]] = defaultdict(list)
        for s in sessions:
            groups[(s.user_id, s.project_id, s.mode)].append(s)

        merged = 0
        moved_messages = 0
        deleted = 0

        with transaction.atomic():
            for (user_id, project_id, mode), items in groups.items():
                if len(items) <= 1:
                    continue

                winner = items[0]  # самая свежая по updated_at
                losers = items[1:]
                self.stdout.write(
                    f"user={user_id} project={project_id} mode={mode}: "
                    f"оставляем #{winner.pk}, схлопываем {len(losers)} дубликатов "
                    f"({', '.join(f'#{l.pk}' for l in losers)})"
                )
                merged += 1
                for loser in losers:
                    cnt = loser.messages.count()
                    if cnt and not dry_run:
                        loser.messages.update(session=winner)
                    moved_messages += cnt
                    if not dry_run:
                        loser.delete()
                    deleted += 1

            if dry_run:
                transaction.set_rollback(True)

        suffix = " (dry-run, изменения откатаны)" if dry_run else ""
        self.stdout.write(self.style.SUCCESS(
            f"Готово{suffix}: групп схлопнуто {merged}, "
            f"перенесено сообщений {moved_messages}, удалено сессий {deleted}."
        ))
