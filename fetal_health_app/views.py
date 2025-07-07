from django.shortcuts import render
from django.http import HttpResponse
import pymongo
from .models import *
from django.conf import settings
from bson.objectid import ObjectId
import os
import pickle
import numpy as np
import joblib
from datetime import datetime
from django.utils.timezone import now
from django.core.serializers.json import DjangoJSONEncoder
import json
from django.core.mail import send_mail
import smtplib
from email.mime.text import MIMEText


# Create your views here.
my_client = pymongo.MongoClient(settings.DB_NAME)
dbname = my_client['fetal_db']
patient_registration = dbname["Patient_Registration"]
doctor_registration = dbname['Doctor_Registration']
lab_technician_registration=dbname['Lab_Technician_Registration']
fetal_report=dbname['Fetal_Report']
book_patient_appointment=dbname['Book_Appointments']
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.path.join(BASE_DIR, 'fetal_health_app', 'ml_model', 'logistic_regression_model.pkl')

def load_model():
    with open(MODEL_PATH, 'rb') as file:
        model = pickle.load(file)
    return model
def index(request):
    return render(request,'index.html')

def patient_login(request):
    return render(request,'userlogin.html')

def doctor_login(request):
    return render(request,'doctorlogin.html')

def lab_login(request):
    return render(request,'lablogin.html')

def admin_login(request):
    return render(request,'adminlogin.html')

def patient_register(request):
    return render(request,'patient_register.html')

def doctor_register(request):
    return render(request,'doctor_register.html')

def lab_register(request):
    return render(request,'lab_register.html')

def save_patient(request):
    error=False
    if request.method == "POST":
        fullname=request.POST['fullname']
        husbandname=request.POST['husbandname']
        emailid=request.POST['emailid']
        phoneno=request.POST['phoneno']
        dateofbirth=request.POST['dateofbirth']
        address=request.POST['address']
        password=request.POST['password']
        age=request.POST['age']
        hospital=request.POST['hospital']
        if patient_registration.count_documents({'phoneno':phoneno}):
            error=True
            message="Data already exists"
            d={'message':message,'error':error}
            return render(request, 'patient_register.html', d)
        else:
             patient = {
                "fullname": fullname,
                "husbandname" : husbandname,
                "emailid" : emailid,
                "phoneno" : phoneno,
                "dateofbirth": dateofbirth,
                "address":address,
                "password":password,
                "age":age,
                "hospital":hospital
            }
             patient_registration.insert_one(patient)
             error=True
             message="Data saved successfully"
             d={'message':message,'error':error}
             return render(request,'patient_register.html')
        
def save_doctor(request):
    error=False
    if request.method == "POST":
        fullname=request.POST['fullname']
        emailid=request.POST['emailid']
        phoneno=request.POST['phoneno']
        address=request.POST['address']
        password=request.POST['password']
        hospital=request.POST['hospital']
        if doctor_registration.count_documents({'phoneno':phoneno}):
            error=True
            message="Data already exists"
            d={'message':message,'error':error}
            return render(request, 'doctor_register.html', d)
        else:
             doctor = {
                "fullname": fullname,
                "emailid" : emailid,
                "phoneno" : phoneno,
                "address":address,
                "password":password,
                "hospital":hospital,
                "status":0
            }
             doctor_registration.insert_one(doctor)
             error=True
             message="Data saved successfully"
             d={'message':message,'error':error}
             return render(request,'doctor_register.html')


def save_lab_technician(request):
    error=False
    if request.method == "POST":
        fullname=request.POST['fullname']
        emailid=request.POST['emailid']
        phoneno=request.POST['phoneno']
        address=request.POST['address']
        password=request.POST['password']
        hospital=request.POST['hospital']
        if lab_technician_registration.count_documents({'phoneno':phoneno}):
            error=True
            message="Data already exists"
            d={'message':message,'error':error}
            return render(request, 'lab_register.html', d)
        else:
             lab = {
                "fullname": fullname,
                "emailid" : emailid,
                "phoneno" : phoneno,
                "address":address,
                "password":password,
                "hospital":hospital,
                "status":0
            }
             lab_technician_registration.insert_one(lab)
             error=True
             message="Data saved successfully"
             d={'message':message,'error':error}
             return render(request,'lab_register.html')
        
def admin_login_check(request):
    error=False
    if request.method == "POST":
        emailid=request.POST['emailid']
        password=request.POST['password']
        if emailid=="admin@gmail.com" and password=="admin":
            return render(request,'adminpage.html')
        else:
            error=True
            message="Invalid Credentials"
            d={'error':error,'message':message}
            return render(request,'adminlogin.html',d)
