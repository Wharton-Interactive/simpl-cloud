# Generated by Django 3.2.4 on 2021-07-01 11:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('simpl', '0003_auto_20210701_1047'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Token',
            new_name='APIToken',
        ),
    ]
