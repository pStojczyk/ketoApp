# Generated by Django 5.0.3 on 2024-11-16 11:08

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0020_remove_fulldayintake_end'),
    ]

    operations = [
        migrations.AlterField(
            model_name='product',
            name='grams',
            field=models.PositiveIntegerField(null=True),
        ),
    ]