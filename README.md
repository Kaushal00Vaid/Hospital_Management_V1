# Hospital Management V1

## Project for FUN

**MAD-1 Project for Sept-2025 Term**

A web-based application built with Flask, SQLite (via SQLAlchemy), Jinja2, and Bootstrap to streamline hospital operations.

---

## Features

- **Patient Management** – register, update, and make appointments.
- **Doctor Management** – maintain doctor profiles, schedules, and specializations.
- **Appointments –** book, re-schedule, or cancel appointments between patients and doctors.
- **Medical Records** – store and retrieve patient history, diagnoses, and prescriptions.
- **Admin Dashboard** – centralized control for hospital staff and system administrators.

The goal of the project is to provide a simple, efficient, and user-friendly system for handling day-to-day hospital activities.

---

## Project Structure

```
Hospital_Management_V1/
│── instance/
│   ├── CureAID.db  # SQLite database
│── static/
│   ├── assets/
│   ├── style.css  # Stylesheet
│── templates/  # HTML Templates
│── .env  # Environment variables
│── .gitignore  # Git ignore file
│── app.py  # Main Flask application
│── config.py  # Configuration settings
│── models.py  # Database models (SQLAlchemy)
│── routes.py  # Routes and application logic
│── README.md  # Project documentation
```

---

## Installation & Setup

### 1. Clone the Repository

```sh
git clone https://github.com/Kaushal00Vaid/Hospital_Management_V1.git
cd Hospital_Management_V1
```

### 2. Create and Activate a Virtual Environment (Optional)

```sh
python -m venv venv
# Activate Virtual Environment:
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```sh
pip install -r requirements.txt
```

### 4. Run the Application

```sh
python app.py
```

The application will be available at: **http://127.0.0.1:5000/**

---

## License

This project is for educational purposes and follows an open-source license.

---

## Author

**Kaushal Vaid**
IITM BS Degree

For queries, reach out at **kaushalvaid123@gmail.com**.

---

Enjoy using **CureAID!** 🚀
