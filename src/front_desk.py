from flask import render_template, Blueprint, flash, redirect, url_for, request
from flask_login import login_required, current_user
from . import requires_access_level, mysql
from werkzeug.security import generate_password_hash
from werkzeug.utils import secure_filename
from .forms import *
from .models import DE_Operator,Doctor,FD_Operator,Administrator, identify_class
from datetime import datetime, timedelta

fdo = Blueprint('fdo', __name__)

@fdo.route('/frontdesk')
@fdo.route('/frontdesk/')
@login_required
@requires_access_level(3)
def frontdesk():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient ORDER BY Patient_ID DESC LIMIT 5")
    patients = cur.fetchall()
    cur.execute("SELECT * FROM Patient")
    total_patients = len(cur.fetchall())
    cur.execute("SELECT * FROM Admitted")
    admitted = cur.fetchall()
    # get free rooms
    cur.execute("SELECT * FROM Discharged")
    discharged = cur.fetchall()
    cur.execute("SELECT * FROM Room WHERE (Room_Num, Floor) NOT IN (SELECT Room_Num, Floor FROM Admitted)")
    free_rooms = cur.fetchall()
    return render_template('frontdesk_dashboard.html', total_patients=total_patients, admitted_patients=len(admitted), available_rooms = len(free_rooms), patients = patients, admitted_patients_list=admitted, discharged_patients_list = discharged, user = current_user)  

@fdo.route('/frontdesk/register', methods=['GET', 'POST'])
@fdo.route('/frontdesk/register/', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def frontdesk_register():
    # if(request.method == 'POST'):
    #     print(request.form)
    #     return render_template('frontdesk_register.html')
    # else:
    #     return render_template('frontdesk_register.html')

    form = RegisterPatient()
    if form.validate_on_submit():
        print("Form validated")
        print(form.name.data)
        print(form.address.data)
        print(form.age.data)
        print(form.gender.data)
        print(form.contact_number.data)
        print(form.emergency_contact.data)
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO Patient (Name, Address, Age, Gender, Personal_Contact, Emergency_Contact) VALUES (%s, %s, %s, %s, %s, %s)", (form.name.data, form.address.data, form.age.data, form.gender.data, form.contact_number.data, form.emergency_contact.data))
        mysql.connection.commit()
        cur.close()
        flash(f'Successfully registered patient {form.name.data}', 'success')
        return redirect(url_for('fdo.frontdesk_register'))
    return render_template('frontdesk_register.html', form=form,  user=current_user)

@fdo.route('/frontdesk/admit')
@fdo.route('/frontdesk/admit/')
@login_required
@requires_access_level(3)
def frontdesk_admit():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient WHERE Patient_ID NOT IN (SELECT Patient_ID FROM Admitted)")
    patients = cur.fetchall()
    cur.close()
    print(patients)
    return render_template('frontdesk_admit.html', patients=patients,  user=current_user)

@fdo.route('/frontdesk/admit/<patient_id>',methods = ['GET','POST'])
@fdo.route('/frontdesk/admit/<patient_id>/',methods = ['GET','POST'])
@login_required
@requires_access_level(3)
def frontdesk_admit_patient(patient_id):
    print(patient_id)
    cur = mysql.connection.cursor()
    date = datetime.now().strftime("%Y-%m-%d")
    cur.execute("SELECT Room_Num, Floor FROM Room WHERE (Room_Num, Floor) NOT IN (SELECT Room_Num, Floor FROM Admitted)")
    room = cur.fetchone()
    if room is None:
        flash(f'No rooms available', 'danger')
        return redirect(url_for('fdo.frontdesk_admit'))
    flash(f'Patient admitted to room {room[0]} on floor {room[1]}', 'success')
    cur.execute("INSERT INTO Admitted (Patient_ID, Room_Num, Floor, Date_Admitted) VALUES (%s, %s, %s, %s)", (patient_id, room[0], room[1], date))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('fdo.frontdesk_admit'))

@fdo.route('/frontdesk/discharge')
@fdo.route('/frontdesk/discharge/')
@login_required
@requires_access_level(3)
def frontdesk_discharge():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient WHERE Patient_ID IN (SELECT Patient_ID FROM Admitted)")
    patients = cur.fetchall()
    cur.close()
    # print(patients)
    return render_template('frontdesk_discharge.html', patients=patients,  user=current_user)

