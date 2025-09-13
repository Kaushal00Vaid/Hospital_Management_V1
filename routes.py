from app import app
from flask import render_template, request, flash, redirect, url_for, session
from sqlalchemy import or_
from datetime import date
from helper import admin_auth_required, patient_auth_required, doctor_auth_required, admin_or_patient_auth_required
from models import db, User, Patient, Doctor, Appointment

@app.route("/")
def home():
    return render_template("landing.html")

# --------------- AUTHENTICATION AND RBAC ----------------

# patient register
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    # if post
    name = request.form.get('name')
    email = request.form.get("email")
    password = request.form.get("password")

    age = request.form.get("age")
    bloodGroup = request.form.get("bloodGroup")
    gender = request.form.get("gender")
    phone = request.form.get("phone")
    address = request.form.get("address")

    if not name or not email or not password or not age or not bloodGroup or not phone or not address:
        flash("Provide all fields", category="danger")
        return redirect(url_for("register"))
    
    # checking if email already present or not
    if User.query.filter_by(email=email).first():
        flash('This email is already being used.',category='danger')
        return redirect(url_for('register'))
    
    # checking if valid bloodgroup
    combinations = [
        "A+",
        "A-",
        "B+",
        "B-",
        "AB+",
        "AB-",
        "O+",
        "O-"
    ]
    if bloodGroup not in combinations:
        flash('Enter valid Blood Group',category='danger')
        return redirect(url_for('register'))
    
    # checking if phone length valid
    if len(phone) != 10:
        flash('Enter valid phone number (length 10)',category='danger')
        return redirect(url_for('register'))
    
    # create User
    newUser = User(email=email, name=name, password=password, role="Patient")
    newUser.set_password(password)
    db.session.add(newUser)

    db.session.flush() # Use flush to get the new_user.id before committing

    # Create patient profile
    new_patient = Patient(user_id=newUser.id, age=age, gender=gender, blood_group=bloodGroup, phone=phone, address=address)

    db.session.add(new_patient)
    db.session.commit()

    if 'user_id' in session:
        return redirect(url_for("admin_dashboard"))
    
    return redirect(url_for("login"))

# login for all roles
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    
    # if post
    email = request.form.get("email")
    password = request.form.get("password")

    if(not email or not password):
        flash("Please Provide all required field", category="danger")
        return redirect(url_for("login"))

    user = User.query.filter_by(email=email).first()

    # checking credentials
    if not user or not user.check_password(password):
        flash("Wrong Credentials", category="danger")
        return redirect(url_for("login"))
    
    session['user_id'] = user.id

    if(user.role == "Admin"):
        return redirect(url_for("admin_dashboard"))
    
    if(user.role == "Patient"):
        return redirect(url_for("user_dashboard"))
    
    if(user.role == "Doctor"):
        return redirect(url_for("doctor_dashboard"))
    
# logout for all roles
@app.route("/logout", methods=["POST"])
def logout():
    if request.method == "POST":
        session.pop('user_id', None)
        return redirect(url_for("home"))
    
# ------------------------ DASHBOARDS --------------------
@app.route("/admin/dashboard")
@admin_auth_required
def admin_dashboard():
    # search params
    doctor_query = request.args.get('doctor_search', '')
    patient_query = request.args.get('patient_search', '')

    # base
    doctors_base_query = db.session.query(User, Doctor).join(Doctor, User.id == Doctor.user_id)
    patients_base_query = db.session.query(User, Patient).join(Patient, User.id == Patient.user_id)

    # if doctor query
    if doctor_query:
        doctors_base_query = doctors_base_query.filter(
            or_(
                User.name.ilike(f'%{doctor_query}%'),
                Doctor.specialization.ilike(f'%{doctor_query}%')
            )
        )
    
    # if patient query
    if patient_query:
        # Check if the query is a number for ID search
        search_id = None
        try:
            search_id = int(patient_query)
        except ValueError:
            pass # Not a number, so don't search by ID

        patient_filter_conditions = [
            User.name.ilike(f'%{patient_query}%'),
            Patient.phone.ilike(f'%{patient_query}%')
        ]
        
        if search_id is not None:
            patient_filter_conditions.append(Patient.id == search_id)

        patients_base_query = patients_base_query.filter(or_(*patient_filter_conditions))
    
    doctors = doctors_base_query.all()
    patients = patients_base_query.all()
    appointments = Appointment.query.all()

    today_appointments = [i for i in appointments if i.appointment_date.date() == date.today()]
    no_of_appointment_today = len(today_appointments)


    return render_template("admin/dashboard.html", doctors=doctors, patients=patients, no_of_appointment_today=no_of_appointment_today, appointments=appointments,doctor_query=doctor_query,
        patient_query=patient_query)

@app.route("/user/dashboard")
@patient_auth_required
def user_dashboard():
    return "<h1>Patient Dashboard</h1>" # Placeholder content

@app.route("/doctor/dashboard")
@doctor_auth_required
def doctor_dashboard():
    return "<h1>Doctor Dashboard</h1>" # Placeholder content

# ------------------------ ADMIN ROUTES -------------------

