# Generated by Django 3.2.8 on 2024-09-30 09:21

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eap_api", "0024_auto_20240926_1231"),
    ]

    operations = [
        migrations.AlterField(
            model_name="assurancecaseimage",
            name="assurance_case",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="case_image",
                to="eap_api.assurancecase",
                unique=True,
            ),
        ),
    ]