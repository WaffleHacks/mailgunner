# Generated by Django 3.1.6 on 2021-02-12 19:02

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("conversations", "0004_auto_20210212_1058"),
    ]

    operations = [
        migrations.AlterField(
            model_name="receivedmessage",
            name="cc",
            field=models.TextField(blank=True, default=""),
            preserve_default=False,
        ),
    ]
