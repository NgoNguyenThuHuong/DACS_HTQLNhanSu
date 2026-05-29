import os
import json
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, accuracy_score, precision_score, recall_score, f1_score
from app import create_app
from app.ai.feature_engineering import get_training_dataset

def train_pipeline():
    app = create_app()
    with app.app_context():
        print("Đang trích xuất features từ database...")
        X, y = get_training_dataset()
        
        if X is None or len(X) < 10:
            print("Không đủ dữ liệu để train mô hình!")
            return
            
        print(f"Tổng số mẫu: {len(X)}. Đặc trưng (Features): {len(X.columns)}")
        print(f"Tỷ lệ nhãn (Active=0, Resigned=1): {y.value_counts().to_dict()}")
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
        
        print("Đang huấn luyện RandomForest với class_weight='balanced'...")
        model = RandomForestClassifier(
            n_estimators=200,
            class_weight='balanced',
            random_state=42,
            max_depth=7
        )
        model.fit(X_train, y_train)
        
        # Đánh giá
        y_pred = model.predict(X_test)
        y_prob = model.predict_proba(X_test)[:, 1]
        
        # Metrics
        acc = accuracy_score(y_test, y_pred)
        precision = precision_score(y_test, y_pred, zero_division=0)
        recall = recall_score(y_test, y_pred, zero_division=0)
        f1 = f1_score(y_test, y_pred, zero_division=0)
        try:
            roc_auc = roc_auc_score(y_test, y_prob)
        except ValueError:
            roc_auc = 0.5 # Trong trường hợp chỉ có 1 class trong test set
            
        cm = confusion_matrix(y_test, y_pred)
        
        print("\n=== ĐÁNH GIÁ MÔ HÌNH (EVALUATION METRICS) ===")
        print(f"Accuracy : {acc:.4f}")
        print(f"Precision: {precision:.4f}")
        print(f"Recall   : {recall:.4f}")
        print(f"F1-Score : {f1:.4f}")
        print(f"ROC-AUC  : {roc_auc:.4f}")
        print(f"Confusion Matrix:\n{cm}")
        print(classification_report(y_test, y_pred, target_names=['Active', 'Resigned']))
        
        # Feature Importances
        importances = model.feature_importances_
        feature_names = X.columns
        feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        print("\n=== TOP FEATURES ===")
        for f, imp in feat_imp[:5]:
            print(f"- {f}: {imp:.4f}")
            
        # Lưu Model
        save_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models')
        os.makedirs(save_dir, exist_ok=True)
        
        model_path = os.path.join(save_dir, 'attrition_model.pkl')
        meta_path = os.path.join(save_dir, 'model_metadata.json')
        
        joblib.dump(model, model_path)
        
        metadata = {
            "training_date": datetime.now().isoformat(),
            "model_version": "v1.0",
            "algorithm": "RandomForestClassifier(class_weight='balanced')",
            "sklearn_version": joblib.__version__, # Joblib holds sklearn models fine, we'll use a string
            "features": list(X.columns),
            "metrics": {
                "accuracy": acc,
                "precision": precision,
                "recall": recall,
                "f1_score": f1,
                "roc_auc": roc_auc
            }
        }
        
        with open(meta_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=4)
            
        print(f"\n[OK] Mô hình đã lưu tại: {model_path}")

if __name__ == '__main__':
    train_pipeline()
