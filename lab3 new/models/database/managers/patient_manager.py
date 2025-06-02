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

    def search_patients(self, name='', diagnosis='', status='', admission_date=''):
        conn = self.db.db.get_connection()
        cursor = conn.cursor()
        
        query = '''
            SELECT p.*, u.name as patient_name 
            FROM patients p
            JOIN users u ON p.user_id = u.id
            WHERE 1=1
        '''
        params = []
        
        if name:
            query += ' AND u.name LIKE ?'
            params.append(f'%{name}%')
            
        if diagnosis:
            query += ' AND (p.current_diagnosis LIKE ? OR p.final_diagnosis LIKE ?)'
            params.extend([f'%{diagnosis}%', f'%{diagnosis}%'])
            
        if status:
            if status.lower() == 'active':
                query += ' AND p.discharge_date IS NULL'
            elif status.lower() == 'discharged':
                query += ' AND p.discharge_date IS NOT NULL'
                
        if admission_date:
            query += ' AND DATE(p.admission_date) = DATE(?)'
            params.append(admission_date)
            
        cursor.execute(query, params)
        patients = cursor.fetchall()
        conn.close()
        
        return [dict(patient) for patient in patients]