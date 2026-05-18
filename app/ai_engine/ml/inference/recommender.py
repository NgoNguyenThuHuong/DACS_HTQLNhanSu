from typing import List, Dict, Any

class HRActionRecommender:
    @staticmethod
    def generate_recommendations(risk_factors: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ánh xạ tự động các nhân tố rủi ro hàng đầu từ mô hình giải thích SHAP 
        sang các đề xuất hành động thực tiễn của phòng nhân sự (Actionable Recommendations).
        """
        recommendations = []
        
        action_library = {
            'attendance_ratio_30d': {
                'title': 'Rà soát chuyên cần & Sức khỏe',
                'action': 'Tổ chức gặp mặt trao đổi kín để tìm hiểu nguyên nhân đi làm không đều. Có thể nhân viên đang gặp vấn đề cá nhân hoặc sức khỏe.',
                'priority': 'Medium',
                'service_action': 'Cân nhắc điều chỉnh lịch làm việc hoặc chế độ làm việc từ xa tạm thời.'
            },
            'overtime_ratio_30d': {
                'title': 'Cân bằng tải công việc & Chế độ nghỉ bù',
                'action': 'Phê duyệt chế độ nghỉ bù linh hoạt ngay trong tuần tới. Rà soát phân bổ tài nguyên dự án để giảm thiểu thời gian tăng ca liên tục, phòng tránh kiệt sức (burnout).',
                'priority': 'High',
                'service_action': 'Sử dụng HRService.approve_or_reject_leave để duyệt đơn nghỉ phép năm / nghỉ bù ưu tiên.'
            },
            'task_completion_rate': {
                'title': 'Hỗ trợ chuyên môn & Giảm tải Task',
                'action': 'Ghép cặp cùng một Mentor giàu kinh nghiệm để hỗ trợ gỡ rối công việc. Tạm thời giảm 20% khối lượng task mới cho nhân viên.',
                'priority': 'High',
                'service_action': 'Sử dụng HRService.manage_tasks để tái phân bổ nhiệm vụ quá tải.'
            },
            'leave_frequency_90d': {
                'title': 'Đối thoại phúc lợi & Khảo sát nội bộ',
                'action': 'Tìm hiểu xem nhân viên có đang gặp các biến cố gia đình cần hỗ trợ đặc biệt từ quỹ phúc lợi công ty hay không.',
                'priority': 'Medium',
                'service_action': 'Gặp mặt trao đổi trực tiếp tìm giải pháp hỗ trợ.'
            },
            'avg_task_delay_days': {
                'title': 'Rà soát Deadline & Đào tạo quy trình',
                'action': 'Kiểm tra lại tính thực tế của các deadline đã giao. Tổ chức các buổi đào tạo quy trình làm việc chuẩn để đẩy nhanh tốc độ hoàn thành.',
                'priority': 'Medium',
                'service_action': 'Điều chỉnh thời gian hoàn thành của các task kế tiếp.'
            },
            'monthly_income_amount': {
                'title': 'Đánh giá điều chỉnh thu nhập',
                'action': 'Tiến hành rà soát mức lương so với thị trường (Benchmark). Đề xuất thưởng nóng dựa trên năng suất (KPI) hoặc xem xét tăng lương cơ bản trong kỳ đánh giá gần nhất.',
                'priority': 'High',
                'service_action': 'Đề xuất tăng lương hoặc bonus năng suất.'
            },
            'job_satisfaction_score': {
                'title': 'Khảo sát định kỳ 1-1 & Định hướng nghề nghiệp',
                'action': 'Lên lịch phỏng vấn định kỳ 1-1 (Stay Interview) nhằm thu thập phản hồi về môi trường làm việc, giải tỏa bức xúc tâm lý.',
                'priority': 'High',
                'service_action': 'Tổ chức buổi trao đổi riêng tư định hướng lộ trình thăng tiến.'
            },
            'environment_satisfaction_score': {
                'title': 'Cải thiện môi trường làm việc & Quan hệ đồng nghiệp',
                'action': 'Tổ chức các buổi Team Building nhỏ, tạo điều kiện cho nhân viên kết nối tốt hơn với Quản lý trực tiếp và các thành viên trong đội ngũ.',
                'priority': 'Medium',
                'service_action': 'Xây dựng không gian làm việc cởi mở và gắn kết.'
            },
            'workload_score': {
                'title': 'Điều tiết khối lượng công việc',
                'action': 'Hạn chế giao thêm các task thuộc nhóm ưu tiên High. Khuyến khích nhân viên bàn giao bớt các công việc phụ trợ không quan trọng.',
                'priority': 'High',
                'service_action': 'Tái cấu trúc danh mục công việc hàng ngày.'
            },
            'probation_status': {
                'title': 'Đánh giá thử việc & Onboarding support',
                'action': 'Tăng cường tương tác trong giai đoạn hòa nhập (Onboarding). Hỗ trợ nhân viên làm quen nhanh với văn hóa doanh nghiệp và đồng nghiệp.',
                'priority': 'Medium',
                'service_action': 'Tổ chức đánh giá tiến độ định kỳ 30-60-90 ngày thử việc.'
            }
        }
        
        for rf in risk_factors:
            feat_name = rf.get('feature')
            if feat_name in action_library:
                action_info = action_library[feat_name].copy()
                action_info['trigger_factor'] = rf.get('name')
                action_info['impact_score'] = round(rf.get('value', 0.0), 3)
                recommendations.append(action_info)
                
        if not recommendations:
            recommendations.append({
                'title': 'Duy trì động lực & Khuyến khích',
                'action': 'Nhân viên có chỉ số rủi ro rất thấp và cống hiến tốt. Tiếp tục tuyên dương, khen thưởng các thành tích xuất sắc để duy trì năng lượng tích cực.',
                'priority': 'Low',
                'trigger_factor': 'Không phát hiện rủi ro',
                'impact_score': 0.0,
                'service_action': 'Tặng voucher quà tặng hoặc khen thưởng tháng.'
            })
            
        return recommendations
