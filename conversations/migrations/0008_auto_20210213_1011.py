# Generated by Django 3.1.6 on 2021-02-13 18:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('conversations', '0007_auto_20210213_0953'),
    ]

    operations = [
        migrations.AlterField(
            model_name='message',
            name='references',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='conversations.message'),
        ),
    ]