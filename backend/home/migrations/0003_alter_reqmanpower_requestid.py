# Generated by Django 5.1.7 on 2025-03-22 17:31

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('home', '0002_alter_reqmanpower_workertype'),
    ]

    operations = [
        migrations.AlterField(
            model_name='reqmanpower',
            name='requestId',
            field=models.ForeignKey(db_column='requestId', on_delete=django.db.models.deletion.CASCADE, to='home.request'),
        ),
    ]
