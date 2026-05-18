import os
import json
import logging
from datetime import datetime
from typing import Dict, Any

class AIAuditLogger:
    """
    Quản lý lưu dấu kiểm toán (AI Governance, Governance & Reproducibility).
    Toàn bộ các sự kiện dự báo, lý giải XAI, đề xuất hệ khuyến nghị
    sẽ được ghi nhận có hệ thống phục vụ mục đích kiểm định mô hình.
    """
    def __init__(self, log_dir: str = None):
        if log_dir is None:
            log_dir = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
                'trained_models'
            )
        os.makedirs(log_dir, exist_ok=True)
        self.log_file = os.path.join(log_dir, 'ai_inference_audit.jsonl')

    def log_inference(self, employee_id: int, request_type: str, result: Dict[str, Any]):
        """
        Ghi nhận sự kiện suy luận vào tệp JSON Lines (JSONL).
        """
        payload = {
            'timestamp': datetime.utcnow().isoformat(),
            'employee_id': employee_id,
            'request_type': request_type,
            'result': result
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(payload, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"[AIAuditLogger] Failed to write log: {e}")

# Khởi tạo instance dùng chung
ai_audit = AIAuditLogger()
