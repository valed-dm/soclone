# Generated by Django 4.2.10 on 2024-02-21 10:21

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Tag",
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
                ("name", models.CharField(max_length=50, unique=True)),
                ("pub_date", models.DateTimeField(verbose_name="date published")),
            ],
        ),
        migrations.CreateModel(
            name="Question",
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
                ("title", models.CharField(max_length=200, unique=True)),
                (
                    "problem",
                    models.TextField(
                        help_text="What are the details of your problem?\nIntroduce the problem and expand on what you put in the title. Minimum 20 characters.",
                        unique=True,
                        validators=[
                            django.core.validators.MinLengthValidator(
                                limit_value=20,
                                message="Description must be 20 characters or more.",
                            )
                        ],
                    ),
                ),
                (
                    "effort",
                    models.TextField(
                        help_text="What did you try and what were you expecting?\nDescribe what you tried, what you expected to happen, and what actually resulted. Minimum 20 characters.",
                        unique=True,
                        validators=[
                            django.core.validators.MinLengthValidator(
                                limit_value=20,
                                message="Description must be 20 characters or more.",
                            )
                        ],
                    ),
                ),
                ("pub_date", models.DateTimeField(verbose_name="date published")),
                ("tags", models.ManyToManyField(to="questions.tag")),
            ],
        ),
    ]