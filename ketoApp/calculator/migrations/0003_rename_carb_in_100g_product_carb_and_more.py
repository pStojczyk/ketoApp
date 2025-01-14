# Generated by Django 5.0.3 on 2024-04-20 16:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0002_product_kcal_in_100g_alter_product_carb_in_100g_and_more'),
    ]

    operations = [
        migrations.RenameField(
            model_name='product',
            old_name='carb_in_100g',
            new_name='carb',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='fat_in_100g',
            new_name='fat',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='kcal_in_100g',
            new_name='grams',
        ),
        migrations.RenameField(
            model_name='product',
            old_name='protein_in_100g',
            new_name='kcal',
        ),
        migrations.AddField(
            model_name='product',
            name='protein',
            field=models.PositiveIntegerField(null=True),
        ),
        migrations.AlterField(
            model_name='product',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]
