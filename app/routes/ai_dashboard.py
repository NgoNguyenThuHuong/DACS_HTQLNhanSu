from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.core.decorators import hr_required
from app.services import AIService
from dataclasses import asdict

ai = Blueprint('ai', __name__)
ai_service = AIService()

@ai.route('/employee/<int:id>/risk', methods=['GET'])
@login_required
@hr_required
def get_employee_risk(id):
    try:
        dto = ai_service.predict_employee_attrition(id)
        return jsonify(asdict(dto))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai.route('/employee/<int:id>/explain', methods=['GET'])
@login_required
@hr_required
def get_employee_explanation(id):
    try:
        dto = ai_service.explain_employee_attrition(id)
        return jsonify(asdict(dto))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai.route('/employee/<int:id>/recommendations', methods=['GET'])
@login_required
@hr_required
def get_employee_recommendations(id):
    try:
        dtos = ai_service.generate_retention_recommendations(id)
        return jsonify([asdict(d) for d in dtos])
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai.route('/employee/<int:id>/dashboard', methods=['GET'])
@login_required
@hr_required
def get_employee_dashboard(id):
    try:
        dto = ai_service.get_employee_ai_dashboard(id)
        
        if request.args.get('format') == 'json':
            return jsonify(asdict(dto))
            
        return render_template('ai/dashboard.html', dashboard=dto)
    except Exception as e:
        if request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 400
        return render_template('errors/500.html', error=str(e)), 500
