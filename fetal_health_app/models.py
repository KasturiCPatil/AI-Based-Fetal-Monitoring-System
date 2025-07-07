from django.db import models

# Create your models here.
class Patient_Registration(models.Model):
    fullname=models.CharField(max_length=20)
    husbandname=models.CharField(max_length=20)
    emailid=models.CharField(max_length=20)
    phoneno=models.CharField(max_length=20)
    dateofbirth=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    address=models.CharField(max_length=100)
    age=models.CharField(max_length=5)
    hospital=models.CharField(max_length=50)
     # Default field
    status = models.IntegerField(default='zero')

class Doctor_Registration(models.Model):
    fullname=models.CharField(max_length=20)
    emailid=models.CharField(max_length=20)
    phoneno=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    address=models.CharField(max_length=100)
    hospital=models.CharField(max_length=50)
     # Default field
    status = models.IntegerField(default='zero')

class Lab_Technician_Registration(models.Model):
    fullname=models.CharField(max_length=20)
    emailid=models.CharField(max_length=20)
    phoneno=models.CharField(max_length=20)
    password=models.CharField(max_length=20)
    address=models.CharField(max_length=100)
    hospital=models.CharField(max_length=50)
     # Default field
    status = models.IntegerField(default=0)

class Fetal_Report(models.Model):
    lab_emailid=models.CharField(max_length=20)
    patient_phoneno=models.CharField(max_length=15)
    hospital_name=models.CharField(max_length=25)
    doctor_mailid=models.CharField(max_length=25)
    bv=models.CharField(max_length=10)
    acc=models.CharField(max_length=10)
    auc=models.CharField(max_length=10)
    astv=models.CharField(max_length=10)
    mvstv=models.CharField(max_length=10)
    ptwa=models.CharField(max_length=10)
    hw=models.CharField(max_length=10)
    hm=models.CharField(max_length=10)
    hnp=models.CharField(max_length=10)
    hme=models.CharField(max_length=10)
    result=models.CharField(max_length=50)
    status = models.IntegerField(default=0)
    added_date = models.DateField(auto_now_add=True)
    added_time = models.TimeField(auto_now_add=True)

class Book_Appointments(models.Model):
    patient_phoneno=models.CharField(max_length=15)
    doctor_mailid=models.CharField(max_length=25)
    appointment_date=models.CharField(max_length=25)
    appointment_time=models.CharField(max_length=25)
    reason=models.CharField(max_length=250)
    status = models.IntegerField(default=0)



