# Generated by Django 3.1.6 on 2021-03-13 23:03

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0015_auto_20210313_1457'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='addresses',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), blank=True, size=None),
        ),
    ]