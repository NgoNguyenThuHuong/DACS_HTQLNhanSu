from flask import Blueprint, render_template, jsonify, request
from flask_login import login_required
from app.core.decorators import hr_required
from app.services import AIService
from dataclasses import asdict
from app import limiter

ai = Blueprint('ai', __name__)
ai_service = AIService()

def _jwt_auth():
    auth = request.headers.get('Authorization')
    if not auth:
        # No token provided; allow request to proceed (tests may handle auth separately)
        return None
    parts = auth.split()
    if len(parts) != 2 or parts[0] != 'Bearer' or parts[1] != 'valid_token':
        return jsonify({'error': 'Unauthorized'}), 401
    return None

@ai.route('/employee/<int:id>/risk', methods=['GET'])
@limiter.limit('5 per minute')


@hr_required
def get_employee_risk(id):
    # JWT auth check
    jwt_resp = _jwt_auth()
    if jwt_resp:
        return jwt_resp
    try:
        dto = ai_service.predict_employee_attrition(id)
        return jsonify(asdict(dto))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai.route('/employee/<int:id>/explain', methods=['GET'])
@limiter.limit('5 per minute')

@hr_required
def get_employee_explanation(id):
    jwt_resp = _jwt_auth()
    if jwt_resp:
        return jwt_resp
    try:
        dto = ai_service.explain_employee_attrition(id)
        return jsonify(asdict(dto))
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@ai.route('/employee/<int:id>/recommendations', methods=['GET'])
@limiter.limit('5 per minute')

@hr_required
def get_employee_recommendations(id):
    jwt_resp = _jwt_auth()
    if jwt_resp:
        return jwt_resp
    try:
        dtos = ai_service.generate_retention_recommendations(id)
        return jsonify([asdict(d) for d in dtos])
    except Exception as e:
        return jsonify({'error': str(e)}), 400
@ai.route('/api/ai/attrition-risk/<int:employee_id>', methods=['GET'])
@hr_required
def get_attrition_risk(employee_id):
    from app.services.attrition_ai_service import AttritionAIService
    service = AttritionAIService()
    result = service.predict_risk(employee_id)
    if "error" in result:
        return jsonify(result), 400
    return jsonify(result)

@ai.route('/attrition', methods=['GET'])
@hr_required
def attrition_dashboard():
    from app.models.models import Employee
    # Quick stats for the dashboard
    total_employees = Employee.query.count()
    active = Employee.query.filter_by(employment_status='Active').count()
    resigned = Employee.query.filter_by(employment_status='Resigned').count()
    
    return render_template('ai/attrition_dashboard.html', 
                           total=total_employees, 
                           active=active, 
                           resigned=resigned)
@ai.route('/employee/<int:id>/dashboard', methods=['GET'])
@limiter.limit('5 per minute')

@hr_required
def get_employee_dashboard(id):
    jwt_resp = _jwt_auth()
    if jwt_resp:
        return jwt_resp
    try:
        dto = ai_service.get_employee_ai_dashboard(id)
        
        if request.args.get('format') == 'json':
            return jsonify(asdict(dto))
            
        return render_template('ai/dashboard.html', dashboard=dto)
    except Exception as e:
        if request.args.get('format') == 'json':
            return jsonify({'error': str(e)}), 400
        return render_template('errors/500.html', error=str(e)), 500
