# Generated by Django 5.0.3 on 2024-04-26 07:34

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0004_alter_product_name'),
        ('users', '0010_alter_demand_keto_app_user'),
    ]

    operations = [
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='users.ketoappuser'),
        ),
    ]