@fdo.route('/frontdesk/discharge/<patient_id>')
@fdo.route('/frontdesk/discharge/<patient_id>/')
@login_required
@requires_access_level(3)
def frontdesk_discharge_patient(patient_id):
    # print(patient_id)
    date = datetime.now().strftime("%Y-%m-%d")
    cur = mysql.connection.cursor()
    cur.execute(f"SELECT Room_Num, Floor FROM Admitted WHERE Patient_ID = {patient_id}")
    room = cur.fetchone()
    cur.execute(f"DELETE FROM Admitted WHERE Patient_ID = {patient_id}")
    mysql.connection.commit()
    cur.execute("INSERT INTO Discharged (Patient_ID, Room_Num, Floor, Date_Discharged) VALUES (%s, %s, %s, %s)", (patient_id, room[0], room[1], date))
    mysql.connection.commit()
    cur.close()
    flash(f'Patient discharged', 'success')
    return redirect(url_for('fdo.frontdesk_discharge'))

@fdo.route('/frontdesk/appointment_schedule')
@fdo.route('/frontdesk/appointment_schedule/')
@login_required
@requires_access_level(3)
def frontdesk_appointment_schedule():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM Patient WHERE Patient_ID NOT IN (SELECT Patient_ID FROM Admitted)")
    patients = cur.fetchall()
    cur.close()
    print(patients)
    return render_template('frontdesk_appointment_schedule.html', patients=patients,  user = current_user)

@fdo.route('/frontdesk/appointment_schedule/<patient_id>', methods=['GET', 'POST'])
@fdo.route('/frontdesk/appointment_schedule/<patient_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def frontdesk_appointment_schedule_patient(patient_id):
    if request.method == 'POST':
        is_urgent = request.form.get('priority')
        if(is_urgent == 'Urgent'):
            date_to_schedule = (datetime.now()+timedelta(days=1)).strftime("%Y-%m-%d")
            cur = mysql.connection.cursor()
            # start = '10:00:00'
            # end = '16:00:00'
            # for i in range(0, 6):
            #     start[1] = str(i)
            #     cur.execute("SELECT Doctor_ID")
            # min_time = '16:00:00'
            # cur.execute("SELECT Doctor_ID, MIN(Appointment_Time) FROM Appointment WHERE Appointment_Date = %s GROUP BY Doctor_ID", (date_to_schedule,))
            # min_time_doctor = cur.fetchall()
            # doctors_with_appointments = []
            # for doctor in min_time_doctor:
            #     doctors_with_appointments.append(doctor[0])
            # cur.execute("SELECT * FROM Doctor WHERE Doctor_ID NOT IN (%s)", (doctors_with_appointments,))
            # free_doctors = cur.fetchall()
            # if(len(free_doctors) != 0):
            #     doctor_id = free_doctors[0][0]
            #     cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doctor_id, date_to_schedule, '10:00:00'))
            # else:
            #     for 
            doctors_free = []
            cur.execute("SELECT Doctor_ID, Name FROM Doctor WHERE Doctor_ID NOT IN (SELECT Doctor_ID FROM Appointment WHERE Appointment_Date = %s)", (date_to_schedule,))
            doctors_free = cur.fetchall()
            if(len(doctors_free) != 0):
                doctors_id = doctors_free[0][0]
                cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doctors_id, date_to_schedule, '10:00:00'))
                mysql.connection.commit()
                flash(f'Appointment scheduled for patient {patient_id} at 10:00:00 on date {date_to_schedule} with doctor {doctors_free[0][1]}', 'success')
                return redirect(url_for('fdo.frontdesk_appointment_schedule'))
            
            else:
                start = '10:00:00'
                cur.execute("SELECT Doctor_ID, Name FROM Doctor")
                doctors = cur.fetchall()

                for i in range(0, 6):
                    start = start[0]+str(i)+start[2:]
                    for doc in doctors:
                        cur.execute("SELECT * FROM Appointment WHERE Doctor_ID = %s AND Appointment_Date = %s AND Appointment_Time = %s", (doc[0], date_to_schedule, start))
                        if(cur.fetchone() is None):
                            cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doc[0], date_to_schedule, start))
                            mysql.connection.commit()
                            flash(f'Appointment scheduled for patient {patient_id} at {start} on date {date_to_schedule} with doctor {doc[1]}', 'success')
                            return redirect(url_for('fdo.frontdesk_appointment_schedule'))
                        
                flash(f'No doctors available on urgent priority', 'danger')
                return redirect(url_for('fdo.frontdesk_appointment_schedule'))
            
            # flash(f'Appointment scheduled for patient {patient_id}', 'success')
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM Doctor")
            doctors = cur.fetchall()
            cur.close()
            return render_template('frontdesk_appointment_schedule_patient.html', patient_id=patient_id, doctors=doctors,  user = current_user)
    

