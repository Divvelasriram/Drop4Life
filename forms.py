from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, TextAreaField, IntegerField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError
from models import User

class RegistrationForm(FlaskForm):
    role = SelectField('Register As', choices=[('donor', 'Donor'), ('hospital', 'Hospital/Blood Bank')], validators=[DataRequired()])
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    
    # Common fields (some might be hidden depending on role via JS)
    phone = StringField('Phone Number', validators=[DataRequired(), Length(min=10, max=20)])
    address = TextAreaField('Address', validators=[DataRequired()])
    
    # Donor specific
    full_name = StringField('Full Name (Donors)')
    blood_group = SelectField('Blood Group', choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')])
    
    # Hospital specific
    hospital_name = StringField('Hospital/Blood Bank Name')
    license_number = StringField('License Number')
    contact_person = StringField('Contact Person Name')

    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')

    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class InventoryForm(FlaskForm):
    blood_group = SelectField('Blood Group', choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], validators=[DataRequired()])
    units = IntegerField('Units Available', validators=[DataRequired()])
    submit = SubmitField('Update Inventory')

class RequestForm(FlaskForm):
    blood_group = SelectField('Blood Group Needed', choices=[('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'), ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')], validators=[DataRequired()])
    units_required = IntegerField('Units Required', validators=[DataRequired()])
    urgency = SelectField('Urgency', choices=[('normal', 'Normal'), ('urgent', 'Urgent'), ('emergency', 'Emergency')], validators=[DataRequired()])
    submit = SubmitField('Post Request')
