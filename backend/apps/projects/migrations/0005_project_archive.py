from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("projects", "0004_add_collaborators_and_invite"),
    ]

    operations = [
        migrations.AddField(
            model_name="project",
            name="is_archived",
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name="project",
            name="archived_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
