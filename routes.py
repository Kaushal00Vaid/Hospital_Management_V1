from app import app
from flask import render_template, request, flash, redirect, url_for, session
from helper import admin_auth_required, patient_auth_required, doctor_auth_required
from models import db, User, Patient, Doctor

@app.route("/")
def home():
    return render_template("landing.html")

# ------ User Authentication ---------

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
    
# ------ Dashboards ---------
@app.route("/admin/dashboard")
@admin_auth_required
def admin_dashboard():
    return "<h1>Admin Dashboard</h1>" # Placeholder content

@app.route("/user/dashboard")
@patient_auth_required
def user_dashboard():
    return "<h1>Patient Dashboard</h1>" # Placeholder content

@app.route("/doctor/dashboard")
@doctor_auth_required
def doctor_dashboard():
    return "<h1>Doctor Dashboard</h1>" # Placeholder content

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
    newUser.set_password(password)
    db.session.add(newUser)

    db.session.flush() # Use flush to get the new_user.id before committing

    # Create patient profile
    new_doctor = Doctor(user_id=newUser.id, specialization=specialization, availability=availability, phone=phone)

    db.session.add(new_doctor)
    db.session.commit()

    return redirect(url_for("login"))