def view_lab_technicians(request):
    return render(request,'view_lab_technician.html')


def lab_technician_login_check(request):
    error = False
    if request.method == "POST":
        emailid = request.POST['emailid']
        password = request.POST['password']
        myquery = {'emailid': emailid, 'password': password} 
        if lab_technician_registration.count_documents(myquery):
            request.session['lab_technician_mailid'] = emailid    
            doctors = list(doctor_registration.find())
            patients = list(patient_registration.find())  
            patient_number = [patient['phoneno'] for patient in patients]
            context = {
                'doctors': doctors,
                'patients': patient_number
            }
            return render(request, 'labtechnicianpage.html', context)
        else:
            error = True
            message = "Invalid Credentials"
            context = {'error': error, 'message': message}
            return render(request, "lablogin.html", context)

def technician_upload_page(request):
    doctors = list(doctor_registration.find())
    patients = list(patient_registration.find())  
    patient_number = [patient['phoneno'] for patient in patients]
    context = {
                'doctors': doctors,
                'patients': patient_number
    }
    return render(request, 'labtechnicianpage.html', context)

def send_notification_email(recipient_email, subject, message):
    sender_email = "healthfetal@gmail.com"
    app_password = "piwz aapp ppaa rgij"  # use App Password

    msg = MIMEText(message)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(sender_email, app_password)
        server.sendmail(sender_email, recipient_email, msg.as_string())

def predict_save(request):
 if request.method == "POST":
    lab_technician_mailid = request.session.get('lab_technician_mailid')
    hospital=request.POST['hospital']
    doctor_mailid=request.POST['doctor_name']
    patient=request.POST['patient_number']
    bv = float(request.POST['bv'])
    acc = float(request.POST['acc'])
    auc = float(request.POST['auc'])
    astv = float(request.POST['astv'])
    mvstv = float(request.POST['mvstv'])
    ptwa = float(request.POST['ptwa'])
    hw = float(request.POST['hw'])
    hm = float(request.POST['hm'])
    hnp = float(request.POST['hnp'])
    hme = float(request.POST['hme'])
    model=joblib.load(MODEL_PATH)
    user_data = np.array([[bv, acc, auc, astv, mvstv, ptwa, hw, hm, hnp, hme]])
    doctors = list(doctor_registration.find())
    patients = list(patient_registration.find())  
    patient_number = [patient['phoneno'] for patient in patients]
    prediction = model.predict(user_data)
    if prediction == 1:
        result = "Fetal Health is Normal"
    elif prediction == 2:
        result = "Fetal Health is Suspect"
    elif prediction == 3:
        result = "Fetal Health is Pathological"
    
    fetal={
        'lab_emailid':lab_technician_mailid,
        'patient_phoneno':patient,
        'hospital_name':hospital,
        'doctor_mailid':doctor_mailid,
        'bv':bv,
        'acc':acc,
        'auc':auc,
        'astv':astv,
        'mvstv':mvstv,
        'ptwa':ptwa,
        'hw':hw,
        'hm':hm,
        'hnp':hnp,
        'hme':hme,
        'result':result,
        'status': 0,
        'added_date': datetime.now().date().isoformat(),  # or str(datetime.date.today())
        'added_time': datetime.now().time().isoformat(timespec='seconds')
    }
    fetal_report.insert_one(fetal)
    patient_email=""
    m_patient = patient_registration.find_one({'phoneno': patient})
    print(m_patient)
    if m_patient:
        patient_email = m_patient.get("emailid")
    print("User Mail:",patient_email)
    send_notification_email(
            recipient_email=patient_email,
            subject='Your Report is Ready!',
            message='Hello, your fetal monitoring report has been uploaded. Please check your dashboard.'
        )
    save_status="Report Uploaded"
    context={'prediction':result,'doctors': doctors,
                'patients': patient_number, 'save_status':save_status}
    return render(request,'labtechnicianpage.html',context)
 
def lab_report_view(request):
    report = []
    lab_technician_mailid = request.session.get('lab_technician_mailid')   
    report_data = fetal_report.find({'lab_emailid': lab_technician_mailid})  
    for rd in report_data:
        rd['report_id'] = str(rd['_id'])  # Convert ObjectId to string for template use
        report.append(rd)  
    context = {'reports': report}
    return render(request, 'labreportview.html', context)


