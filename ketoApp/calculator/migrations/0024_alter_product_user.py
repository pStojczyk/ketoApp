# Generated by Django 5.0.3 on 2025-01-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0023_alter_product_user'),
        ('users', '0012_alter_ketoappuser_gender'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='user',
            field=models.ManyToManyField(to='users.ketoappuser'),
        ),
    ]