# Generated by Django 4.2.6 on 2023-10-31 19:30

from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("airport", "0003_alter_airplane_airplane_type_alter_flight_airplane_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="route",
            name="type_of_measurement",
            field=models.CharField(
                choices=[("km", "Kilometers"), ("miles", "Miles")],
                default="km",
                max_length=10,
            ),
        ),
    ]
