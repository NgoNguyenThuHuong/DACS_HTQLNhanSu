from services.analytics_service import AnalyticsService

# Backward Compatibility Adapter for system-wide old imports
_analytics_service = AnalyticsService()

def get_turnover_risk_ai():
    return _analytics_service.get_turnover_risk_ai_dashboard()

def get_individual_performance(emp_id):
    # Trả về kết quả khớp với cấu trúc cũ
    perf = _analytics_service.get_individual_performance_metrics(emp_id)
    return {
        'score': perf['score'],
        'present_days': perf['present_days'],
        'leave_days': perf['leave_days'],
        'att_score': perf['att_score']
    }

def get_attendance_trend(days=7):
    return _analytics_service.analytics_repo.get_attendance_trend(days)

def get_recent_activity(limit=10):
    return _analytics_service.analytics_repo.get_recent_activities(limit)

def get_individual_radar_data(emp_id):
    return _analytics_service.get_individual_radar_data(emp_id)

def get_radar_data():
    return _analytics_service.get_system_radar_data()
