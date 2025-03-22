from django.db import models
from django.contrib.auth.hashers import make_password, check_password
# Create your models here.

class Area(models.Model):
    areaCode = models.CharField(primary_key=True, unique=True, max_length=10)
    areaName = models.CharField(max_length=100, null = False)

    class Meta:
        db_table = 'area'

class User(models.Model):
    userName = models.CharField(primary_key=True, unique =True, max_length=100)
    password = models.CharField(max_length=100)
    areaCode = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')
    def save(self, *args, **kwargs):
        if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'user'
    
class Supervisor(models.Model):
    userName = models.CharField(primary_key=True, unique=True, max_length=100)
    password = models.CharField(max_length=100)
    areaCode = models.OneToOneField(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')
    def save(self, *args, **kwargs):
        if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'supervisor'
    
class Admin(models.Model):
    userName = models.CharField(primary_key=True, unique=True, max_length=100)
    password = models.CharField(max_length=100)
    def save(self, *args, **kwargs):
        if not self.password.startswith(('pbkdf2_sha256$', 'bcrypt$', 'argon2$')):
            self.password = make_password(self.password)
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'admin'

class Road(models.Model):
    roadId = models.IntegerField(primary_key=True, unique=True) 
    areaCode = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')

    class Meta:
        db_table = 'road'

class StreetLight(models.Model):
    streetLightId = models.IntegerField(primary_key = True, unique = True)
    areaCode = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')
    status = models.BooleanField(default = False)

    class Meta:
        db_table = 'streetLight'

class Drainage(models.Model):
    drainageId = models.IntegerField(primary_key = True, unique = True)
    areaCode = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')
    status = models.BooleanField(default = False)

    class Meta:
        db_table = 'drainage'

class Request(models.Model):
    SERVICE_CHOICES = [
        ('Road', 'Road'),
        ('Light', 'Light'),
        ('Drainage', 'Drainage')
    ]

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Completed', 'Completed'),
        ('Under work', 'Under work')
    ]

    requestId = models.AutoField(primary_key=True)
    areaCode = models.ForeignKey(Area, on_delete=models.CASCADE, to_field='areaCode', db_column='areaCode')
    service = models.CharField(max_length=10, choices=SERVICE_CHOICES)
    serviceCode = models.IntegerField()
    description = models.TextField(blank=True, null=True)
    progress = models.IntegerField(default=0)
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        db_table = 'request'
    
class SchedulingQueue(models.Model):
    requestId = models.OneToOneField(Request, on_delete=models.CASCADE, primary_key=True, to_field='requestId', db_column='requestId')
    priority = models.IntegerField()
    
    class Meta:
        db_table = 'schedulingQueue'
        constraints = [
            models.CheckConstraint(check=models.Q(priority__gte=0) & models.Q(priority__lte=5), name='priority_range')
        ]

class Stats(models.Model):
    requestId = models.OneToOneField(Request, on_delete=models.CASCADE, primary_key=True, to_field='requestId', db_column='requestId')
    raiseDate = models.DateTimeField(auto_now_add=True)
    startDate = models.DateTimeField(null=True, blank=True)
    finishDate = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'stats'
    
class ManPower(models.Model):
    WORKER_TYPES = [
        ('Electrician', 'Electrician'),
        ('Mason', 'Mason'),
        ('Plumber', 'Plumber')
    ]
    
    workerType = models.CharField(max_length=15, choices=WORKER_TYPES, primary_key=True)
    workerCount = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'manPower'
    
class Machine(models.Model):
    MACHINE_TYPES = [
        ('Excavator', 'Excavator'),
        ('Bulldozer', 'Bulldozer'),
        ('Cement Mixer', 'Cement Mixer')
    ]
    
    machineType = models.CharField(max_length=20, choices=MACHINE_TYPES, primary_key=True)
    machineCount = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'machine'
    
class Material(models.Model):
    MATERIAL_TYPES = [
        ('Cement', 'Cement'),
        ('Wiring', 'Wiring'),
        ('Pipes', 'Pipes')
    ]
    
    materialType = models.CharField(max_length=15, choices=MATERIAL_TYPES, primary_key=True)
    materialCount = models.IntegerField(default=0)
    
    class Meta:
        db_table = 'material'
    
class ReqManpower(models.Model):
    requestId = models.ForeignKey(Request, on_delete=models.CASCADE, to_field='requestId', db_column='requestId')
    workerType = models.ForeignKey(ManPower, on_delete=models.CASCADE, to_field='workerType', db_column='workerType')
    workerCount = models.IntegerField(default=0)

    class Meta:
        db_table = 'reqManpower'
        constraints = [
        models.UniqueConstraint(fields=['requestId', 'workerType'], name='unique_request_worker')
        ]

class ReqMachine(models.Model):
    requestId = models.ForeignKey(Request, on_delete=models.CASCADE, to_field='requestId', db_column='requestId')
    machineType = models.ForeignKey(Machine, on_delete=models.CASCADE, to_field='machineType', db_column='machineType')
    machineCount = models.IntegerField(default=0)

    class Meta:
        db_table = 'reqMachine'
        constraints = [
        models.UniqueConstraint(fields=['requestId', 'machineType'], name='unique_request_machine')
        ]
    
class ReqMaterial(models.Model):
    requestId = models.ForeignKey(Request, on_delete=models.CASCADE, to_field='requestId', db_column='requestId')
    materialType = models.ForeignKey(Material, on_delete=models.CASCADE, to_field='materialType', db_column='materialType')
    materialCount = models.IntegerField(default=0)

    class Meta:
        db_table = 'reqMaterial'
        constraints = [
        models.UniqueConstraint(fields=['requestId', 'materialType'], name='unique_request_material')
        ]