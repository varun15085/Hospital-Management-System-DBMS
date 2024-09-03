from flask import *  
from flask_mail import *  
import os
from dotenv import load_dotenv
from flask_mysqldb import MySQL
import pdfkit
load_dotenv()
mysql = MySQL()
app = Flask(__name__)  
  
app.config["MAIL_SERVER"]='smtp.gmail.com'  
app.config["MAIL_PORT"] = 465  
app.config["MAIL_USERNAME"] = 'HMS.iitkgp@gmail.com'  
# app.config['MAIL_PASSWORD'] = 'HMSiitkgp23'  
app.config['MAIL_PASSWORD'] = 'tulcolduqjiwwpcn'
app.config['MAIL_USE_TLS'] = False  
app.config['MAIL_USE_SSL'] = True  
app.config['MYSQL_USER'] = os.getenv('MYSQL_USER')
app.config['MYSQL_PASSWORD'] = os.getenv('MYSQL_PASSWORD')
app.config['MYSQL_DB'] = 'hospital_db'

mail = Mail(app)  
mysql.init_app(app)
 

@app.route("/send/<patieidnt_id>/<doctor_id>/<file>", methods = ["GET"])
def index(patient_id,doctor_id,file):
    extension = file[-3:]
    file = f"./public/{file}"
    cur = mysql.connection.cursor()
    cur.execute("SELECT Username,Name FROM Doctor WHERE Doctor_ID = %s", (doctor_id,))
    doctor = cur.fetchone()
    cur.execute("SELECT Name,Age,Gender FROM Patient WHERE Patient_ID = %s", (patient_id,))
    patient = cur.fetchone()
    cur.close()
    subject = f"Health Report for {patient[0]}"
    body = f"Dear {doctor[1]},\n\nPlease find the attached health report for {patient[0]}.\n\nRegards,\nHMS Team"
    msg = Message(subject = subject, body = body, sender = app.config['MAIL_USERNAME'], recipients = ['kushaz.sehgal@gmail.com'])
    if extension == 'pdf':
        content_type = 'application/pdf'
    elif extension == 'png':
        content_type = 'image/png'    
    elif extension == 'txt':
        content_type = 'text/plain'
    with app.open_resource(file) as fp:  
        msg.attach(f"{patient[0]}_report.{extension}",content_type,fp.read())  
        # msg.attach(f"{patient[0]}_report2.{extension}",content_type,fp.read()) 
    with app.open_resource('./public/A2.pdf') as fp:  
        msg.attach(f"{patient[0]}_report2.pdf",'application/pdf',fp.read())          
    mail.send(msg)  
    return "sent"  
  
@app.route("/home")
def home():
    return render_template("timepass.html")
@app.route("/send_page")
def send_html():

    pdfkit.from_url('http://127.0.0.1:5000/home', '../public/out.pdf')
    subject = f"Health Report for Patient"
    body = f"Dear Doctor,\n\nPlease find the attached health report for Patient.\n\nRegards,\nHMS Team"
    msg = Message(subject = subject, body = body, sender = app.config['MAIL_USERNAME'], recipients = ['kushaz.sehgal@gmail.com'])
    with app.open_resource('../public/out.pdf') as fp:  
        msg.attach("health_report.pdf",'application/pdf',fp.read()) 
    mail.send(msg)
    return ("HTML page converted to pdf and sent!")
if __name__ == "__main__":  
    app.run(debug = True)  