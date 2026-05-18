from dataclasses import dataclass
from typing import List, Dict, Any, Optional

@dataclass
class AttritionPredictionDTO:
    probability: float
    risk_score: float
    level: str
    color: str
    model_type: str

@dataclass
class ShapContributionDTO:
    feature: str
    name: str
    value: float

@dataclass
class ShapExplanationDTO:
    risk_factors: List[ShapContributionDTO]
    mitigation_factors: List[ShapContributionDTO]
    raw_shap_contributions: Dict[str, float]

@dataclass
class RetentionRecommendationDTO:
    title: str
    action: str
    priority: str
    trigger_factor: str
    impact_score: float
    service_action: str

@dataclass
class EmployeeAIDashboardDTO:
    employee_id: int
    fullname: str
    position: str
    department: str
    prediction: AttritionPredictionDTO
    explanation: ShapExplanationDTO
    recommendations: List[RetentionRecommendationDTO]
    weekly_attendance_trend: List[Dict[str, Any]]
    radar_values: List[float]
    radar_labels: List[str]
    last_updated: str
