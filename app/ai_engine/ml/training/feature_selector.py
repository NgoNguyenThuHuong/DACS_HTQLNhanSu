import pandas as pd
import numpy as np
from sklearn.feature_selection import mutual_info_classif
from typing import Dict, List, Tuple, Any

class FeatureSelector:
    @staticmethod
    def analyze_correlations(df: pd.DataFrame, target_col: str) -> Dict[str, float]:
        """
        Tính toán hệ số tương quan Pearson giữa tất cả các đặc trưng và cột mục tiêu (target).
        """
        corr_matrix = df.corr()
        if target_col not in corr_matrix.columns:
            return {}
        
        target_corr = corr_matrix[target_col].drop(target_col)
        target_corr = target_corr.fillna(0)
        
        return {k: round(float(v), 4) for k, v in target_corr.to_dict().items()}

    @staticmethod
    def calculate_mutual_info(df: pd.DataFrame, target_col: str, feature_cols: List[str]) -> Dict[str, float]:
        """
        Tính toán thông tin tương hỗ (Mutual Information Score) giữa các đặc trưng và nhãn.
        """
        X = df[feature_cols].fillna(0)
        y = df[target_col]
        
        mi_scores = mutual_info_classif(X, y, random_state=42)
        
        return {feature_cols[i]: round(float(mi_scores[i]), 4) for i in range(len(feature_cols))}

    @classmethod
    def get_top_features(cls, df: pd.DataFrame, target_col: str, feature_cols: List[str], top_k: int = 5) -> List[Tuple[str, float]]:
        """
        Lấy ra Top K đặc trưng quan trọng nhất dựa trên Mutual Information Score.
        """
        mi = cls.calculate_mutual_info(df, target_col, feature_cols)
        sorted_features = sorted(mi.items(), key=lambda x: x[1], reverse=True)
        return sorted_features[:top_k]
