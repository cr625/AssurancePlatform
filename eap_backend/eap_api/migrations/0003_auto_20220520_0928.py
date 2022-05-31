# Generated by Django 3.2.8 on 2022-05-20 09:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eap_api", "0002_auto_20220519_1546"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assurancecase",
            name="edit_groups",
            field=models.ManyToManyField(
                blank=True, related_name="editable_cases", to="eap_api.EAPGroup"
            ),
        ),
        migrations.AlterField(
            model_name="assurancecase",
            name="view_groups",
            field=models.ManyToManyField(
                blank=True, related_name="viewable_cases", to="eap_api.EAPGroup"
            ),
        ),
    ]