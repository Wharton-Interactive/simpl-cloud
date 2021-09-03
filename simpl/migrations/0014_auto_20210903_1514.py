# Generated by Django 2.2.22 on 2021-09-03 15:14

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("simpl", "0013_gameexperience_multiplayer"),
    ]

    operations = [
        migrations.AlterField(
            model_name="player",
            name="character",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.SIMPL_CHARACTER,
            ),
        ),
    ]