def delete_report(request):
    error=False
    report=[]
    if request.method == "POST":
        report_id=ObjectId(request.POST['id'])
        fetal_report.delete_one({'_id':report_id})
        error=True
        message="Record Deleted"
        lab_technician_mailid = request.session.get('lab_technician_mailid')
        report_data=fetal_report.find({'lab_emailid':lab_technician_mailid})
        for rd in report_data:
            rd['report_id']=str(rd['_id'])
            report.append(rd)
        #report=list(report_data)
        context={'reports':report,'error':error,'message':message}
        return render(request,'labreportview.html',context)

def doctor_report_view(request):
    report = []
    emailid = request.session.get('doctor_mailid')
    report_data = fetal_report.find({'doctor_mailid': emailid})  
    for rd in report_data:
        rd['report_id'] = str(rd['_id'])  # Convert ObjectId to string for template use
        report.append(rd)  
    context = {'reports': report}
    return render(request,'doctorpage.html',context)

def doctor_individual_view(request):
    if request.method == "POST":
        report_id=ObjectId(request.POST['id'])
        report_data=fetal_report.find_one({'_id':report_id})
        doctor_mailid=report_data.get('doctor_mailid')
        patient_number=report_data.get('patient_phoneno')
        doctor_data=doctor_registration.find_one({'emailid':doctor_mailid})
        patient_data=patient_registration.find_one({'phoneno':patient_number})
        doctor_name=doctor_data.get("fullname")
        doctor_hospital=doctor_data.get("hospital")
        patient_name=patient_data.get("fullname")
        reports=list(report_data)
        status=1
        fetal_report.update_one({'_id': report_id},{'$set': {'status': status}})
        context={'rd':report_data,'doctor_name':doctor_name,'doctor_hospital':doctor_hospital,'patient_name':patient_name,"patient_phoneno":patient_number}
    return render(request,'doctorindividualreport.html',context)

def doctor_login_check(request):
    error = False
    if request.method == "POST":
        emailid = request.POST['emailid']
        password = request.POST['password']
        myquery = {'emailid': emailid, 'password': password} 
        if doctor_registration.count_documents(myquery):
            request.session['doctor_mailid'] = emailid
            report = []
            report_data = fetal_report.find({'doctor_mailid': emailid})  
            for rd in report_data:
                rd['report_id'] = str(rd['_id'])  
                report.append(rd)  
            context = {'reports': report}   
            return render(request,"doctorpage.html",context)     
        else:
            error = True
            message = "Invalid Credentials"
            context = {'error': error, 'message': message}
            return render(request, "doctorlogin.html", context)
    return render(request,"doctorpage.html")

def patien_login_check(request):
    error = False
    if request.method == "POST":
        emailid = request.POST['emailid']
        password = request.POST['password']
        myquery = {'emailid': emailid, 'password': password} 
        if patient_registration.count_documents(myquery):
            patient_data=patient_registration.find_one(myquery)
            print("Emailid ID is:",emailid)
            patient_phoneno=patient_data.get("phoneno")
            print("Phone Number is:",patient_phoneno)
            request.session['patient_phoneno'] = patient_phoneno
            report_data=fetal_report.find({'patient_phoneno':patient_phoneno})
            final_report=list(report_data)
            print(final_report)
            context = {
                'report': final_report,
                'patient_phoneno': patient_phoneno,
                'dates': json.dumps([str(report['added_date']) for report in final_report], cls=DjangoJSONEncoder),
                'acc': json.dumps([report['acc'] for report in final_report], cls=DjangoJSONEncoder),
                'bv': json.dumps([report['bv'] for report in final_report], cls=DjangoJSONEncoder),
                'auc': json.dumps([report['auc'] for report in final_report], cls=DjangoJSONEncoder),
                'hw':json.dumps([report['hw'] for report in final_report], cls=DjangoJSONEncoder),
                'hm':json.dumps([report['hm'] for report in final_report], cls=DjangoJSONEncoder),
                'results': json.dumps([report['result'] for report in final_report], cls=DjangoJSONEncoder)
            }
            return render(request,"patientpage.html",context)     
        else:
            error = True
            message = "Invalid Credentials"
            context = {'error': error, 'message': message}
            return render(request, "patientpage.html", context)

