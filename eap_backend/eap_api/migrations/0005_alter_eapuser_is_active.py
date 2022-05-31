# Generated by Django 3.2.8 on 2022-05-31 10:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eap_api", "0004_auto_20220531_0935"),
    ]

    operations = [
        migrations.AlterField(
            model_name="eapuser",
            name="is_active",
            field=models.BooleanField(
                default=True,
                help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.",
                verbose_name="active",
            ),
        ),
    ]
