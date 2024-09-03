from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import requires_access_level, mysql
from werkzeug.utils import secure_filename
from .forms import *
import os

deo = Blueprint('deo', __name__)

@deo.route('/dataentry')
@deo.route('/dataentry/')
@login_required
@requires_access_level(4)
def dataentry():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Test_ID , TestDate,  Category , Patient.Name, BodyPart FROM Test JOIN Patient where Test.Patient_ID = Patient.Patient_ID and Test.ResultObtained = 0")
    incomplete_tests = cur.fetchall()
    cur.execute("SELECT Test_ID , TestDate,  Category , Patient.Name, BodyPart , Result FROM Test JOIN Patient where Test.Patient_ID = Patient.Patient_ID and Test.ResultObtained = 1")
    complete_tests = cur.fetchall()
    cur.execute("SELECT Treatment_ID, TreatmentDate, Category, Details, Doctor.Name, Patient.Name FROM Treatment JOIN Patient JOIN Doctor where Treatment.Patient_ID = Patient.Patient_ID and Treatment.Doctor_ID = Doctor.Doctor_ID")
    treatments = cur.fetchall()
    cur.close()
    print(incomplete_tests, complete_tests, treatments)
    return render_template('dataentry_main_dashboard.html', incomplete_tests=incomplete_tests, complete_tests=complete_tests, treatments=treatments, user=current_user)

@deo.route('/dataentry/test')
@deo.route('/dataentry/test/')
@login_required
@requires_access_level(4)
def dataentry_test():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Test_ID , TestDate,  Category , Name, BodyPart FROM Test JOIN Patient where Test.Patient_ID = Patient.Patient_ID and Test.ResultObtained = 0")
    tests = cur.fetchall()
    cur.close()
    return render_template('dataentry_select_test.html', user=current_user,tests = tests)

