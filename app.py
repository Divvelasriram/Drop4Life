from flask import Flask, render_template, redirect, url_for, flash, request
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime
from flask_bcrypt import Bcrypt
from models import db, User, DonorProfile, HospitalProfile, BloodInventory, BloodRequest, DonationHistory
from config import Config
from utils import send_emergency_alert
import os

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route("/")
def home():
    return render_template('index.html')

from forms import RegistrationForm, LoginForm

@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=True)
            flash('Login Successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login Unsuccessful. Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password, role=form.role.data)
        db.session.add(user)
        db.session.commit()
        
        # Create respective profiles based on role
        if form.role.data == 'donor':
            donor_profile = DonorProfile(user_id=user.id, full_name=form.full_name.data, blood_group=form.blood_group.data, phone=form.phone.data, address=form.address.data)
            db.session.add(donor_profile)
        elif form.role.data == 'hospital':
            hospital_profile = HospitalProfile(user_id=user.id, hospital_name=form.hospital_name.data, license_number=form.license_number.data, contact_person=form.contact_person.data, phone=form.phone.data, address=form.address.data)
            db.session.add(hospital_profile)
        
        db.session.commit()
        flash('Account created successfully! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

from forms import RegistrationForm, LoginForm, InventoryForm, RequestForm

@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'donor':
        profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
        history = DonationHistory.query.filter_by(donor_id=profile.id).all()
        return render_template('donor_dashboard.html', profile=profile, history=history)
    elif current_user.role == 'hospital':
        profile = HospitalProfile.query.filter_by(user_id=current_user.id).first()
        inventory_form = InventoryForm()
        request_form = RequestForm()
        
        if request.method == 'POST':
            if 'update_inventory' in request.form and inventory_form.validate_on_submit():
                # Check if blood group exists in inventory
                inv = BloodInventory.query.filter_by(hospital_id=profile.id, blood_group=inventory_form.blood_group.data).first()
                if inv:
                    inv.units_available = inventory_form.units.data
                    inv.last_updated = datetime.utcnow()
                else:
                    new_inv = BloodInventory(hospital_id=profile.id, blood_group=inventory_form.blood_group.data, units_available=inventory_form.units.data)
                    db.session.add(new_inv)
                db.session.commit()
                flash('Inventory Updated Successfully', 'success')
                return redirect(url_for('dashboard'))
                
            elif 'post_request' in request.form and request_form.validate_on_submit():
                new_req = BloodRequest(hospital_id=profile.id, blood_group=request_form.blood_group.data, units_required=request_form.units_required.data, urgency=request_form.urgency.data)
                db.session.add(new_req)
                db.session.commit()
                
                # Trigger Notification if Emergency
                if new_req.urgency == 'emergency':
                    send_emergency_alert(new_req.blood_group, profile.hospital_name, profile.address)

                flash('Blood Request Posted Successfully', 'success')
                return redirect(url_for('dashboard'))

        inventory = BloodInventory.query.filter_by(hospital_id=profile.id).all()
        requests = BloodRequest.query.filter_by(hospital_id=profile.id).order_by(BloodRequest.request_date.desc()).all()
        return render_template('hospital_dashboard.html', profile=profile, inventory_form=inventory_form, request_form=request_form, inventory=inventory, requests=requests)
    
    return redirect(url_for('home'))

@app.route("/find_blood")
def find_blood():
    return render_template('find_blood.html', title='Find Blood')

@app.route("/education")
def education():
    return render_template('education.html', title='Learn & FAQs')

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
