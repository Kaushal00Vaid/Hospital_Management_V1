from functools import wraps
from flask import session, flash, redirect, url_for
from models import User
from datetime import datetime

# authentication for admin
def admin_auth_required(func):
    @wraps(func)
    def inner(*args,**kwargs):
        if 'user_id' not in session:
            flash('Please login first.',category='danger')
            return redirect(url_for('login'))
        
        user = User.query.get(session["user_id"])
        if user.role != "Admin":
            flash('Access denied. Only admin can access this page.', category='danger')
            return redirect(url_for('home'))
        return func(*args, **kwargs)
    return inner

# authentication for patient
def patient_auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.',category='danger')
            return redirect(url_for('login'))
        user = User.query.get(session["user_id"])
        if user.role != "Patient":
            flash('Access denied. Only Patients can access this page',category='danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

# authentication for doctor
def doctor_auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please login first.',category='danger')
            return redirect(url_for('login'))
        user = User.query.get(session["user_id"])
        if user.role != "Doctor":
            flash('Access denied. Only Doctor can access this page',category='danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner

# authentication for admin OR patient
def admin_or_patient_auth_required(func):
    @wraps(func)
    def inner(*args, **kwargs):
        if 'user_id' not in session:
            flash('Please log in to access this page.', 'danger')
            return redirect(url_for('login'))
        user = User.query.get(session["user_id"])
        if user.role != "Admin" and user.role != "Patient":
            flash('Access denied. Only Admin or Patient can access this page',category='danger')
            return redirect(url_for('login'))
        return func(*args, **kwargs)
    return inner


# availability check
def is_doctor_available(appointment_datetime, availability_string):
    """
    Checks if an appointment datetime is within a doctor's availability string.
    Expected format: "Mon-Fri, 9 AM - 5 PM"
    """
    try:
        # split and parse days tehen time
        days_part, times_part = availability_string.split(', ')
        
        day_map = {"Mon": 0, "Tue": 1, "Wed": 2, "Thu": 3, "Fri": 4, "Sat": 5, "Sun": 6}
        start_day_str, end_day_str = days_part.split('-')
        start_day = day_map[start_day_str]
        end_day = day_map[end_day_str]

        start_time_str, end_time_str = times_part.split(' - ')
        start_time = datetime.strptime(start_time_str, "%I %p").time()
        end_time = datetime.strptime(end_time_str, "%I %p").time()

        # check if requested whitin range
        appointment_day = appointment_datetime.weekday()
        appointment_time = appointment_datetime.time()

        if not (start_day <= appointment_day <= end_day):
            return False, "The selected day is outside the doctor's working days."

        # check time valid range
        if not (start_time <= appointment_time < end_time):
            return False, "The selected time is outside the doctor's working hours."
            
        return True, "Slot is available."

    except (ValueError, KeyError):
        return False, "Could not parse the doctor's availability schedule. Please contact support."