def user_dashboard(request):
    patient_phoneno = request.session.get('patient_phoneno')
    report_data=fetal_report.find({'patient_phoneno':patient_phoneno})
    final_report=list(report_data)
    print(final_report)
    context = {
            'report': final_report,
            'patient_phoneno': patient_phoneno,
            'dates': json.dumps([str(report['added_date']) for report in final_report], cls=DjangoJSONEncoder),
            'acc': json.dumps([report['acc'] for report in final_report], cls=DjangoJSONEncoder),
            'bv': json.dumps([report['bv'] for report in final_report], cls=DjangoJSONEncoder),
            'auc': json.dumps([report['auc'] for report in final_report], cls=DjangoJSONEncoder),
            'hw':json.dumps([report['hw'] for report in final_report], cls=DjangoJSONEncoder),
            'hm':json.dumps([report['hm'] for report in final_report], cls=DjangoJSONEncoder),
            'results': json.dumps([report['result'] for report in final_report], cls=DjangoJSONEncoder)
            }
    return render(request,"patientpage.html",context) 

def view_patient_reports(request):
    report = []
    patient_phoneno = request.session.get('patient_phoneno')
    report_data = fetal_report.find({'patient_phoneno': patient_phoneno})  
    for rd in report_data:
        rd['report_id'] = str(rd['_id'])  # Convert ObjectId to string for template use
        report.append(rd)  
    context = {'reports': report}
    return render(request,'patient_report_page.html',context)

def health_tips_patient(request):
    return render(request,'patient_health_tips.html')

def food_tips_patient(request):
    return render(request,'patient_food_tips.html')

def book_appointments(request):
    doctor_mailids=set()
    patient_phoneno = request.session.get('patient_phoneno')
    report_data = fetal_report.find({'patient_phoneno': patient_phoneno}) 
    for report in report_data:
        value=report.get('doctor_mailid')
        if value:
            doctor_mailids.add(value)
    doctor_details = []
    print("Doctor MailIDs:",doctor_mailids)
    if doctor_mailids:
        doctor_details = list(doctor_registration.find({'emailid': {'$in': list(doctor_mailids)}}))
    print("Doctor details:",doctor_details)
    context={'doctors':doctor_details}
    return render(request,'book_appoinments.html',context)

def buy_products(request):
    return render(request,'product.html')

def index_page(request):
    return render(request,'index.html')

def view_admin_page(request):
    return render(request,'adminpage.html')

def view_admin_doctors(request):
    doctors=doctor_registration.find()
    error=False
    message=""
    if request.method=='POST':
        emailid=request.POST['id']
        doctor_registration.delete_one({'emailid':emailid})
        error=True
        message="Doctor deleted"
        context={'doctors':doctors,'error':error,'message':message}
    context={'doctors':doctors,'error':error,'message':message}
    return render(request,'view_admin_doctors.html',context)

def view_admin_technician(request):
    lab_tech=lab_technician_registration.find()
    error=False
    message=""
    if request.method=='POST':
        emailid=request.POST['id']
        lab_technician_registration.delete_one({'emailid':emailid})
        error=True
        message="Lab Technician deleted"
        context={'doctors':lab_tech,'error':error,'message':message}
    context={'doctors':lab_tech,'error':error,'message':message}
    return render(request,'view_lab_technician.html',context)


def view_admin_user(request):
    user=patient_registration.find()
    error=False
    message=""
    if request.method=='POST':
        emailid=request.POST['id']
        patient_registration.delete_one({'emailid':emailid})
        error=True
        message="Patient deleted"
        context={'doctors':user,'error':error,'message':message}
    context={'doctors':user,'error':error,'message':message}
    return render(request,'view_lab_technician.html',context)

def patient_individual_view(request):
    if request.method == "POST":
        report_id=ObjectId(request.POST['id'])
        report_data=fetal_report.find_one({'_id':report_id})
        doctor_mailid=report_data.get('doctor_mailid')
        patient_number=report_data.get('patient_phoneno')
        doctor_data=doctor_registration.find_one({'emailid':doctor_mailid})
        patient_data=patient_registration.find_one({'phoneno':patient_number})
        doctor_name=doctor_data.get("fullname")
        doctor_hospital=doctor_data.get("hospital")
        patient_name=patient_data.get("fullname")
        reports=list(report_data)
        context={'rd':report_data,'doctor_name':doctor_name,'doctor_hospital':doctor_hospital,'patient_name':patient_name,"patient_phoneno":patient_number}
    return render(request,'patientindividualview.html',context)

def doctor_report_view(request):
    emailid= request.session.get('doctor_mailid')
    report = []
    report_data = fetal_report.find({'doctor_mailid': emailid})  
    for rd in report_data:
        rd['report_id'] = str(rd['_id'])  
        report.append(rd)  
    context = {'reports': report}   
    return render(request,"doctorpage.html",context) 

