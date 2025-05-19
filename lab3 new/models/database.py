from datetime import datetime
import sqlite3
from .enums import UserRole

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

        # Create prescriptions table
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS prescriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_id INTEGER NOT NULL,
            doctor_id INTEGER NOT NULL,
            prescription_type TEXT NOT NULL,
            description TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_at TIMESTAMP,
            completed_by INTEGER,
            FOREIGN KEY (patient_id) REFERENCES patients (id),
            FOREIGN KEY (doctor_id) REFERENCES doctors (id),
            FOREIGN KEY (completed_by) REFERENCES users (id)
        )
        ''')

        conn.commit()
        conn.close()






    # =============== Authorization Functions ===============
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

    def get_all_users(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        result = []
        for user in users:
            user_dict = dict(user)
            # Add role-specific information
            if UserRole(user_dict['role']) == UserRole.DOCTOR:
                doctor = self.get_doctor_by_user_id(user_dict['id'])
                if doctor:
                    user_dict['specialization'] = doctor['specialization']
            elif UserRole(user_dict['role']) == UserRole.NURSE:
                nurse = self.get_nurse_by_user_id(user_dict['id'])
                if nurse:
                    user_dict['department'] = nurse['department']
            elif UserRole(user_dict['role']) == UserRole.PATIENT:
                patient = self.get_patient_by_user_id(user_dict['id'])
                if patient:
                    user_dict['admission_date'] = patient['admission_date']
                    user_dict['discharge_date'] = patient['discharge_date']
            result.append(user_dict)
        
        conn.close()
        return result






    # =============== Diagnosis Functions ===============
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

    def get_patient_by_id(self, patient_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return dict(patient) if patient else None

    def discharge_patient(self, patient_id, final_diagnosis):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE patients SET discharge_date = ?, final_diagnosis = ? WHERE id = ?',
                (datetime.now(), final_diagnosis, patient_id)
            )
            conn.commit()
            return self.get_patient_by_id(patient_id)
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()





    # =============== Prescriptions Functions ===============
    def add_prescription(self, patient_id, doctor_id, prescription_type, description):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'INSERT INTO prescriptions (patient_id, doctor_id, prescription_type, description) VALUES (?, ?, ?, ?)',
                (patient_id, doctor_id, prescription_type.value, description)
            )
            prescription_id = cursor.lastrowid
            conn.commit()
            return self.get_prescription(prescription_id)
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()

    def get_prescription(self, prescription_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE id = ?', (prescription_id,))
        prescription = cursor.fetchone()
        conn.close()
        return dict(prescription) if prescription else None

    def get_patient_prescriptions(self, patient_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE patient_id = ?', (patient_id,))
        prescriptions = cursor.fetchall()
        conn.close()
        return [dict(prescription) for prescription in prescriptions]

    def complete_prescription(self, prescription_id, completed_by):
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute(
                'UPDATE prescriptions SET status = ?, completed_at = ?, completed_by = ? WHERE id = ?',
                ('completed', datetime.now(), completed_by, prescription_id)
            )
            conn.commit()
            return self.get_prescription(prescription_id)
        except Exception as e:
            conn.rollback()
            return None
        finally:
            conn.close()

db = Database() 