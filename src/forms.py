from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, IntegerField, SelectField, DateField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, NumberRange, Email
from wtforms.fields import DateField
import datetime

class RegisterPatient(FlaskForm):
    gender_choices = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = SelectField("Gender", choices = gender_choices, validators = [DataRequired()])
    name = StringField("Patient Name", validators=[DataRequired(), Length(min=2, max=50)])
    address = StringField("Patient Address", validators=[DataRequired(), Length(min=2, max=50)])
    age = IntegerField("Patient Age", validators=[DataRequired(), NumberRange(min=1, max=120)])
    contact_number = StringField("Patient Contact Number", validators=[DataRequired(), Length(min=10, max=10)])
    emergency_contact = StringField("Patient Emergency Contact", validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField("Register Patient")

class AddUser(FlaskForm):
    gender_choices = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]
    gender = SelectField("Gender", choices = gender_choices, validators = [DataRequired()])
    username = StringField("Username", validators=[DataRequired(), Length(min=2, max=50), Email(message="Please enter a valid email address!")])
    password1 = PasswordField("Password", validators=[DataRequired(), Length(min=7, max=20)])
    # password2 = PasswordField("Confirm Password", validators=[DataRequired(), EqualTo('password1')])
    name = StringField("Name", validators=[DataRequired(), Length(min=2, max=30)])
    address = StringField("Address", validators=[DataRequired(), Length(min=2, max=50)])
    age = IntegerField("Age", validators=[DataRequired(), NumberRange(min=1, max=120)])
    contact_number = StringField("Contact Number", validators=[DataRequired(), Length(min=10, max=10)])
    submit = SubmitField("Add User")

class GetUser(FlaskForm):
    choices = [('Doctor', 'Doctor'), ('FD_Operator', 'FrontDesk Operator'), ('DE_Operator', 'DataEntry Operator'), ('Administrator', 'Administrator')]
    users = SelectField(u'Field name', choices = choices, validators = [DataRequired()])
    submit = SubmitField("Select User")

class AddRoom(FlaskForm):
    num = IntegerField("Room Number", validators=[DataRequired(), NumberRange(min=1)])
    floor = IntegerField("Floor Number", validators=[DataRequired(), NumberRange(min=1)])
    submit = SubmitField("Create Room")

class AddTestResult(FlaskForm):
    choices = [('CT Scan', 'CT Scan'), ('PET Scan', 'PET Scan'), ('Biopsy', 'Biopsy') , ('Ultrasound', 'Ultrasound')]
    test_date = DateField("Test Date",default=datetime.date.today(),format='%Y-%m-%d',validators=[DataRequired(message="You need to enter the end date.")])
    # test_date = StringField("Test Date",validators=[DataRequired(message="You need to enter the end date.")],render_kw={"placeholder": "YYYY-MM-DD"})
    category = StringField("Category", validators=[DataRequired(), Length(min=2, max=1000)])
    bodypart = StringField("Associated Body Part", validators=[DataRequired(), Length(min=2, max=1000)])
    patient = StringField("Patient Name", validators=[DataRequired(), Length(min=2, max=1000)])
    result = StringField("Test Result", validators=[DataRequired(), Length(min=2, max=1000)])
    file_upload = FileField("Upload File(Optional)", validators=[FileAllowed(['jpg', 'png', 'pdf'], 'Images only!')])
    submit = SubmitField("Add Test")

class AddTreatment(FlaskForm):
    choices = [('Physiotherapy', 'Physiotherapy'), ('Operation', 'Operation'),('General', 'General')]
    # treatment_date = StringField("Treatment Date", format='YYYY-MM-DD',validators=[DataRequired(message="You need to enter the end date.")],render_kw={"placeholder": "YYYY-MM-DD"})
    treatment_date = DateField("Treatment Date",default=datetime.date.today(),format='%Y-%m-%d',validators=[DataRequired(message="You need to enter the end date.")])
    category = SelectField(u'Field name', choices = choices, validators = [DataRequired()])    
    details = StringField("Details", validators=[DataRequired(), Length(min=2, max=1000)])
    patient = StringField("Patient Name", validators=[DataRequired(), Length(min=2, max=1000)])
    doctor = StringField("Doctor Name", validators=[DataRequired(), Length(min=2, max=1000)])
    doctor_id = IntegerField("Doctor ID", validators=[DataRequired()])
    file_upload = FileField("Upload File(Optional)", validators=[FileAllowed(['jpg', 'png', 'pdf'], 'Images only!')])
    submit = SubmitField("Add Treatment")

class AddTreatmentForm(FlaskForm):
    choices = [('Physiotherapy', 'Physiotherapy'), ('Operation', 'Operation'), ('General', 'General'), ]
    treatment_date = DateField("Treatment Date",default=datetime.date.today(),format='%Y-%m-%d',validators=[DataRequired(message="You need to enter the date.")])
    category = SelectField(u'Field name', choices = choices, validators = [DataRequired()])    
    details = StringField("Details", validators=[DataRequired(), Length(min=2, max=1000)])
    patient_id = IntegerField("Patient ID", validators=[DataRequired()])
    submit = SubmitField("Add Treatment")

class AddTestForm(FlaskForm):
    choices = [('CT Scan', 'CT Scan'), ('PET Scan', 'PET Scan'), ('Biopsy', 'Biopsy') , ('Ultrasound', 'Ultrasound')]
    test_date = DateField("Test Date",default=datetime.date.today(),format='%Y-%m-%d',validators=[DataRequired(message="You need to enter the date.")])
    category = SelectField(u'Field name', choices = choices, validators = [DataRequired()])    
    bodypart = StringField("Associated Body Part", validators=[DataRequired(), Length(min=2, max=1000)])
    patient_id = IntegerField("Patient ID", validators=[DataRequired()])
    submit = SubmitField("Add Test")

class AddPrescriptionForm(FlaskForm):
    prescription_date = DateField("Prescription Date",default=datetime.date.today(),format='%Y-%m-%d',validators=[DataRequired(message="You need to enter the date.")])
    medicine = StringField("Medicine", validators=[DataRequired(), Length(min=2, max=1000)])
    treatment_id = IntegerField("Treatment ID", validators=[DataRequired()])
    submit = SubmitField("Add Prescription")
