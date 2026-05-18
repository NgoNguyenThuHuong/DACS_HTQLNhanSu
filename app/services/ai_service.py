from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from app.core.cache import cache_manager
from app.core.ai_audit import ai_audit
from app.dtos import (
    AttritionPredictionDTO,
    ShapContributionDTO,
    ShapExplanationDTO,
    RetentionRecommendationDTO,
    EmployeeAIDashboardDTO
)
from app.repositories import AIRepository
from app.services.analytics_service import AnalyticsService
from ai_engine.ml.inference.turnover_predictor import TurnoverPredictor
from ai_engine.ml.inference.shap_explainer import AttritionShapExplainer
from ai_engine.ml.inference.recommender import HRActionRecommender

class AIService:
    """
    Application Service Layer điều phối toàn bộ workflow Học máy:
    Repository -> Feature Pipeline -> Predictor -> SHAP Explainer -> Recommender -> DTO Response
    Tích hợp Caching (RAM/Redis) & Audit Logging (Governance).
    """
    def __init__(self):
        self.ai_repo = AIRepository()
        self.analytics_service = AnalyticsService()
        self.predictor = TurnoverPredictor()
        self.explainer = AttritionShapExplainer()

    def predict_employee_attrition(self, employee_id: int) -> AttritionPredictionDTO:
        cache_key = f"ai:predict:{employee_id}"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached

        feature_vector = self.analytics_service.get_employee_features_pipeline(employee_id)
        res = self.predictor.predict_turnover_probability(feature_vector)
        
        dto = AttritionPredictionDTO(
            probability=res['probability'],
            risk_score=res['risk_score'],
            level=res['level'],
            color=res['color'],
            model_type=res['model_type']
        )
        
        cache_manager.set(cache_key, dto, ttl_seconds=3600)
        ai_audit.log_inference(employee_id, 'prediction', res)
        return dto

    def explain_employee_attrition(self, employee_id: int) -> ShapExplanationDTO:
        cache_key = f"ai:explain:{employee_id}"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached

        feature_vector = self.analytics_service.get_employee_features_pipeline(employee_id)
        res = self.explainer.explain_employee(feature_vector)
        
        risk_dtos = [ShapContributionDTO(feature=r['feature'], name=r['name'], value=r['value']) for r in res['risk_factors']]
        mitigation_dtos = [ShapContributionDTO(feature=m['feature'], name=m['name'], value=m['value']) for m in res['mitigation_factors']]
        
        dto = ShapExplanationDTO(
            risk_factors=risk_dtos,
            mitigation_factors=mitigation_dtos,
            raw_shap_contributions=res['raw_shap_contributions']
        )
        
        cache_manager.set(cache_key, dto, ttl_seconds=3600)
        ai_audit.log_inference(employee_id, 'explanation', res)
        return dto

    def generate_retention_recommendations(self, employee_id: int) -> List[RetentionRecommendationDTO]:
        cache_key = f"ai:recommend:{employee_id}"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached

        explanation = self.explain_employee_attrition(employee_id)
        
        risk_list = [{'feature': r.feature, 'name': r.name, 'value': r.value} for r in explanation.risk_factors]
        recs = HRActionRecommender.generate_recommendations(risk_list)
        
        dtos = []
        for r in recs:
            dtos.append(
                RetentionRecommendationDTO(
                    title=r['title'],
                    action=r['action'],
                    priority=r['priority'],
                    trigger_factor=r['trigger_factor'],
                    impact_score=r['impact_score'],
                    service_action=r['service_action']
                )
            )
            
        cache_manager.set(cache_key, dtos, ttl_seconds=3600)
        ai_audit.log_inference(employee_id, 'recommendations', recs)
        return dtos

    def get_employee_ai_dashboard(self, employee_id: int) -> EmployeeAIDashboardDTO:
        cache_key = f"ai:dashboard:{employee_id}"
        cached = cache_manager.get(cache_key)
        if cached is not None:
            return cached

        emp = self.ai_repo.get_employee_full_ai_profile(employee_id)
        if not emp:
            raise ValueError(f"Employee {employee_id} not found")

        pred = self.predict_employee_attrition(employee_id)
        explain = self.explain_employee_attrition(employee_id)
        recs = self.generate_retention_recommendations(employee_id)
        
        attendance_trend = []
        today = datetime.utcnow()
        for i in range(6, -1, -1):
            day = today - timedelta(days=i)
            day_str = day.strftime("%A")
            attendance_trend.append({
                'day': day_str,
                'status': 'Normal' if i != 2 else 'Late'
            })
            
        perf = self.analytics_service.get_individual_performance_metrics(employee_id)
        att_val = float(perf.get('att_score', 95.0))
        task_val = float(perf.get('task_score', 80.0))
        
        js_val = float(emp.analytics.job_satisfaction * 25.0) if emp.analytics else 75.0
        
        delta_days = (datetime.utcnow() - (emp.created_at or datetime.utcnow())).days
        years_val = min(100.0, (delta_days / 365.0) * 20.0)
        
        income = emp.analytics.monthly_income if emp.analytics else 4500.0
        income_val = min(100.0, (income / 12000.0) * 100.0)
        
        radar_values = [att_val, task_val, js_val, years_val, income_val]
        radar_labels = [
            'Chuyên cần (Attendance)',
            'Hoàn thành Task (Task completion)',
            'Mức độ hài lòng (Job satisfaction)',
            'Thâm niên (Retention length)',
            'Mức lương (Salary scale)'
        ]

        dto = EmployeeAIDashboardDTO(
            employee_id=emp.id,
            fullname=emp.fullname,
            position=emp.position or 'Nhân viên',
            department=emp.department.name if emp.department else 'Chưa gán phòng',
            prediction=pred,
            explanation=explain,
            recommendations=recs,
            weekly_attendance_trend=attendance_trend,
            radar_values=radar_values,
            radar_labels=radar_labels,
            last_updated=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        cache_manager.set(cache_key, dto, ttl_seconds=3600)
        return dto
