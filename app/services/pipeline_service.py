from app.extensions import db
from app.models.pipeline import CandidatePipeline
from app.models.models import Candidate
from datetime import datetime
import json

class PipelineService:
    @staticmethod
    def get_board():
        # Get all pipelines and group by stage
        pipelines = db.session.query(CandidatePipeline, Candidate).join(Candidate).all()
        board = {
            'New': [],
            'Testing': [],
            'Interview': [],
            'Offer': [],
            'Hired': [],
            'Rejected': []
        }
        for pipeline, candidate in pipelines:
            if pipeline.stage not in board:
                board[pipeline.stage] = []
                
            board[pipeline.stage].append({
                'id': pipeline.id,
                'candidate_id': candidate.id,
                'fullname': candidate.fullname,
                'email': candidate.email,
                'status': candidate.status,
                'stage': pipeline.stage,
                'risk_indicator': pipeline.risk_indicator
            })
        return board

    @staticmethod
    def update_stage(candidate_id, new_stage, user_id=None):
        pipeline = db.session.query(CandidatePipeline).filter_by(candidate_id=candidate_id).first()
        if not pipeline:
            pipeline = CandidatePipeline(candidate_id=candidate_id, stage='New', history=[])
            db.session.add(pipeline)
            
        history = pipeline.history or []
        # Append new history event
        event = {
            'from_stage': pipeline.stage,
            'to_stage': new_stage,
            'timestamp': datetime.utcnow().isoformat(),
            'user_id': user_id
        }
        
        # We need to explicitly assign to trigger SQLAlchemy JSON update
        new_history = list(history)
        new_history.append(event)
        pipeline.history = new_history
        pipeline.stage = new_stage
        
        db.session.commit()
        return pipeline