# Doctor Register
@app.route("/admin/doctor_register", methods=["GET", "POST"])
@admin_auth_required
def doctor_register():
    if request.method == "GET":
        return render_template("doctor_registration.html")
    
    # if post
    name = request.form.get('name')
    email = request.form.get("email")
    password = request.form.get("password")

    specialization = request.form.get("specialization")
    phone = request.form.get("phone")
    availability = request.form.get("availability")

    if not name or not email or not password or not specialization or not phone  or not availability:
        flash("Provide all fields", category="danger")
        return redirect(url_for("doctor_register"))
    
    # checking if email already present or not
    if User.query.filter_by(email=email).first():
        flash('This email is already being used.',category='danger')
        return redirect(url_for('doctor_register'))
    
    # checking if phone length valid
    if len(phone) != 10:
        flash('Enter valid phone number (length 10)',category='danger')
        return redirect(url_for('doctor-register'))
    
    # create User
    newUser = User(email=email, name=name, password=password, role="Doctor")

    # print(newUser) # debug print

    newUser.set_password(password)
    db.session.add(newUser)

    db.session.flush() # Use flush to get the new_user.id before committing

    # Create patient profile
    new_doctor = Doctor(user_id=newUser.id, specialization=specialization, availability=availability, phone=phone)

    db.session.add(new_doctor)
    db.session.commit()

    if 'user_id' in session:
        return redirect(url_for("admin_dashboard"))

    return redirect(url_for("login"))

# edit doc
@app.route("/admin/doctor/edit/<int:doctor_id>", methods=['GET', 'POST'])
@admin_auth_required
def edit_doctor(doctor_id):
    
    # get doc detail (join User and Doctor)
    doctor_data = db.session.query(User, Doctor).join(Doctor, User.id == Doctor.user_id).filter(Doctor.id == doctor_id).first_or_404()

    # print(doctor_data) # debug print
    
    if request.method == 'POST':
        user_to_update = doctor_data.User
        doctor_to_update = doctor_data.Doctor

        # form data
        user_to_update.name = request.form.get('name')
        new_email = request.form.get('email')
        doctor_to_update.specialization = request.form.get('specialization')
        doctor_to_update.phone = request.form.get('phone')
        doctor_to_update.availability = request.form.get('availability')

        # repeated email check
        if new_email != user_to_update.email:
            # print(edit checkpoint) # debug print
            existing_user = User.query.filter_by(email=new_email).first()
            if existing_user:
                flash('That email address is already registered.', 'danger')
                return render_template("admin/edit_doctor.html", doctor_data=doctor_data)
        
        user_to_update.email = new_email
        
        db.session.commit()
        
        flash(f'Doctor {user_to_update.name}\'s profile has been updated!', 'success')
        return redirect(url_for('admin_dashboard'))

    # if get
    return render_template("admin/edit_doctor.html", doctor_data=doctor_data)

# delete doc
@app.route("/admin/doctor/delete/<int:doctor_id>", methods=['POST'])
@admin_auth_required
def delete_doctor(doctor_id):

    # print("delete ghus gaya bhai") # debug print

    # get doc and user
    doctor_to_delete = Doctor.query.get_or_404(doctor_id)
    user_to_delete = User.query.get_or_404(doctor_to_delete.user_id)
    
    # for flash
    doctor_name = user_to_delete.name
    
    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash(f'Doctor {doctor_name} has been successfully deleted.', 'success')
    return redirect(url_for('admin_dashboard'))

# edit patient
@app.route("/patient/edit/<int:patient_id>", methods=['GET', 'POST'])
@admin_or_patient_auth_required  
def edit_patient(patient_id):
    # login detail
    current_user = User.query.get(session['user_id'])
    
    # get patient profile
    patient_to_edit = Patient.query.get_or_404(patient_id)

    # patient only updating his profile (not others)
    if current_user.role == 'Patient' and current_user.id != patient_to_edit.user_id:
        flash('You are not authorized to view or edit this profile.', 'danger')
        return redirect(url_for('user_dashboard'))

    patient_data = db.session.query(User, Patient).join(Patient, User.id == Patient.user_id).filter(Patient.id == patient_id).first()

    if request.method == 'POST':
        user_to_update = patient_data.User
        patient_to_update = patient_data.Patient

        # Update fields...
        user_to_update.name = request.form.get('name')

        # repeated email check
        if request.form.get('email') != user_to_update.email:
            # print(edit checkpoint) # debug print
            existing_user = User.query.filter_by(email=request.form.get('email')).first()
            if existing_user:
                flash('That email address is already registered.', 'danger')
                # print("email change kr (edit patient)") # debug print
                return render_template("patient/edit_patient.html", patient_data=patient_data)
        user_to_update.email = request.form.get('email') 

        patient_to_update.phone = request.form.get('phone')
        patient_to_update.age = request.form.get('age')
        patient_to_update.gender = request.form.get('gender')
        patient_to_update.blood_group = request.form.get('bloodGroup')
        patient_to_update.address = request.form.get('address')
        
        db.session.commit()
        flash('Profile updated successfully!', 'success')

        if current_user.role == 'Admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))

    return render_template('patient/edit_patient.html', patient_data=patient_data)

# delete patient
@app.route("/admin/patient/delete/<int:patient_id>", methods=['POST'])
@admin_auth_required
def delete_patient(patient_id):
    patient_to_delete = Patient.query.get_or_404(patient_id)
    user_to_delete = User.query.get_or_404(patient_to_delete.user_id)
    
    # for flash
    patient_name = user_to_delete.name

    db.session.delete(user_to_delete)
    db.session.commit()
    
    flash(f'Patient {patient_name} and all associated data have been permanently deleted.', 'success')
    return redirect(url_for('admin_dashboard'))


