from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("ai", "0003_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="chatmessage",
            name="reaction",
            field=models.CharField(
                blank=True,
                choices=[("like", "Нравится"), ("dislike", "Не нравится")],
                max_length=8,
                null=True,
            ),
        ),
    ]
