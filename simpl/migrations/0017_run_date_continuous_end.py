# Generated by Django 3.2 on 2021-09-06 21:00

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("simpl", "0016_link_lobby_instances"),
    ]

    operations = [
        migrations.AddField(
            model_name="run",
            name="date_continuous_end",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
