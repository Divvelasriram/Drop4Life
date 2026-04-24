from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_login import LoginManager, current_user, login_user, logout_user, login_required
from datetime import datetime, timedelta
from functools import wraps
from flask_bcrypt import Bcrypt
from models import db, User, DonorProfile, HospitalProfile, BloodInventory, BloodRequest, DonationHistory
from forms import RegistrationForm, LoginForm, InventoryForm, RequestForm, DonorProfileForm, RecordDonationForm
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

POINTS_PER_DONATION = 50
DONATION_COOLDOWN_DAYS = 90
CERTIFICATE_TIERS = [
    {'name': 'Bronze Donor', 'min_points': 100, 'color': '#CD7F32'},
    {'name': 'Silver Donor', 'min_points': 300, 'color': '#C0C0C0'},
    {'name': 'Gold Donor', 'min_points': 500, 'color': '#FFD700'},
    {'name': 'Platinum Donor', 'min_points': 1000, 'color': '#E5E4E2'},
]

def seed_admin():
    admin = User.query.filter_by(role='admin').first()
    if not admin:
        hashed_pw = bcrypt.generate_password_hash('admin123').decode('utf-8')
        admin = User(username='admin', email='admin@drop4life.com', password=hashed_pw, role='admin')
        db.session.add(admin)
        db.session.commit()

with app.app_context():
    db.create_all()
    seed_admin()


def admin_required(f):
    @wraps(f)
    @login_required
    def decorated(*args, **kwargs):
        if current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@app.route("/")
def home():
    return render_template('index.html')


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
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
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
@login_required
def logout():
    logout_user()
    return redirect(url_for('home'))


# --------------- Donor Dashboard ---------------

def get_donor_certificate_tier(points):
    tier = None
    for t in CERTIFICATE_TIERS:
        if points >= t['min_points']:
            tier = t
    return tier

def get_next_eligible_date(last_donation_date):
    if not last_donation_date:
        return None
    return last_donation_date + timedelta(days=DONATION_COOLDOWN_DAYS)


@app.route("/dashboard", methods=['GET', 'POST'])
@login_required
def dashboard():
    if current_user.role == 'admin':
        return redirect(url_for('admin_dashboard'))

    if current_user.role == 'donor':
        profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
        history = DonationHistory.query.filter_by(donor_id=profile.id).order_by(DonationHistory.donation_date.desc()).all()
        tier = get_donor_certificate_tier(profile.points)
        next_eligible = get_next_eligible_date(profile.last_donation_date)
        is_eligible = next_eligible is None or datetime.utcnow() >= next_eligible
        return render_template('donor_dashboard.html', profile=profile, history=history,
                               tier=tier, next_eligible=next_eligible, is_eligible=is_eligible)

    elif current_user.role == 'hospital':
        profile = HospitalProfile.query.filter_by(user_id=current_user.id).first()
        inventory_form = InventoryForm()
        request_form = RequestForm()
        donation_form = RecordDonationForm()

        if request.method == 'POST':
            if 'update_inventory' in request.form and inventory_form.validate_on_submit():
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

                if new_req.urgency == 'emergency':
                    send_emergency_alert(new_req.blood_group, profile.hospital_name, profile.address)

                flash('Blood Request Posted Successfully', 'success')
                return redirect(url_for('dashboard'))

            elif 'record_donation' in request.form and donation_form.validate_on_submit():
                donor_user = User.query.filter_by(email=donation_form.donor_email.data, role='donor').first()
                if not donor_user:
                    flash('No donor found with that email address.', 'danger')
                    return redirect(url_for('dashboard'))

                donor_profile = DonorProfile.query.filter_by(user_id=donor_user.id).first()
                record = DonationHistory(
                    donor_id=donor_profile.id,
                    hospital_id=profile.id,
                    units_donated=donation_form.units_donated.data,
                    points_awarded=POINTS_PER_DONATION
                )
                db.session.add(record)

                donor_profile.points += POINTS_PER_DONATION
                donor_profile.last_donation_date = datetime.utcnow()
                db.session.commit()
                flash(f'Donation recorded! {POINTS_PER_DONATION} points awarded to {donor_profile.full_name}.', 'success')
                return redirect(url_for('dashboard'))

        inventory = BloodInventory.query.filter_by(hospital_id=profile.id).all()
        requests_list = BloodRequest.query.filter_by(hospital_id=profile.id).order_by(BloodRequest.request_date.desc()).all()
        return render_template('hospital_dashboard.html', profile=profile, inventory_form=inventory_form,
                               request_form=request_form, donation_form=donation_form,
                               inventory=inventory, requests=requests_list)

    return redirect(url_for('home'))


