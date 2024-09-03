from flask import render_template, Blueprint, flash, redirect, url_for, request, send_file
from flask_login import login_required, current_user
from . import requires_access_level, mysql
from .forms import *
from datetime import datetime
import os

doctor = Blueprint('doctor', __name__)

@doctor.route('/doctor', methods=['GET', 'POST'])
@doctor.route('/doctor/', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def doctor_dashboard():
    cur = mysql.connection.cursor()
    cur.execute("SELECT DISTINCT Patient.Patient_ID, Patient.Name, Patient.Age, Patient.Gender, Patient.Address ,Patient.Personal_Contact, Patient.Emergency_Contact FROM Treatment JOIN Patient WHERE Treatment.Patient_ID = Patient.Patient_ID and Treatment.Doctor_ID = %s", (current_user.Doctor_ID,))
    patients_treated = cur.fetchall()
    # delete those entries in appointments whose appointment date / appointment time has passed
    cur.execute("DELETE FROM Appointment WHERE Appointment_Date < %s OR (Appointment_Date = %s AND Appointment_Time < %s)", (datetime.now().date(), datetime.now().date(), datetime.now().time()))
    mysql.connection.commit()
    cur.execute("SELECT Appointment_ID, Appointment_Date, Appointment_Time, Patient.Name,  Patient.Age, Patient.Gender FROM Appointment JOIN Patient WHERE Appointment.Patient_ID = Patient.Patient_ID and Appointment.Doctor_ID = %s ORDER BY Appointment_Date, Appointment_Time", (current_user.Doctor_ID,))
    appointments = cur.fetchall()
    print(appointments)
    cur.close()
    return render_template('doctor_dashboard.html', name=current_user.Name, appointments=appointments, patients_treated=patients_treated, user = current_user)


@doctor.route('/doctor/query_patients', methods=['GET', 'POST'])
@doctor.route('/doctor/query_patients/', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def query_patients():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient")
    patients = cur.fetchall()
    cur.close()
    return render_template('doctor_query_patients.html', name=current_user.Name, patients=patients, user = current_user)

@doctor.route('/doctor/query_patients/<int:patient_id>', methods=['GET', 'POST'])
@doctor.route('/doctor/query_patients/<int:patient_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def query_patient(patient_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Treatment_ID, TreatmentDate, Category, Details, Document_Path FROM Treatment WHERE Patient_ID = %s", (patient_id,))
    treatments = cur.fetchall()
    cur.execute("SELECT Test_ID,TestDate,Category,BodyPart,Result,ResultObtained,Document_Path FROM Test WHERE Patient_ID = %s", (patient_id,))
    tests = cur.fetchall()
    tests_og = []
    for test in tests:
        if test[5] == False:
            coloro = "bg-light"
            textc = "text-dark"
        elif test[5] == True:
            coloro = "bg-light"
            textc = "text-dark"
        test = test + (coloro,) #7
        test = test + (textc,) #8
        if test[6] != None:
            filename = os.path.basename(test[6])
        else:
            filename = None
        test = test + (filename,) #9
        tests_og.append(test)

    filename = ""
    treatments_og = []
    for treatment in treatments:
        if treatment[4] != None:
            filename = os.path.basename(treatment[4])
        else:
            filename = None
        cur.execute("SELECT Name FROM Drugs_Prescribed WHERE Treatment_ID = %s", (treatment[0],))
        medicines = cur.fetchall()
        medicine = []
        for med in medicines:
            medicine.append(med[0])
        
        if treatment[2] == "General":
            color = "bg-primary"
        elif treatment[2] == "Operation":
            color = "bg-danger"
        else:
            color = "bg-success"
        treatment = treatment + (filename,)
        treatment = treatment + (medicine,)
        treatment = treatment + (color,)
        treatments_og.append(treatment)
    cur.close()
    form_1 = AddTreatmentForm()
    if form_1.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Treatment (TreatmentDate, Category, Details, Patient_ID, Doctor_ID) VALUES (%s, %s, %s, %s, %s)", (form_1.treatment_date.data, form_1.category.data, form_1.details.data, patient_id, current_user.Doctor_ID))
        mysql.connection.commit()
        cur.close()
        flash('Treatment added successfully.', category='success')
        return redirect(url_for('doctor.query_patient', patient_id=patient_id))
    form_2 = AddTestForm()
    if form_2.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Test (TestDate, Category, BodyPart, ResultObtained, Patient_ID) VALUES (%s, %s, %s, FALSE, %s)", (form_2.test_date.data, form_2.category.data, form_2.bodypart.data, patient_id))
        mysql.connection.commit()
        cur.close()
        flash('Test added successfully.', category='success')
        return redirect(url_for('doctor.query_patient', patient_id=patient_id))
    return render_template('doctor_patient_details.html', name=current_user.Name, treatments=treatments_og, tests = tests_og, user = current_user, form_1=form_1, form_2=form_2, patient_id=patient_id)

@doctor.route('/doctor/show/treatment_pdf', methods=['POST'])
@doctor.route('/doctor/show/treatment_pdf/', methods=['POST'])
@login_required
@requires_access_level(2)
def show_treatment_pdf():
    if request.method == 'POST':
        path = request.form['path']
        filename = request.form['filename']
        return send_file(path, as_attachment=True, download_name=filename)
    
@doctor.route('/doctor/show/test_pdf', methods=['POST'])
@login_required
@requires_access_level(2)
def show_test_pdf():
    if request.method == 'POST':
        path = request.form['path']
        filename = request.form['filename']
        return send_file(path, as_attachment=True, download_name=filename)
    
@doctor.route('/doctor/add_prescription' , methods=['GET', 'POST'])
@doctor.route('/doctor/add_prescription/' , methods=['GET', 'POST'])
@login_required
@requires_access_level(2)
def add_prescription():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Treatment_ID, TreatmentDate, Category, Details, Patient.Name, Patient.Age, Patient.Gender FROM Treatment JOIN Patient WHERE Treatment.Patient_ID = Patient.Patient_ID ")
    treated_patients = cur.fetchall()
    form = AddPrescriptionForm()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Drugs_Prescribed (Name, Treatment_ID) VALUES (%s, %s)", (form.medicine.data, form.treatment_id.data))
        mysql.connection.commit()
        cur.close()
        flash('Prescription added successfully.', category='success')
        return redirect(url_for('doctor.add_prescription'))
    return render_template('doctor_add_prescription.html', form = form ,name=current_user.Name, treated_patients = treated_patients ,user = current_user)

# @doctor.route('/doctor/add_treatment' , methods=['GET', 'POST'])
# @login_required
# @requires_access_level(2)
# def add_treatment():
#     form = AddTreatmentForm()
#     if form.validate_on_submit():
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO Treatment (TreatmentDate, Category, Details, Patient_ID, Doctor_ID) VALUES (%s, %s, %s, %s, %s)", (form.treatment_date.data, form.category.data, form.details.data, form.patient_id.data, current_user.Doctor_ID))
#         mysql.connection.commit()
#         cur.close()
#         flash('Treatment added successfully.', category='success')
#         return redirect(url_for('doctor.doctor_dashboard'))
#     return render_template('doctor_add_treatment.html', name=current_user.Name, form=form, user = current_user)

# @doctor.route('/doctor/add_test' , methods=['GET', 'POST'])
# @login_required
# @requires_access_level(2)
# def add_test():
#     form = AddTestForm()
#     if form.validate_on_submit():
#         cur = mysql.connection.cursor()
#         cur.execute("INSERT INTO Test (TestDate, Category, BodyPart, ResultObtained, Patient_ID) VALUES (%s, %s, %s, FALSE, %s)", (form.test_date.data, form.category.data, form.bodypart.data, form.patient_id.data))
#         mysql.connection.commit()
#         cur.close()
#         flash('Treatment added successfully.', category='success')
#         return redirect(url_for('doctor.doctor_dashboard'))
#     return render_template('doctor_add_test.html', name=current_user.Name, form=form, user = current_user)

@doctor.route('/report/doctor/<int:patient_id>', methods=['GET', 'POST'])
@doctor.route('/report/doctor/<int:patient_id>/', methods=['GET', 'POST'])
def report(patient_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT Treatment_ID, TreatmentDate, Category, Details, Document_Path FROM Treatment WHERE Patient_ID = %s", (patient_id,))
    treatments = cur.fetchall()
    cur.execute("SELECT Test_ID,TestDate,Category,BodyPart,Result,ResultObtained FROM Test WHERE Patient_ID = %s", (patient_id,))
    tests = cur.fetchall()
    cur.execute("SELECT Name FROM Patient WHERE Patient_ID = %s",(patient_id,))
    patient_name = cur.fetchone()[0]
    test_og = []
    for test in tests:
        if test[5] == False:
            coloro = "bg-light"
            textc = "text-dark"
        elif test[5] == True:
            coloro = "bg-light"
            textc = "text-dark"
        test = test + (coloro,)
        test = test + (textc,)
        test_og.append(test)

    filename = ""
    treatments_og = []
    for treatment in treatments:
        if treatment[4] != None:
            filename = os.path.basename(treatment[4])
        else:
            filename = None
        cur.execute("SELECT Name FROM Drugs_Prescribed WHERE Treatment_ID = %s", (treatment[0],))
        medicines = cur.fetchall()
        medicine = []
        for med in medicines:
            medicine.append(med[0])
        
        if treatment[2] == "General":
            color = "bg-primary"
        elif treatment[2] == "Operation":
            color = "bg-danger"
        else:
            color = "bg-success"
        treatment = treatment + (filename,)
        treatment = treatment + (medicine,)
        treatment = treatment + (color,)
        treatments_og.append(treatment)
    cur.close()
    return render_template('patient_details.html', treatments=treatments_og, tests = test_og, user = current_user, patient_id=patient_id,patient_name = patient_name)


