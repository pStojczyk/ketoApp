# Generated by Django 5.0.3 on 2024-04-26 08:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0006_alter_product_grams'),
        ('users', '0010_alter_demand_keto_app_user'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='product',
            name='user',
        ),
        migrations.AddField(
            model_name='product',
            name='user',
            field=models.ManyToManyField(null=True, to='users.ketoappuser'),
        ),
    ]
