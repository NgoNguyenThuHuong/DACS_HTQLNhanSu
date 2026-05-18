import os
import pickle
import numpy as np
import pandas as pd
from typing import Dict, List, Any, Optional
from app.ai_engine.ml.training.train_attrition import AttritionTrainingPipeline

class TurnoverPredictor:
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

    def _ensure_model_loaded(self):
        """
        Đảm bảo mô hình đã được tải. Nếu file mô hình chưa tồn tại (chạy lần đầu),
        tự động kích hoạt AttritionTrainingPipeline để tự huấn luyện và lưu trữ (Self-Bootstrapping).
        """
        if self.model_data is not None:
            return

        if not os.path.exists(self.model_path):
            print(f"[TurnoverPredictor] Model file {self.model_path} not found. Bootstrapping training...")
            pipeline = AttritionTrainingPipeline()
            pipeline.run(save_dir=os.path.dirname(self.model_path))

        with open(self.model_path, 'rb') as f:
            self.model_data = pickle.load(f)
            self.feature_cols = self.model_data['feature_cols']

    def predict_turnover_probability(self, feature_dict: Dict[str, Any]) -> Dict[str, Any]:
        """
        Dự báo xác suất nghỉ việc cho một nhân viên dựa trên vector đặc trưng của họ.
        """
        self._ensure_model_loaded()
        
        row = []
        for col in self.feature_cols:
            val = feature_dict.get(col, 0.0)
            row.append(val)
            
        X = pd.DataFrame([row], columns=self.feature_cols)
        
        model = self.model_data['model']
        prob = float(model.predict_proba(X)[0, 1])
        
        level = 'HIGH' if prob > 0.6 else ('MEDIUM' if prob > 0.3 else 'LOW')
        color = 'danger' if prob > 0.6 else ('warning' if prob > 0.3 else 'success')
        
        return {
            'probability': round(prob, 4),
            'risk_score': round(prob * 100.0, 1),
            'level': level,
            'color': color,
            'model_type': self.model_data['model_type']
        }

    def predict_batch(self, feature_dicts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Dự báo hàng loạt cho danh sách nhân viên để tối ưu hóa hiệu năng.
        """
        if not feature_dicts:
            return []
            
        self._ensure_model_loaded()
        model = self.model_data['model']
        
        rows = []
        for fd in feature_dicts:
            row = [fd.get(col, 0.0) for col in self.feature_cols]
            rows.append(row)
            
        X = pd.DataFrame(rows, columns=self.feature_cols)
        probs = model.predict_proba(X)[:, 1]
        
        results = []
        for i, prob in enumerate(probs):
            prob = float(prob)
            level = 'HIGH' if prob > 0.6 else ('MEDIUM' if prob > 0.3 else 'LOW')
            results.append({
                'employee_id': feature_dicts[i].get('employee_id'),
                'probability': round(prob, 4),
                'risk_score': round(prob * 100.0, 1),
                'level': level,
                'color': 'danger' if prob > 0.6 else ('warning' if prob > 0.3 else 'success')
            })
            
        return results
