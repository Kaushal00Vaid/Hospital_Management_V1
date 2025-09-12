from functools import wraps
from flask import session, flash, redirect, url_for
from models import User

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