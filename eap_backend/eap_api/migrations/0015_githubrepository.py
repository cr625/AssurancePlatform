# Generated by Django 3.2.8 on 2023-11-07 13:07

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("eap_api", "0014_remove_comment_parent"),
    ]

    operations = [
        migrations.CreateModel(
            name="GitHubRepository",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("name", models.CharField(max_length=200)),
                ("url", models.URLField()),
                ("description", models.TextField(blank=True, null=True)),
                ("created_date", models.DateTimeField(auto_now_add=True)),
                (
                    "owner",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="github_repositories",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]