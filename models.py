from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='donor') # 'donor', 'hospital', 'admin'
    
    # Relationships
    donor_profile = db.relationship('DonorProfile', backref='user', uselist=False)
    hospital_profile = db.relationship('HospitalProfile', backref='user', uselist=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.role}')"

class DonorProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=True)
    points = db.Column(db.Integer, default=0)
    last_donation_date = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    donations = db.relationship('DonationHistory', backref='donor', lazy=True)

class HospitalProfile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    hospital_name = db.Column(db.String(150), nullable=False)
    license_number = db.Column(db.String(50), nullable=False)
    contact_person = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    address = db.Column(db.Text, nullable=False)
    latitude = db.Column(db.Float, nullable=True)
    longitude = db.Column(db.Float, nullable=True)
    
    # Relationships
    inventory = db.relationship('BloodInventory', backref='hospital', lazy=True)
    requests = db.relationship('BloodRequest', backref='hospital', lazy=True)

class BloodInventory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital_profile.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_available = db.Column(db.Integer, default=0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

class BloodRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital_profile.id'), nullable=False)
    blood_group = db.Column(db.String(5), nullable=False)
    units_required = db.Column(db.Integer, nullable=False)
    urgency = db.Column(db.String(20), nullable=False) # 'normal', 'urgent', 'emergency'
    status = db.Column(db.String(20), default='pending') # 'pending', 'fulfilled', 'cancelled'
    request_date = db.Column(db.DateTime, default=datetime.utcnow)

class DonationHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    donor_id = db.Column(db.Integer, db.ForeignKey('donor_profile.id'), nullable=False)
    hospital_id = db.Column(db.Integer, db.ForeignKey('hospital_profile.id'), nullable=False)
    donation_date = db.Column(db.DateTime, default=datetime.utcnow)
    units_donated = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='completed')
    points_awarded = db.Column(db.Integer, default=50)

    hospital = db.relationship('HospitalProfile', backref='donations')
