from enum import Enum
from datetime import datetime
import sqlite3
import json

class UserRole(Enum):
    ADMIN = 'admin'
    DOCTOR = 'doctor'
    NURSE = 'nurse'
    PATIENT = 'patient'

class Database:
    def __init__(self, db_name='hospital.db'):
        self.db_name = db_name
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(self.db_name)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Create users table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''')

        # Create doctors table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS doctors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            specialization TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create nurses table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS nurses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            department TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
        ''')

        # Create patients table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS patients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER UNIQUE,
            doctor_id INTEGER,
            admission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            discharge_date TIMESTAMP,
            current_diagnosis TEXT,
            final_diagnosis TEXT,
            FOREIGN KEY (user_id) REFERENCES users (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id)
        )
        ''')

        conn.commit()
        conn.close()

    def add_user(self, username, password, role, name, **kwargs):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                'INSERT INTO users (username, password, role, name) VALUES (?, ?, ?, ?)',
                (username, password, role.value, name)
            )
            user_id = cursor.lastrowid

            if role == UserRole.DOCTOR:
                cursor.execute(
                    'INSERT INTO doctors (user_id, specialization) VALUES (?, ?)',
                    (user_id, kwargs.get('specialization', ''))
                )
            elif role == UserRole.NURSE:
                cursor.execute(
                    'INSERT INTO nurses (user_id, department) VALUES (?, ?)',
                    (user_id, kwargs.get('department', ''))
                )
            elif role == UserRole.PATIENT:
                cursor.execute(
                    'INSERT INTO patients (user_id, doctor_id) VALUES (?, ?)',
                    (user_id, kwargs.get('doctor_id'))
                )

            conn.commit()
            return self.get_user(user_id)
        except sqlite3.IntegrityError:
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_user(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

    def get_user_by_username(self, username):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

    def get_doctor_by_user_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE user_id = ?', (user_id,))
        doctor = cursor.fetchone()
        
        if doctor:
            return dict(doctor)
        return None

    def get_nurse_by_user_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM nurses WHERE user_id = ?', (user_id,))
        nurse = cursor.fetchone()
        
        if nurse:
            return dict(nurse)
        return None

    def get_patient_by_user_id(self, user_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patients WHERE user_id = ?', (user_id,))
        patient = cursor.fetchone()
        
        if patient:
            return dict(patient)
        return None

db = Database() 
