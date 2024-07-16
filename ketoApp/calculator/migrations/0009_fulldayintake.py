# Generated by Django 5.0.3 on 2024-04-26 12:10

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0008_alter_product_user'),
        ('users', '0010_alter_demand_keto_app_user'),
    ]

    operations = [
        migrations.CreateModel(
            name='FullDayIntake',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField(default=datetime.date(2024, 4, 26))),
                ('total_kcal', models.PositiveIntegerField()),
                ('total_carbs', models.PositiveIntegerField()),
                ('total_fat', models.PositiveIntegerField()),
                ('total_protein', models.PositiveIntegerField()),
                ('products', models.ManyToManyField(to='calculator.product')),
                ('user', models.ManyToManyField(to='users.ketoappuser')),
            ],
        ),
    ]