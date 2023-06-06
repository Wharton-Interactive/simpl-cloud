# Generated by Django 3.2.18 on 2023-05-05 07:51

import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import simpl.utils.models

try:
    from django.db.models import JSONField
except ImportError:
    from django.contrib.postgres.fields import JSONField


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.SIMPL_RUN),
        migrations.swappable_dependency(settings.SIMPL_GAME_EXPERIENCE),
    ]

    operations = [
        migrations.CreateModel(
            name="WorldWithRelatedName",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("date_start", models.DateTimeField(blank=True, null=True)),
                ("date_end", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(blank=True, max_length=100)),
                ("data", JSONField(blank=True, default=dict, editable=False)),
                (
                    "game",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.SIMPL_GAME_EXPERIENCE,
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        related_name="worldswithrelatedname",
                        to=settings.SIMPL_RUN,
                    ),
                ),
            ],
            options={
                "ordering": ("-date_created",),
                "abstract": False,
            },
            bases=(simpl.utils.models.DataMixin, models.Model),
        ),
        migrations.CreateModel(
            name="World",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        default=django.utils.timezone.now, editable=False
                    ),
                ),
                ("date_start", models.DateTimeField(blank=True, null=True)),
                ("date_end", models.DateTimeField(blank=True, null=True)),
                ("name", models.CharField(blank=True, max_length=100)),
                ("data", JSONField(blank=True, default=dict, editable=False)),
                (
                    "game",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.SIMPL_GAME_EXPERIENCE,
                    ),
                ),
                (
                    "run",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.SET_NULL,
                        to=settings.SIMPL_RUN,
                    ),
                ),
            ],
            options={
                "ordering": ("-date_created",),
                "abstract": False,
            },
            bases=(simpl.utils.models.DataMixin, models.Model),
        ),
    ]