def save_appointment(request):
    error=False
    message=""
    if request.method=='POST':
        patient_number=request.session.get('patient_phoneno')
        dc_mailid=request.POST['doctor_name']
        appointment_date=request.POST['appointment_date']
        appointment_time=request.POST['appointment_time']
        reason=request.POST['reason']
        check_exists={'patient_phoneno':patient_number,'doctor_mailid':dc_mailid,'appointment_date':appointment_date,'appointment_time':appointment_time}
        if book_patient_appointment.count_documents(check_exists):
            error=True
            message="Data does not exists"
        else:
            p_appointment={
                'patient_phoneno':patient_number,
                'doctor_mailid':dc_mailid,
                'appointment_date':appointment_date,
                'appointment_time':appointment_time,
                'reason':reason,
                'status':0
            }
            book_patient_appointment.insert_one(p_appointment)
            error=True
            message="Request sent for appointment"
        doctor_mailids=set()
        patient_phoneno = request.session.get('patient_phoneno')
        report_data = fetal_report.find({'patient_phoneno': patient_phoneno}) 
        for report in report_data:
            value=report.get('doctor_mailid')
            if value:
                doctor_mailids.add(value)
        doctor_details = []
        if doctor_mailids:
            doctor_details = list(doctor_registration.find({'doctor_mailid': {'$in': list(doctor_mailids)}}))
        context={'doctors':doctor_details,'error':error,'message':message}
    return render(request,'book_appoinments.html',context)

def view_all_appointments(request):
    patient_phoneno = request.session.get('patient_phoneno')
    reports = list(book_patient_appointment.find({'patient_phoneno': patient_phoneno}))  # Make it list first!

    # Collect all doctor_mailids
    doctor_mailids = set()
    for report in reports:
        doctor_mailids.add(report.get('doctor_mailid'))

    # Fetch doctor details
    doctor_info = {}
    if doctor_mailids:
        doctors = doctor_registration.find({'emailid': {'$in': list(doctor_mailids)}})
        for doctor in doctors:
            # Make a mapping: doctor_mailid --> doctor_name
            doctor_info[doctor['emailid']] = doctor['fullname']

    # Now, attach doctor_name into each report
    for report in reports:
        doctor_mailid = report.get('doctor_mailid')
        report['doctor_name'] = doctor_info.get(doctor_mailid, 'Unknown Doctor')

    # Pass to template
    context = {'reports': reports}
    return render(request, 'view_appointments.html', context)

def doctor_view_appointments(request):
    error=False
    context=""
    message=""
    if request.method=='POST':
        patient_name=request.POST['patient_name']
        appointment_date=request.POST['appointment_date']
        appointment_time=request.POST['appointment_time']
        status=1
        patients=patient_registration.find_one({'fullname':patient_name})
        phoneno=patients.get("phoneno")
        book_patient_appointment.update_one({'patient_phoneno':phoneno,'appointment_date':appointment_date,'appointment_time':appointment_time},{'$set': {'status': status}})
        error=True
        message="Appointment accepted"
        patient_email=""
        m_patients=patient_registration.find_one({'fullname':patient_name})
        if m_patients:
            patient_email=m_patients.get("emailid")
        send_notification_email(
            recipient_email=patient_email,
            subject='Appointment Status',
            message='Your appointment dated on '+appointment_date+" and time "+appointment_time+" has been accepted"
        )
    emailid= request.session.get('doctor_mailid')
    reports = list(book_patient_appointment.find({'doctor_mailid': emailid}))  # Make it list first!

    # Collect all doctor_mailids
    patients_phoneno = set()
    for report in reports:
        patients_phoneno.add(report.get('patient_phoneno'))

    # Fetch doctor details
    patient_info = {}
    if patients_phoneno:
        doctors = patient_registration.find({'phoneno': {'$in': list(patients_phoneno)}})
        for doctor in doctors:
            # Make a mapping: doctor_mailid --> doctor_name
            patient_info[doctor['phoneno']] = doctor['fullname']

    # Now, attach doctor_name into each report
    for report in reports:
        patient_number = report.get('patient_phoneno')
        report['fullname'] = patient_info.get(patient_number, 'Unknown Patient')

    # Pass to template
    context = {'reports': reports,'error':error,'message':message}
    return render(request,'doctor_view_appointments.html',context)