@fdo.route('/frontdesk/appointment_schedule/<patient_id>/<doctor_id>', methods=['GET', 'POST'])
@fdo.route('/frontdesk/appointment_schedule/<patient_id>/<doctor_id>/', methods=['GET', 'POST'])
@login_required
@requires_access_level(3)
def frontdesk_appointment_schedule_date(patient_id, doctor_id):
    if request.method == 'POST':
        cur = mysql.connection.cursor()
        date_selected = request.form.get('date')
        cur_date = datetime.now().strftime("%Y-%m-%d")
        if date_selected <= cur_date:
            flash(f'Please select a date in the future', 'danger')
            # return redirect(url_for('fdo.frontdesk_appointment_schedule_patient', patient_id=patient_id, doctors = doctors))
            return redirect(url_for('fdo.frontdesk_appointment_schedule'))
            # return redirect(url_for('fdo.frontdesk_appointment_schedule_date', patient_id=patient_id, doctor_id=doctor_id))
        cur.execute("SELECT Appointment_Time FROM Appointment WHERE Appointment_Date = %s AND Doctor_ID = %s", (date_selected, doctor_id))
        appointments = cur.fetchall()
        # print(appointments)
        print("\n\n\nAPPOINTMENTS\n\n\n", appointments)
        if(len(appointments) == 0):
            time_scheduled = '10:00:00'
            flash(f'Appointment scheduled for {date_selected} at {time_scheduled}', 'success')
            cur = mysql.connection.cursor()
            cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doctor_id, date_selected, time_scheduled))
            mysql.connection.commit()
        else:
            sorted_appointments = sorted(appointments)
            last_appointment_time = sorted_appointments[-1][0]
            print("TYPE LAST APP", type(last_appointment_time))
            last_appointment_time = str(last_appointment_time)
            # print("STR TIME",str_time)
            # print("\n\n\nLAST APPOINTMENT TIME\n\n\n", last_appointment_time)
            # print((last_appointment_time[0]))
            # last_appointment_time = datetime.strftime(last_appointment_time, '%H:%M:%S')
            # print(last_appointment_time)
            # check if last appointment is before 4pm
            # if(last_appointment_time.hour < 16):
            #     next_appointment_time = last_appointment_time + timedelta(minutes=60)
            #     flash(f'Appointment scheduled for {date_selected} at {next_appointment_time}', 'success')
            #     cur = mysql.connection.cursor()
            #     cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doctor_id, date_selected, next_appointment_time))
            #     mysql.connection.commit()
            # else:
            #     flash(f'No appointments available on {date_selected}', 'danger')
            if last_appointment_time < '16:00:00':
                next_appointment_time = datetime.strptime(last_appointment_time, '%H:%M:%S') + timedelta(minutes=60)
                next_appointment_time = datetime.strftime(next_appointment_time, '%H:%M:%S')
                flash(f'Appointment scheduled for {date_selected} at {next_appointment_time}', 'success')
                cur = mysql.connection.cursor()
                cur.execute("INSERT INTO Appointment (Patient_ID, Doctor_ID, Appointment_Date, Appointment_Time) VALUES (%s, %s, %s, %s)", (patient_id, doctor_id, date_selected, next_appointment_time))
                mysql.connection.commit()
            else:
                flash(f'No appointments available on {date_selected}', 'danger')
        cur.close()
        return redirect(url_for('fdo.frontdesk_appointment_schedule'))
    else:
        return render_template('frontdesk_appointment_schedule_date.html', patient_id=patient_id, doctor_id=doctor_id,  user = current_user)