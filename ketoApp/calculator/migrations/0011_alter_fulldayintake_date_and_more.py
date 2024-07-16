# Generated by Django 5.0.3 on 2024-04-26 12:45

import django.db.models.functions.datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0010_remove_fulldayintake_products_fulldayintake_product'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fulldayintake',
            name='date',
            field=models.DateTimeField(db_default=django.db.models.functions.datetime.Now(), null=True),
        ),
        migrations.AlterField(
            model_name='fulldayintake',
            name='total_carbs',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='fulldayintake',
            name='total_fat',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='fulldayintake',
            name='total_kcal',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='fulldayintake',
            name='total_protein',
            field=models.PositiveIntegerField(null=True),
        ),
    ]