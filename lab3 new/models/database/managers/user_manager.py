import sqlite3
from models.enums.user_enums import UserRole

class UserManager:
    def __init__(self, db):
        self.db = db

    def add_user(self, username, password, role, name, **kwargs):
        conn = self.db.db.get_connection()
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
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE id = ?', (user_id,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

    def get_user_by_username(self, username):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        
        if user:
            return dict(user)
        return None

    def get_all_users(self):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM users')
        users = cursor.fetchall()
        
        result = []
        for user in users:
            user_dict = dict(user)
            if UserRole(user_dict['role']) == UserRole.DOCTOR:
                doctor = self.get_doctor_by_user_id(user_dict['id'])
                if doctor:
                    user_dict['specialization'] = doctor['specialization']
            elif UserRole(user_dict['role']) == UserRole.NURSE:
                nurse = self.get_nurse_by_user_id(user_dict['id'])
                if nurse:
                    user_dict['department'] = nurse['department']
            elif UserRole(user_dict['role']) == UserRole.PATIENT:
                patient = self.db.patients.get_patient_by_user_id(user_dict['id'])
                if patient:
                    user_dict['admission_date'] = patient['admission_date']
                    user_dict['discharge_date'] = patient['discharge_date']
            result.append(user_dict)
        
        conn.close()
        return result

    def get_doctor_by_user_id(self, user_id):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM doctors WHERE user_id = ?', (user_id,))
        doctor = cursor.fetchone()
        
        if doctor:
            return dict(doctor)
        return None

    def get_nurse_by_user_id(self, user_id):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM nurses WHERE user_id = ?', (user_id,))
        nurse = cursor.fetchone()
        
        if nurse:
            return dict(nurse)
        return None