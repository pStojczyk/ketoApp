# Generated by Django 5.0.3 on 2024-03-22 11:01

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_ketoappuser_activity_ketoappuser_age_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keto_app_user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='users.ketoappuser')),
            ],
        ),
    ]
