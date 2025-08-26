from app import db
from datetime import datetime
import json

class AudioAnalysis(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    upload_timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    analysis_timestamp = db.Column(db.DateTime)
    
    # Educational context
    subject = db.Column(db.String(100))  # Materia/asignatura
    grade_level = db.Column(db.String(50))  # Grado escolar
    lesson_topic = db.Column(db.String(255))  # Tema de la clase
    additional_context = db.Column(db.Text)  # Contexto adicional
    
    # Transcription results
    transcription_text = db.Column(db.Text)
    transcription_data = db.Column(db.Text)  # JSON string for detailed transcription
    
    # Prosodic analysis results
    prosody_data = db.Column(db.Text)  # JSON string for prosodic metrics
    
    # RIC AI feedback
    ric_feedback = db.Column(db.Text)  # JSON string for AI-generated feedback
    
    # Analysis status
    status = db.Column(db.String(50), default='uploaded')  # uploaded, processing, completed, error
    error_message = db.Column(db.Text)
    
    def get_transcription_data(self):
        """Parse transcription data from JSON"""
        if self.transcription_data:
            try:
                return json.loads(self.transcription_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_transcription_data(self, data):
        """Store transcription data as JSON"""
        self.transcription_data = json.dumps(data)
    
    def get_prosody_data(self):
        """Parse prosody data from JSON"""
        if self.prosody_data:
            try:
                return json.loads(self.prosody_data)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_prosody_data(self, data):
        """Store prosody data as JSON"""
        self.prosody_data = json.dumps(data)
    
    def get_ric_feedback(self):
        """Parse RIC feedback from JSON"""
        if self.ric_feedback:
            try:
                return json.loads(self.ric_feedback)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def set_ric_feedback(self, data):
        """Store RIC feedback as JSON"""
        self.ric_feedback = json.dumps(data)
    
    def get_educational_context(self):
        """Get educational context as dictionary"""
        return {
            'subject': self.subject or 'General',
            'grade_level': self.grade_level or 'No especificado',
            'lesson_topic': self.lesson_topic or 'Tema general',
            'additional_context': self.additional_context or ''
        }