@deo.route('/dataentry/test/<test_id>', methods=['GET', 'POST'])
@deo.route('/dataentry/test/<test_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(4)
def dataentry_test_id(test_id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT TestDate,  Category , BodyPart , Name  FROM Test JOIN Patient where Test.Patient_ID = Patient.Patient_ID and Test.ResultObtained = 0 and Test.Test_ID = %s", (test_id,))
    test = cur.fetchone()
    cur.close()
    form = AddTestResult()
    if form.validate_on_submit():
        cur = mysql.connection.cursor()
        if(form.file_upload.data is not None):
            filename = secure_filename(form.file_upload.data.filename)
            print(filename)
            print("HELLO")
            patient_data_path = os.getcwd() + '/test_patient_data/' + test_id + '/'
            if not os.path.exists(patient_data_path):
                os.makedirs(patient_data_path)
            form.file_upload.data.save(patient_data_path + filename)
            print(patient_data_path + filename)
            cur.execute(f"UPDATE Test SET ResultObtained = 1 , Result = '{form.result.data}', Document_Path = '{patient_data_path + filename}'WHERE Test_ID = '{test_id}'")
        else:
            cur.execute(f"UPDATE Test SET ResultObtained = 1 , Result = '{form.result.data}'WHERE Test_ID = '{test_id}'")
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully added test result {test[1]} for patient {test[3]}', 'success')
        return redirect(url_for('deo.dataentry'))
    return render_template('dataentry_add_test.html', user=current_user, test=test, form=form)

@deo.route('/dataentry/treatment')
@deo.route('/dataentry/treatment/')
@login_required
@requires_access_level(4)
def dataentry_select_patient():
    cur = mysql.connection.cursor()
    cur.execute("SELECT Patient_ID,Name,Address,Age,Gender,Personal_Contact ,Emergency_Contact FROM Patient")
    patients = cur.fetchall()
    return render_template('dataentry_select_patient.html', user=current_user,patients = patients)

@deo.route('/dataentry/treatment/<patient_id>', methods=['GET', 'POST'])
@deo.route('/dataentry/treatment/<patient_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(4)
def dataentry_select_doctor(patient_id):
    cur = mysql.connection.cursor()
    
    cur.execute("SELECT Doctor_ID,Name,Username,Age,Gender,Personal_Contact FROM Doctor")
    doctors = cur.fetchall()
    cur.execute("SELECT Name FROM Patient WHERE Patient_ID = %s", (patient_id,))
    patient_name = cur.fetchone()
    form = AddTreatment()
    if form.validate_on_submit():
        if(form.file_upload.data is not None):
            filename = secure_filename(form.file_upload.data.filename)
            patient_data_path = os.getcwd() + '/treatment_patient_data/' + patient_id + '/'
            if not os.path.exists(patient_data_path):
                os.makedirs(patient_data_path)
            form.file_upload.data.save(patient_data_path + filename)
            cur.execute(f"INSERT INTO Treatment (Patient_ID, Doctor_ID, TreatmentDate, Category, Details, Document_Path) VALUES ('{patient_id}', '{form.doctor_id.data}', '{form.treatment_date.data}', '{form.category.data}', '{form.details.data}', '{patient_data_path + filename}')")
        else:
            cur.execute(f"INSERT INTO Treatment (Patient_ID, Doctor_ID, TreatmentDate, Category, Details) VALUES ('{patient_id}', '{form.doctor_id.data}', '{form.treatment_date.data}', '{form.category.data}', '{form.details.data}')")
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully added treatment {form.category.data} for patient {form.patient.data} by doctor {form.doctor.data}', 'success')
        return redirect(url_for('deo.dataentry'))
    return render_template('dataentry_select_doctor.html', user=current_user,doctors = doctors, patient_name = patient_name, form = form)

# @routes.route('/dataentry/treatment/<patient_id>/<doctor_id>', methods=['GET', 'POST'])
# @routes.route('/dataentry/treatment/<patient_id>/<doctor_id>/', methods=['GET', 'POST'])
# @login_required
# @requires_access_level(4)
# def dataentry_treatment(patient_id, doctor_id):
#     cur = mysql.connection.cursor()
#     cur.execute("SELECT Name FROM Patient where Patient_ID = %s", (patient_id,))
#     patient = cur.fetchone()
#     cur.execute("SELECT Name FROM Doctor where Doctor_ID = %s", (doctor_id,))
#     doctor = cur.fetchone()
#     patient = patient[0]
#     doctor = doctor[0]
#     print(patient)
#     print(doctor)
#     cur.close()
#     form = AddTreatment()
#     if form.validate_on_submit():
#         print("Form validated")
#         cur = mysql.connection.cursor()
#         if(form.file_upload.data is not None):
#             filename = secure_filename(form.file_upload.data.filename)
#             patient_data_path = os.getcwd() + '/patient_data/' + patient_id + '/'
#             if not os.path.exists(patient_data_path):
#                 os.makedirs(patient_data_path)
#             form.file_upload.data.save(patient_data_path + filename)
#             cur.execute(f"INSERT INTO Treatment (Patient_ID, Doctor_ID, TreatmentDate, Category, Details, Document_Path) VALUES ('{patient_id}', '{doctor_id}', '{form.treatment_date.data}', '{form.category.data}', '{form.details.data}', '{patient_data_path + filename}')")
#         else:
#             cur.execute(f"INSERT INTO Treatment (Patient_ID, Doctor_ID, TreatmentDate, Category, Details) VALUES ('{patient_id}', '{doctor_id}', '{form.treatment_date.data}', '{form.category.data}', '{form.details.data}')")
#         mysql.connection.commit()
#         cur.close()
#         flash(f'Successfully added treatment {form.category.data} for patient {patient} by doctor {doctor}', 'success')
#         return redirect(url_for('routes.dataentry'))
#     return render_template('dataentry_add_treatment.html', user=current_user, patient=patient, doctor=doctor, form=form)