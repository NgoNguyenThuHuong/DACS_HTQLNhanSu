import os
import pickle
import pandas as pd
from sklearn.model_selection import train_test_split
from app.ai_engine.ml.training.dataset_builder import DatasetBuilder
from app.ai_engine.ml.training.evaluation import ModelEvaluator
from app.ai_engine.ml.training.feature_selector import FeatureSelector

class AttritionTrainingPipeline:
    def __init__(self):
        self.dataset_builder = DatasetBuilder()
        self.feature_cols = [
            'attendance_ratio_30d',
            'overtime_ratio_30d',
            'task_completion_rate',
            'leave_frequency_90d',
            'avg_task_delay_days',
            'monthly_income_amount',
            'years_at_company',
            'promotion_gap_months',
            'job_satisfaction_score',
            'environment_satisfaction_score',
            'workload_score',
            'probation_status'
        ]
        self.target_col = 'attrition_label'

    def run(self, save_dir: str = None) -> dict:
        """
        Khởi chạy toàn bộ luồng huấn luyện offline (Offline Training Pipeline):
        1. Tạo/Nạp dữ liệu
        2. Chia tập Train/Test
        3. Huấn luyện XGBoost Classifier (fallback sang RandomForest nếu import lỗi)
        4. Đánh giá chất lượng mô hình
        5. Xuất bản lưu trữ Model artifact
        """
        df = self.dataset_builder.build_employee_dataset(include_synthetic=True, target_size=600)
        
        X = df[self.feature_cols]
        y = df[self.target_col]

        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

        model = None
        try:
            from xgboost import XGBClassifier
            model = XGBClassifier(
                n_estimators=100,
                max_depth=4,
                learning_rate=0.05,
                random_state=42,
                eval_metric='logloss',
                use_label_encoder=False
            )
            model.fit(X_train, y_train)
            model_type = "XGBoost"
        except (ImportError, Exception):
            from sklearn.ensemble import RandomForestClassifier
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=6,
                random_state=42
            )
            model.fit(X_train, y_train)
            model_type = "RandomForest"

        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        metrics = ModelEvaluator.evaluate_classifier(y_test.values, y_pred, y_prob)
        metrics['model_type'] = model_type

        if save_dir is None:
            save_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'models')
        os.makedirs(save_dir, exist_ok=True)
        
        model_path = os.path.join(save_dir, 'xgboost_attrition_v1.bin')
        
        payload = {
            'model': model,
            'feature_cols': self.feature_cols,
            'model_type': model_type,
            'metrics': metrics,
            'trained_at': pd.Timestamp.now().isoformat()
        }
        
        with open(model_path, 'wb') as f:
            pickle.dump(payload, f)
            
        metrics['model_saved_path'] = model_path
        return metrics

if __name__ == '__main__':
    pipeline = AttritionTrainingPipeline()
    res = pipeline.run()
    print("Training finished:", res)
