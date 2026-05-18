import secrets

import apps.projects.models
from django.conf import settings
from django.db import migrations, models


def _fill_invite_tokens(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    for project in Project.objects.filter(invite_token=""):
        project.invite_token = secrets.token_urlsafe(16)
        project.save(update_fields=["invite_token"])


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0003_project_summary_generated_at_project_summary_payload"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="collaborators",
            field=models.ManyToManyField(
                blank=True,
                help_text="Приглашённые соавторы (помимо владельца и команды)",
                related_name="joined_projects",
                to=settings.AUTH_USER_MODEL,
            ),
        ),
        migrations.AddField(
            model_name="project",
            name="invite_token",
            field=models.CharField(blank=True, default="", max_length=64),
        ),
        migrations.RunPython(_fill_invite_tokens, reverse_code=migrations.RunPython.noop),
        migrations.AlterField(
            model_name="project",
            name="invite_token",
            field=models.CharField(
                blank=True,
                default=apps.projects.models._project_invite_token,
                max_length=64,
                unique=True,
            ),
        ),
    ]
