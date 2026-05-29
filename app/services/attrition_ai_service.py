import os
import joblib
import pandas as pd
from app.ai.feature_engineering import extract_features
from app.models.models import Employee

class AttritionAIService:
    def __init__(self):
        model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), 'models', 'attrition_model.pkl')
        if not os.path.exists(model_path):
            self.model = None
        else:
            self.model = joblib.load(model_path)
            
    def predict_risk(self, employee_id):
        if self.model is None:
            return {"error": "Model not trained yet."}
            
        emp = Employee.query.get(employee_id)
        if not emp:
            return {"error": "Employee not found."}
            
        df = extract_features(employee_id=employee_id)
        if df.empty:
            return {"error": "Cannot extract features for this employee."}
            
        # Drop target for prediction
        if 'target_attrition' in df.columns:
            df = df.drop(columns=['target_attrition'])
            
        X = df.drop(columns=['employee_id'])
        
        prob = self.model.predict_proba(X)[0][1] # Probability of Resigned (class 1)
        pred_class = self.model.predict(X)[0]
        
        # Explainable AI: Extract top factors based on feature value * feature importance
        importances = self.model.feature_importances_
        feature_names = X.columns
        
        # Calculate contribution (simple local approximation: importance * normalized value if we had scaler, 
        # but for RandomForest, feature importance is global. We will highlight the top global features 
        # where the employee has a "bad" value, or just return top global features as factors)
        # Better approach: if it's a known risk feature (like late_count), and it's high, it's a top factor.
        
        factors = []
        # Sort features by global importance
        feat_imp = sorted(zip(feature_names, importances), key=lambda x: x[1], reverse=True)
        
        emp_values = X.iloc[0].to_dict()
        
        for f, imp in feat_imp:
            val = emp_values[f]
            # Simple logic to convert feature name and value to a human readable factor
            if f == 'late_count' and val > 2:
                factors.append(f"Frequent lateness ({val} times)")
            elif f == 'monthly_late_trend' and val > 1:
                factors.append(f"High recent lateness trend")
            elif f == 'job_satisfaction' and val < 3:
                factors.append(f"Low job satisfaction (Score: {val})")
            elif f == 'task_completion_rate' and val < 0.7:
                factors.append(f"Low task completion rate ({val*100:.0f}%)")
            elif f == 'total_overtime_hours' and val > 20:
                factors.append(f"High overtime hours ({val:.1f}h)")
            elif f == 'performance_rating' and val < 3:
                factors.append(f"Low performance rating ({val})")
                
            if len(factors) >= 3:
                break
                
        if len(factors) == 0:
            factors.append("No specific high-risk anomalies detected.")
            
        if prob >= 0.7:
            risk_level = "High"
        elif prob >= 0.4:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        confidence = max(prob, 1 - prob)

        return {
            "employee_id": emp.id,
            "employee_name": emp.fullname,
            "prediction": f"{risk_level} Risk",
            "probability": round(float(prob), 4),
            "confidence": round(float(confidence), 4),
            "risk_level": risk_level,
            "top_factors": factors,
            "feature_values": emp_values,
            "model_version": "v1.0"
        }
