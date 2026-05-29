from app.extensions import db
from datetime import datetime

class CandidatePipeline(db.Model):
    __tablename__ = 'candidate_pipeline'

    id = db.Column(db.Integer, primary_key=True)
    candidate_id = db.Column(db.Integer, db.ForeignKey('candidates.id'), nullable=False, unique=True)
    stage = db.Column(db.String(50), nullable=False, default='New')
    history = db.Column(db.JSON, nullable=True) # Array of {stage, timestamp, user_id}
    hr_notes = db.Column(db.Text, nullable=True)
    ai_recommendation = db.Column(db.JSON, nullable=True)
    risk_indicator = db.Column(db.String(20), nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    candidate = db.relationship('Candidate', backref=db.backref('pipeline', uselist=False))
