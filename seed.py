# seed.py

import random
from faker import Faker
from datetime import datetime, timedelta

from app import app
from models import db, User, Doctor, Patient, Appointment, Treatment, Payment

fake = Faker('en_IN')

def seed_data():
    with app.app_context():
        print("Starting database seeding...")

        # --- Clean up existing data ---
        print("Deleting existing data (except Admin)...")
        Treatment.query.delete()
        Payment.query.delete()
        Appointment.query.delete()
        Doctor.query.delete()
        Patient.query.delete()
        User.query.filter(User.role != 'Admin').delete()
        db.session.commit()

        # --- Seed Doctors ---
        print("Seeding Doctors...")
        specializations = ['Cardiology', 'Dermatology', 'Neurology', 'Pediatrics', 'Orthopedics']
        for _ in range(10):
            doctor_user = User(name=f"Dr. {fake.name()}", email=fake.email(), role='Doctor')
            doctor_user.set_password('test')
            db.session.add(doctor_user)
            db.session.flush()
            doctor_profile = Doctor(user_id=doctor_user.id, specialization=random.choice(specializations), phone=fake.phone_number(), availability="Mon-Fri, 9 AM - 5 PM")
            db.session.add(doctor_profile)
        
        # --- Seed Patients ---
        print("Seeding Patients...")
        blood_groups = ['A+', 'A-', 'B+', 'B-', 'AB+', 'AB-', 'O+', 'O-']
        for _ in range(40):
            patient_user = User(name=fake.name(), email=fake.email(), role='Patient')
            patient_user.set_password('test')
            db.session.add(patient_user)
            db.session.flush()
            patient_profile = Patient(user_id=patient_user.id, age=random.randint(5, 80), gender=random.choice(['Male', 'Female', 'Other']), blood_group=random.choice(blood_groups), phone=fake.phone_number(), address=fake.address())
            db.session.add(patient_profile)
        
        db.session.commit()

        # --- Seed Appointments ---
        print("Seeding 100 Appointments...")
        all_doctor_ids = [d.id for d in Doctor.query.all()]
        all_patient_ids = [p.id for p in Patient.query.all()]
        for _ in range(100):
            db.session.add(Appointment(doctor_id=random.choice(all_doctor_ids), patient_id=random.choice(all_patient_ids), appointment_date=fake.date_time_between(start_date='-30d', end_date='+30d'), status='Scheduled'))
        db.session.commit()

        # --- Update Appointment Statuses ---
        # Mark about 50% as completed
        appointments_to_complete = Appointment.query.filter_by(status='Scheduled').order_by(db.func.random()).limit(50).all()
        for appt in appointments_to_complete:
            appt.status = 'Completed'
        
        # Mark about 20% of the remaining as cancelled
        appointments_to_cancel = Appointment.query.filter_by(status='Scheduled').order_by(db.func.random()).limit(20).all()
        for appt in appointments_to_cancel:
            appt.status = 'Cancelled'
        db.session.commit()

        # --- Seed Treatments & Payments ---
        completed_appointments = Appointment.query.filter_by(status='Completed').all()
        print(f"Adding treatments for {len(completed_appointments)} completed appointments...")
        for appt in completed_appointments:
            db.session.add(Treatment(appointment_id=appt.id, diagnosis=fake.bs().title(), prescription=f"Take 1 pill of {fake.word().capitalize()} twice daily.", notes=f"Thik hojaa bhai..."))
        
        all_appointments = Appointment.query.all()
        print(f"Adding payments for {min(len(all_appointments), 70)} appointments...")
        for appt in random.sample(all_appointments, k=min(len(all_appointments), 70)):
            db.session.add(Payment(appointment_id=appt.id, amount=round(random.uniform(500.0, 5000.0), 2), status=random.choice(['pending', 'paid'])))

        db.session.commit()
        print("Database seeding completed successfully! All tables are now populated.")

if __name__ == '__main__':
    seed_data()