# --------------- Edit Donor Profile ---------------

@app.route("/edit_profile", methods=['GET', 'POST'])
@login_required
def edit_profile():
    if current_user.role != 'donor':
        abort(403)
    profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
    form = DonorProfileForm(obj=profile)

    if form.validate_on_submit():
        profile.full_name = form.full_name.data
        profile.blood_group = form.blood_group.data
        profile.phone = form.phone.data
        profile.address = form.address.data
        profile.date_of_birth = form.date_of_birth.data
        profile.weight_kg = form.weight_kg.data
        profile.medical_conditions = form.medical_conditions.data
        profile.allergies = form.allergies.data
        profile.emergency_contact = form.emergency_contact.data
        db.session.commit()
        flash('Profile updated successfully!', 'success')
        return redirect(url_for('dashboard'))

    return render_template('edit_profile.html', title='Edit Profile', form=form, profile=profile)


# --------------- Certificate ---------------

@app.route("/certificate")
@login_required
def certificate():
    if current_user.role != 'donor':
        abort(403)
    profile = DonorProfile.query.filter_by(user_id=current_user.id).first()
    tier = get_donor_certificate_tier(profile.points)
    if not tier:
        flash('You need at least 100 points to earn a certificate. Keep donating!', 'info')
        return redirect(url_for('dashboard'))
    total_donations = DonationHistory.query.filter_by(donor_id=profile.id).count()
    return render_template('certificate.html', profile=profile, tier=tier,
                           total_donations=total_donations, date=datetime.utcnow())


# --------------- Admin Dashboard ---------------

@app.route("/admin")
@admin_required
def admin_dashboard():
    users = User.query.all()
    donors = DonorProfile.query.all()
    hospitals = HospitalProfile.query.all()
    blood_requests = BloodRequest.query.order_by(BloodRequest.request_date.desc()).limit(50).all()
    donations = DonationHistory.query.order_by(DonationHistory.donation_date.desc()).limit(50).all()
    return render_template('admin_dashboard.html', title='Admin Panel',
                           users=users, donors=donors, hospitals=hospitals,
                           blood_requests=blood_requests, donations=donations)


@app.route("/admin/delete_user/<int:user_id>", methods=['POST'])
@admin_required
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    if user.role == 'admin':
        flash('Cannot delete admin account.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if user.role == 'donor' and user.donor_profile:
        DonationHistory.query.filter_by(donor_id=user.donor_profile.id).delete()
        db.session.delete(user.donor_profile)
    elif user.role == 'hospital' and user.hospital_profile:
        BloodInventory.query.filter_by(hospital_id=user.hospital_profile.id).delete()
        BloodRequest.query.filter_by(hospital_id=user.hospital_profile.id).delete()
        DonationHistory.query.filter_by(hospital_id=user.hospital_profile.id).delete()
        db.session.delete(user.hospital_profile)

    db.session.delete(user)
    db.session.commit()
    flash(f'User {user.username} has been deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


# --------------- Static Pages ---------------

@app.route("/find_blood")
def find_blood():
    return render_template('find_blood.html', title='Find Blood')

@app.route("/education")
def education():
    return render_template('education.html', title='Learn & FAQs')


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        seed_admin()
    app.run(debug=True)
