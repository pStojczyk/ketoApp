# Generated by Django 5.0.3 on 2024-04-09 16:25

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0004_ketoappuser_cmp_ketoappuser_daily_carbs_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Profile',
        ),
    ]
