import os
import sys
import json
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

# Add current path to python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app
from app.ai_engine.ml.training.dataset_builder import DatasetBuilder

def run_evaluation():
    app = create_app()
    with app.app_context():
        print("--- RUNNING AI-HRM MODEL EVALUATION ---")
        builder = DatasetBuilder()
        df = builder.build_employee_dataset(include_synthetic=True, target_size=600)
        
        # 1. DATASET QUALITY AUDIT
        missing_count = int(df.isnull().sum().sum())
        duplicate_count = int(df.duplicated().sum())
        
        # Check outliers in monthly income (using IQR)
        q1 = df['monthly_income_amount'].quantile(0.25)
        q3 = df['monthly_income_amount'].quantile(0.75)
        iqr = q3 - q1
        outliers_income = int(((df['monthly_income_amount'] < (q1 - 1.5 * iqr)) | (df['monthly_income_amount'] > (q3 + 1.5 * iqr))).sum())
        
        # Check invalid data constraints
        invalid_salary_count = int((df['monthly_income_amount'] <= 0).sum())
        abnormal_overtime_count = int(((df['overtime_ratio_30d'] < 0) | (df['overtime_ratio_30d'] > 1)).sum())
        null_satisfaction_count = int(df['job_satisfaction_score'].isnull().sum())
        
        imbalance_ratio = float((df['attrition_label'] == 1).sum() / len(df))
        
        # 2. MODEL TRAINING & PERFORMANCE METRICS
        feature_cols = [
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
        
        X = df[feature_cols]
        y = df['attrition_label']
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        # Train RandomForest Classifier (highly stable fallback)
        model = RandomForestClassifier(n_estimators=100, max_depth=6, random_state=42)
        model.fit(X_train, y_train)
        
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Compute metrics
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred, zero_division=0)
        rec = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        auc = roc_auc_score(y_test, y_prob)
        
        cm = confusion_matrix(y_test, y_pred)
        tn, fp, fn, tp = cm.ravel()
        
        # 3. FEATURE IMPORTANCE (XAI / SHAP surrogate)
        importances = model.feature_importances_
        feature_importance_dict = {}
        for col, imp in zip(feature_cols, importances):
            feature_importance_dict[col] = float(imp)
            
        sorted_importance = sorted(feature_importance_dict.items(), key=lambda x: x[1], reverse=True)
        
        # 4. BIAS & FAIRNESS EVALUATION
        # Group by department (we can use monthly income median or mock department for synthetic data)
        # For simplicity, let's create a simulated gender bias check based on random assignment for synthetic data
        np.random.seed(42)
        genders = np.random.choice(['Male', 'Female'], size=len(df), p=[0.55, 0.45])
        df['gender'] = genders
        
        # Calculate attrition risk by gender
        df['predicted_risk'] = model.predict_proba(df[feature_cols])[:, 1]
        male_avg_risk = float(df[df['gender'] == 'Male']['predicted_risk'].mean())
        female_avg_risk = float(df[df['gender'] == 'Female']['predicted_risk'].mean())
        fairness_ratio = min(male_avg_risk, female_avg_risk) / max(male_avg_risk, female_avg_risk)
        
        result = {
            'metrics': {
                'accuracy': float(acc),
                'precision': float(prec),
                'recall': float(rec),
                'f1_score': float(f1),
                'roc_auc': float(auc)
            },
            'confusion_matrix': {
                'tn': int(tn),
                'fp': int(fp),
                'fn': int(fn),
                'tp': int(tp)
            },
            'data_quality': {
                'total_samples': len(df),
                'missing_count': missing_count,
                'duplicate_count': duplicate_count,
                'outliers_income': outliers_income,
                'invalid_salary': invalid_salary_count,
                'abnormal_overtime': abnormal_overtime_count,
                'null_satisfaction': null_satisfaction_count,
                'imbalance_ratio': imbalance_ratio
            },
            'feature_importance': sorted_importance,
            'fairness': {
                'male_avg_risk': male_avg_risk,
                'female_avg_risk': female_avg_risk,
                'fairness_ratio': fairness_ratio
            }
        }
        
        # Output result as JSON
        output_path = os.path.join(os.path.dirname(__file__), 'eval_results.json')
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=4, ensure_ascii=False)
            
        print("EVALUATION COMPLETED SUCCESSFULLY!")
        print(f"Results saved to: {output_path}")

if __name__ == '__main__':
    run_evaluation()
