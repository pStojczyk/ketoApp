# Generated by Django 5.0.3 on 2024-05-14 09:27

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('calculator', '0016_alter_fulldayintake_date_alter_product_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='fulldayintake',
            name='date',
            field=models.DateField(blank=True, null=True),
        ),
    ]