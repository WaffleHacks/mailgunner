# Generated by Django 3.1.6 on 2021-03-13 22:57

import django.contrib.postgres.fields
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0014_auto_20210213_1450'),
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=256)),
                ('addresses', django.contrib.postgres.fields.ArrayField(base_field=models.EmailField(max_length=254), size=None)),
            ],
        ),
        migrations.AddField(
            model_name='thread',
            name='category',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='conversations.category'),
        ),
    ]
