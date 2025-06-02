from datetime import datetime

class PatientManager:
    def __init__(self, db):
        self.db = db

    def get_patient_by_user_id(self, user_id):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM patients WHERE user_id = ?', (user_id,))
        patient = cursor.fetchone()
        
        if patient:
            return dict(patient)
        return None

    def get_patient_by_id(self, patient_id):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM patients WHERE id = ?', (patient_id,))
        patient = cursor.fetchone()
        conn.close()
        return dict(patient) if patient else None

    def discharge_patient(self, patient_id, final_diagnosis):
        conn = self.db.db.get_connection()
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