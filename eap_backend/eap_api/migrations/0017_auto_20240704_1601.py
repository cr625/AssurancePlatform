# Generated by Django 3.2.8 on 2024-07-04 16:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("eap_api", "0016_auto_20240613_1028"),
    ]

    operations = [
        migrations.AlterField(
            model_name="context",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="URL",
            field=models.CharField(blank=True, max_length=3000, null=True),
        ),
        migrations.AlterField(
            model_name="evidence",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="propertyclaim",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="strategy",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AlterField(
            model_name="toplevelnormativegoal",
            name="name",
            field=models.CharField(blank=True, max_length=200),
        ),
    ]
