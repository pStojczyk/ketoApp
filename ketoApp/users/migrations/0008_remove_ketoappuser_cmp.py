# Generated by Django 5.0.3 on 2024-04-18 19:31

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0007_alter_ketoappuser_activity'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='ketoappuser',
            name='cmp',
        ),
    ]