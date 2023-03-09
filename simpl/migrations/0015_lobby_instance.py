# Generated by Django 3.2 on 2021-09-05 23:52

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("simpl", "0014_auto_20210903_1514"),
    ]

    operations = [
        migrations.AddField(
            model_name="lobby",
            name="instance",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to=settings.SIMPL_INSTANCE,
            ),
        ),
    ]
