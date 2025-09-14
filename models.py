from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash

# initialize SQLAlchemy
db = SQLAlchemy()

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(30), nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    doctor_profile = db.relationship('Doctor', backref='user', uselist=False, cascade="all, delete-orphan")
    patient_profile = db.relationship('Patient', backref='user', uselist=False, cascade="all, delete-orphan")

    # hashing password
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # checking password
    def check_password(self, password):
        return check_password_hash(self.password, password)


# inserting admin
def insert_admin(*args, **kwargs):
    if not User.query.filter_by(email="admin@gmail.com").first():
        admin = User(
            email="admin@gmail.com",
            password="admin",
            name="Admin",
            role="Admin",
        )
        admin.set_password("admin") # hash the password
        db.session.add(admin)
        db.session.commit()
        print("Admin Added")
    else:
        print("Admin already exists")

class Doctor(db.Model):
    __tablename__ = "doctors"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    specialization = db.Column(db.String(100))
    phone = db.Column(db.String(30))
    availability = db.Column(db.String(120))

    # doctor is "one" user (doctor.user)
    # uselist for specifying one to one instead of one to many
    # user = db.relationship("User", backref=db.backref("doctor", lazy=True, uselist=False))

class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False, unique=True)
    age = db.Column(db.Integer)
    gender = db.Column(db.String(10))
    blood_group = db.Column(db.String(5))
    phone = db.Column(db.String(20))
    address = db.Column(db.Text)

    # user = db.relationship("User", backref=db.backref("patient", uselist=False))

class Appointment(db.Model):
    __tablename__ = "appointments"

    id = db.Column(db.Integer, primary_key=True)
    patient_id = db.Column(db.Integer, db.ForeignKey("patients.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("doctors.id"), nullable=False)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(20), default="scheduled")  # scheduled, completed, cancelled
    notes = db.Column(db.Text)

    patient = db.relationship("Patient", backref=db.backref("appointments", cascade="all, delete-orphan"))
    doctor = db.relationship("Doctor", backref=db.backref("appointments", cascade="all, delete-orphan"))
    
class Treatment(db.Model):
    __tablename__ = "treatments"

    id = db.Column(db.Integer, primary_key=True)
    
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False, unique=True)
    
    diagnosis = db.Column(db.Text)
    prescription = db.Column(db.Text)
    record_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))
    notes = db.Column(db.Text)

    appointment = db.relationship("Appointment", backref=db.backref("treatment", uselist=False, cascade="all, delete-orphan"))
    
    
class Payment(db.Model):
    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)
    
    appointment_id = db.Column(db.Integer, db.ForeignKey("appointments.id"), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), default="pending")  # pending, paid
    billing_date = db.Column(db.DateTime, default=datetime.now(timezone.utc))

    appointment = db.relationship("Appointment", backref=db.backref("payment", uselist=False, cascade="all, delete-orphan"))


def create_tables():
    db.create_all()
    insert_admin()