from datetime import datetime

class PrescriptionManager:
    def __init__(self, db):
        self.db = db

    def add_prescription(self, patient_id, doctor_id, prescription_type, description):
        conn = self.db.db.get_connection()
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
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE id = ?', (prescription_id,))
        prescription = cursor.fetchone()
        conn.close()
        return dict(prescription) if prescription else None

    def get_patient_prescriptions(self, patient_id):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM prescriptions WHERE patient_id = ?', (patient_id,))
        prescriptions = cursor.fetchall()
        conn.close()
        return [dict(prescription) for prescription in prescriptions]

    def complete_prescription(self, prescription_id, completed_by):
        conn = self.db.db.get_connection()
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