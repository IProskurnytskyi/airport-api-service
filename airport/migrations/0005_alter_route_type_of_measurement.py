# Generated by Django 4.2.6 on 2023-10-31 21:11

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0004_route_type_of_measurement"),
    ]

    operations = [
        migrations.AlterField(
            model_name="route",
            name="type_of_measurement",
            field=models.CharField(
                choices=[("km", "Kilometers"), ("ml", "Miles")],
                default="km",
                max_length=10,
            ),
        ),
    ]
