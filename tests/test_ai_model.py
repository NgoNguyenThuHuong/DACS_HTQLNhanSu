import unittest
import os
import sys

# Add current path to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.ai_engine.ml.inference.turnover_predictor import TurnoverPredictor

class TestAttritionAIModel(unittest.TestCase):
    def setUp(self):
        self.predictor = TurnoverPredictor()

    def test_risk_prediction_bounds_and_structure(self):
        # Sample employee feature vector
        features = {
            'attendance_ratio_30d': 0.95,
            'overtime_ratio_30d': 1.0,
            'task_completion_rate': 0.85,
            'leave_frequency_90d': 2,
            'avg_task_delay_days': 1.5,
            'monthly_income_amount': 5000.0,
            'years_at_company': 2.5,
            'promotion_gap_months': 12,
            'job_satisfaction_score': 0.5,
            'environment_satisfaction_score': 0.75,
            'workload_score': 0.6,
            'probation_status': 0
        }
        
        result = self.predictor.predict_turnover_probability(features)
        
        # Verify output structure
        self.assertIn('probability', result)
        self.assertIn('risk_score', result)
        self.assertIn('level', result)
        self.assertIn('color', result)
        self.assertIn('model_type', result)
        
        # Verify value constraints
        self.assertTrue(0.0 <= result['probability'] <= 1.0)
        self.assertTrue(0.0 <= result['risk_score'] <= 100.0)
        self.assertIn(result['level'], ['HIGH', 'MEDIUM', 'LOW'])
        self.assertIn(result['color'], ['danger', 'warning', 'success'])

    def test_extreme_unhappy_employee(self):
        # Unhappy employee: Low salary, high overtime, low satisfaction, high delay
        unhappy_features = {
            'attendance_ratio_30d': 0.6,
            'overtime_ratio_30d': 1.0,
            'task_completion_rate': 0.4,
            'leave_frequency_90d': 8,
            'avg_task_delay_days': 10.0,
            'monthly_income_amount': 3000.0,
            'years_at_company': 1.0,
            'promotion_gap_months': 12,
            'job_satisfaction_score': 0.25,
            'environment_satisfaction_score': 0.25,
            'workload_score': 0.9,
            'probation_status': 0
        }
        
        result = self.predictor.predict_turnover_probability(unhappy_features)
        
        # Expect higher risk than a happy employee
        happy_features = {
            'attendance_ratio_30d': 0.99,
            'overtime_ratio_30d': 0.0,
            'task_completion_rate': 0.98,
            'leave_frequency_90d': 0,
            'avg_task_delay_days': 0.0,
            'monthly_income_amount': 15000.0,
            'years_at_company': 5.0,
            'promotion_gap_months': 2,
            'job_satisfaction_score': 1.0,
            'environment_satisfaction_score': 1.0,
            'workload_score': 0.4,
            'probation_status': 0
        }
        
        happy_result = self.predictor.predict_turnover_probability(happy_features)
        self.assertGreater(result['probability'], happy_result['probability'])

if __name__ == '__main__':
    unittest.main()
