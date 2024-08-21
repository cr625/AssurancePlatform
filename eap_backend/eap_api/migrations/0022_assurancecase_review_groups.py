# Generated by Django 3.2.8 on 2024-08-21 14:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eap_api", "0021_eapuser_auth_username"),
    ]

    operations = [
        migrations.AddField(
            model_name="assurancecase",
            name="review_groups",
            field=models.ManyToManyField(
                blank=True, related_name="reviewable_cases", to="eap_api.EAPGroup"
            ),
        ),
    ]
