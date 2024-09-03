from flask import Flask, sessions, flash
from flask_mysqldb import MySQL
from flask_login import LoginManager
from flask import session, redirect, url_for
from functools import wraps
import os
from dotenv import load_dotenv 
from flask_mail import Mail, Message
from flask_apscheduler import APScheduler
import pdfkit

load_dotenv()
mysql = MySQL()
scheduler = APScheduler()

def reverse_tuple(t):
    new_tuple = ()
    for i in range(len(t)-1, -1, -1):
        new_tuple += (t[i],)
    return new_tuple

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'

    from .auth import auth
    from .admin import adm
    from .doctor import doctor
    from .front_desk import fdo
    from .data_entry import deo

    app.register_blueprint(adm, url_prefix='/')
    app.register_blueprint(auth, url_prefix='/')
    app.register_blueprint(doctor, url_prefix='/')
    app.register_blueprint(fdo, url_prefix='/')
    app.register_blueprint(deo, url_prefix='/')

    # init MYSQL
    # app.config['MYSQL_HOST'] = 'localhost'
    app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
    app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
    app.config["MAIL_SERVER"]='smtp.gmail.com'  
    app.config["MAIL_PORT"] = 465  
    app.config["MAIL_USERNAME"] = 'HMS.iitkgp@gmail.com'  
    # app.config['MAIL_PASSWORD'] = 'tulcolduqjiwwpcn' #app password, different for every system (HMSiitkgp23)
    app.config['MAIL_PASSWORD'] = 'tmctkhmtwagcfrxv' #app password, different for every system (HMSiitkgp23)

    app.config['MAIL_USE_TLS'] = False  
    app.config['MAIL_USE_SSL'] = True  
    app.config['MYSQL_DB'] = 'hospital_db'
    app.config['SCHEDULER_API_ENABLED'] = True

    mail = Mail(app)
    mysql.init_app(app)
    mail.init_app(app)

    from .models import Administrator, Doctor, DE_Operator, FD_Operator

    @scheduler.task('cron', id='send_weekly_mail', day_of_week='mon', hour=14, minute=50, second=0)
    def send_mail():
        print("Sending mail")
        with app.app_context():
            cur = mysql.connection.cursor()
            cur.execute(
                "SELECT Doctor_ID, Username FROM Doctor"
            )
            doctor_ids = cur.fetchall()
            doctor_ids = reverse_tuple(doctor_ids)
            for doctor_id in doctor_ids:
                cur.execute(
                    "SELECT distinct Patient_ID FROM Treatment WHERE Doctor_ID = %s", (doctor_id[0],)
                )
                patient_ids = cur.fetchall()
                subject = f"Health Report for Patient"
                body = f"Dear Doctor,\n\nPlease find the attached health report for Patient.\n\nRegards,\nHMS Team"
                msg = Message(subject = subject, body = body, sender = app.config['MAIL_USERNAME'], recipients = [doctor_id[1]])
                # msg = Message(subject = subject, body = body, sender = app.config['MAIL_USERNAME'], recipients = ['jating1120@gmail.com'])
                for patient_id in patient_ids:
                    print("patient_id = ", patient_id[0])
                    route_url = "http://127.0.0.1:5000/report/doctor/"+str(patient_id[0])
                    path = os.getcwd()
                    path = path + "/public/out.pdf"
                    pdfkit.from_url(route_url, path)
                    with app.open_resource(path) as fp:
                        # msg.attach("health_report.pdf", "application/pdf", fp.read())
                        file_name = "health_report_" + str(patient_id[0]) + ".pdf"
                        msg.attach(file_name,"application/pdf",fp.read())
                mail.send(msg)
                print("Mail sent to doc: ", doctor_id[1])
    
    scheduler.init_app(app)
    scheduler.start()
    
    login_manager = LoginManager()
    login_manager.login_view = 'auth.login'
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        id = str(id)
        type = id[0]
        id = int(id[1:])
        if type == '1':
            return Administrator.get(id)
        elif type == '2':
            return Doctor.get(id)
        elif type == '3':
            return FD_Operator.get(id)
        elif type == '4':
            return DE_Operator.get(id)
        else:
            return None
    return app

def requires_access_level(access_level):
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if session['Access_Level'] != access_level:
                flash('You do not have access to that page. Sorry!', category='danger')
                return redirect(url_for('auth.login'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator


