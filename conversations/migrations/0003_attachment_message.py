# Generated by Django 3.1.6 on 2021-02-11 07:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("conversations", "0002_auto_20210210_2303"),
    ]

    operations = [
        migrations.AddField(
            model_name="attachment",
            name="message",
            field=models.ForeignKey(
                default=None,
                on_delete=django.db.models.deletion.CASCADE,
                to="conversations.receivedmessage",
            ),
            preserve_default=False,
        ),
    ]
