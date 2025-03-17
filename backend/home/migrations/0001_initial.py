# Generated by Django 5.1.7 on 2025-03-17 21:28

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Admin',
            fields=[
                ('userName', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'admin',
            },
        ),
        migrations.CreateModel(
            name='Area',
            fields=[
                ('areaCode', models.CharField(max_length=10, primary_key=True, serialize=False, unique=True)),
                ('areaName', models.CharField(max_length=100)),
            ],
            options={
                'db_table': 'area',
            },
        ),
        migrations.CreateModel(
            name='Machine',
            fields=[
                ('machineType', models.CharField(choices=[('Excavator', 'Excavator'), ('Bulldozer', 'Bulldozer'), ('Cement Mixer', 'Cement Mixer')], max_length=20, primary_key=True, serialize=False)),
                ('machineCount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'machine',
            },
        ),
        migrations.CreateModel(
            name='ManPower',
            fields=[
                ('workerType', models.CharField(choices=[('Electrician', 'Electrician'), ('Mason', 'Mason'), ('Plumber', 'Plumber')], max_length=15, primary_key=True, serialize=False)),
                ('workerCount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'manPower',
            },
        ),
        migrations.CreateModel(
            name='Material',
            fields=[
                ('materialType', models.CharField(choices=[('Cement', 'Cement'), ('Wiring', 'Wiring'), ('Pipes', 'Pipes')], max_length=15, primary_key=True, serialize=False)),
                ('materialCount', models.IntegerField(default=0)),
            ],
            options={
                'db_table': 'material',
            },
        ),
        migrations.CreateModel(
            name='Request',
            fields=[
                ('requestId', models.AutoField(primary_key=True, serialize=False)),
                ('service', models.CharField(choices=[('Road', 'Road'), ('Light', 'Light'), ('Drainage', 'Drainage')], max_length=10)),
                ('serviceCode', models.IntegerField()),
                ('description', models.TextField(blank=True, null=True)),
                ('progress', models.IntegerField(default=0)),
                ('status', models.CharField(choices=[('Pending', 'Pending'), ('Completed', 'Completed'), ('Under work', 'Under work')], default='Pending', max_length=15)),
                ('areaCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'request',
            },
        ),
        migrations.CreateModel(
            name='Drainage',
            fields=[
                ('drainageId', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('status', models.BooleanField(default=False)),
                ('areaCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'drainage',
            },
        ),
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('requestId', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='home.request')),
                ('raiseDate', models.DateTimeField(auto_now_add=True)),
                ('startDate', models.DateTimeField(blank=True, null=True)),
                ('finishDate', models.DateTimeField(blank=True, null=True)),
            ],
            options={
                'db_table': 'stats',
            },
        ),
        migrations.CreateModel(
            name='Road',
            fields=[
                ('roadId', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('areaCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'road',
            },
        ),
        migrations.CreateModel(
            name='StreetLight',
            fields=[
                ('streetLightId', models.IntegerField(primary_key=True, serialize=False, unique=True)),
                ('status', models.BooleanField(default=False)),
                ('areaCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'streetLight',
            },
        ),
        migrations.CreateModel(
            name='Supervisor',
            fields=[
                ('userName', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('areaCode', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'supervisor',
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('userName', models.CharField(max_length=100, primary_key=True, serialize=False, unique=True)),
                ('password', models.CharField(max_length=100)),
                ('areaCode', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.area')),
            ],
            options={
                'db_table': 'user',
            },
        ),
        migrations.CreateModel(
            name='SchedulingQueue',
            fields=[
                ('requestId', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='home.request')),
                ('priority', models.IntegerField()),
            ],
            options={
                'db_table': 'schedulingQueue',
                'constraints': [models.CheckConstraint(condition=models.Q(('priority__gte', 0), ('priority__lte', 5)), name='priority_range')],
            },
        ),
        migrations.CreateModel(
            name='ReqMaterial',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('materialCount', models.IntegerField(default=0)),
                ('materialType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.material')),
                ('requestId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.request')),
            ],
            options={
                'db_table': 'reqMaterial',
                'constraints': [models.UniqueConstraint(fields=('requestId', 'materialType'), name='unique_request_material')],
            },
        ),
        migrations.CreateModel(
            name='ReqManpower',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('workerCount', models.IntegerField(default=0)),
                ('workerType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.manpower')),
                ('requestId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.request')),
            ],
            options={
                'db_table': 'reqManpower',
                'constraints': [models.UniqueConstraint(fields=('requestId', 'workerType'), name='unique_request_worker')],
            },
        ),
        migrations.CreateModel(
            name='ReqMachine',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('machineCount', models.IntegerField(default=0)),
                ('machineType', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.machine')),
                ('requestId', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='home.request')),
            ],
            options={
                'db_table': 'reqMachine',
                'constraints': [models.UniqueConstraint(fields=('requestId', 'machineType'), name='unique_request_machine')],
            },
        ),
    ]
