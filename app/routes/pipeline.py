from flask import Blueprint, jsonify, request
from app.services.pipeline_service import PipelineService
from app.core.decorators import hr_required
from flask_login import current_user

pipeline_bp = Blueprint('pipeline', __name__)

@pipeline_bp.route('/board', methods=['GET'])
@hr_required
def get_board():
    try:
        board = PipelineService.get_board()
        return jsonify(board)
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@pipeline_bp.route('/<int:candidate_id>/stage', methods=['POST'])
@hr_required
def update_stage(candidate_id):
    try:
        data = request.json
        new_stage = data.get('stage')
        if not new_stage:
            return jsonify({'error': 'Stage is required'}), 400
            
        pipeline = PipelineService.update_stage(
            candidate_id=candidate_id,
            new_stage=new_stage,
            user_id=current_user.id if current_user.is_authenticated else None
        )
        return jsonify({
            'success': True,
            'message': 'Stage updated',
            'stage': pipeline.stage
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400
