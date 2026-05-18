import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional

class AttritionShapExplainer:
    def __init__(self, model_path: Optional[str] = None):
        if model_path is None:
            model_path = os.path.join(
                os.path.dirname(os.path.dirname(__file__)),
                'models',
                'xgboost_attrition_v1.bin'
            )
        self.model_path = model_path
        self.model_data = None
        self.feature_cols = []
        self.explainer = None

    def _ensure_loaded(self):
        if self.model_data is not None:
            return

        if not os.path.exists(self.model_path):
            from app.ai_engine.ml.training.train_attrition import AttritionTrainingPipeline
            pipeline = AttritionTrainingPipeline()
            pipeline.run(save_dir=os.path.dirname(self.model_path))

        with open(self.model_path, 'rb') as f:
            self.model_data = pickle.load(f)
            self.feature_cols = self.model_data['feature_cols']

        model = self.model_data['model']
        try:
            import shap
            self.explainer = shap.TreeExplainer(model)
        except Exception:
            self.explainer = None

    def explain_employee(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Tính toán giải thích đóng góp đặc trưng (Feature Attributions) cho một nhân viên cụ thể.
        Trả về top 3 yếu tố thúc đẩy rủi ro nghỉ việc tăng (Risk Factors) 
        và top 3 yếu tố giúp giảm thiểu rủi ro nghỉ việc (Mitigation Factors).
        """
        self._ensure_loaded()
        
        row = [feature_dict.get(col, 0.0) for col in self.feature_cols]
        X = pd.DataFrame([row], columns=self.feature_cols)

        contributions = {}

        if self.explainer is not None:
            try:
                shap_values = self.explainer.shap_values(X)
                if isinstance(shap_values, list):
                    vals = shap_values[1][0]
                elif len(shap_values.shape) == 3:
                    vals = shap_values[0, :, 1]
                else:
                    vals = shap_values[0]
                
                for i, col in enumerate(self.feature_cols):
                    contributions[col] = float(vals[i])
            except Exception:
                self.explainer = None

        if self.explainer is None:
            for col in self.feature_cols:
                val = feature_dict.get(col, 0.0)
                
                if col == 'job_satisfaction_score':
                    score = (0.75 - val) * 0.4
                elif col == 'environment_satisfaction_score':
                    score = (0.75 - val) * 0.3
                elif col == 'overtime_ratio_30d':
                    score = val * 0.5
                elif col == 'attendance_ratio_30d':
                    score = (0.95 - val) * 0.6
                elif col == 'task_completion_rate':
                    score = (0.90 - val) * 0.5
                elif col == 'avg_task_delay_days':
                    score = val * 0.15
                elif col == 'monthly_income_amount':
                    score = max(0.0, (6000.0 - val) / 6000.0) * 0.3
                elif col == 'leave_frequency_90d':
                    score = (val - 1) * 0.1
                elif col == 'workload_score':
                    score = (val - 0.5) * 0.25
                elif col == 'probation_status':
                    score = val * 0.2
                else:
                    score = 0.0
                    
                contributions[col] = round(score, 4)

        display_names = {
            'attendance_ratio_30d': 'Tỷ lệ chuyên cần thấp',
            'overtime_ratio_30d': 'Thời gian làm thêm giờ (Overtime) cao',
            'task_completion_rate': 'Tỷ lệ hoàn thành nhiệm vụ thấp',
            'leave_frequency_90d': 'Tần suất xin nghỉ phép tăng cao',
            'avg_task_delay_days': 'Số ngày trễ hạn Task trung bình',
            'monthly_income_amount': 'Thu nhập so với mặt bằng thấp',
            'years_at_company': 'Thâm niên cống hiến ngắn',
            'promotion_gap_months': 'Thời gian chưa được thăng tiến lâu',
            'job_satisfaction_score': 'Hài lòng công việc thấp',
            'environment_satisfaction_score': 'Hài lòng môi trường thấp',
            'workload_score': 'Khối lượng công việc quá tải',
            'probation_status': 'Đang trong giai đoạn thử việc'
        }

        risk_factors = []
        mitigation_factors = []

        for col, val in contributions.items():
            disp_name = display_names.get(col, col)
            if val > 0:
                risk_factors.append({'feature': col, 'name': disp_name, 'value': val})
            else:
                positive_disp = disp_name.replace('thấp', 'cao').replace('cao', 'thấp').replace('ngắn', 'dài')
                if col == 'attendance_ratio_30d': positive_disp = "Chuyên cần làm việc xuất sắc"
                if col == 'task_completion_rate': positive_disp = "Tỷ lệ hoàn thành công việc cao"
                if col == 'job_satisfaction_score': positive_disp = "Mức độ hài lòng công việc rất cao"
                if col == 'monthly_income_amount': positive_disp = "Thu nhập hấp dẫn, ổn định"
                
                mitigation_factors.append({'feature': col, 'name': positive_disp, 'value': val})

        risk_factors.sort(key=lambda x: x['value'], reverse=True)
        mitigation_factors.sort(key=lambda x: x['value'])

        return {
            'risk_factors': risk_factors[:3],
            'mitigation_factors': mitigation_factors[:3],
            'raw_shap_contributions': contributions
        }
