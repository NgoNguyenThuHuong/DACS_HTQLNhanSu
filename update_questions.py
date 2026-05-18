import sys
import codecs
sys.stdout = codecs.getwriter('utf-8')(sys.stdout.detach()) if hasattr(sys.stdout, 'detach') else sys.stdout

from app import create_app
from database.models import Exam, ExamQuestion, CandidateAnswer
from core.extensions import db

app = create_app()

print("Bắt đầu cập nhật ngân hàng câu hỏi...")

with app.app_context():
    # 1. Tìm kỳ thi mặc định (hoặc tạo mới nếu chưa có)
    exam = Exam.query.first()
    if not exam:
        print("Không tìm thấy Exam. Tạo mới Exam mặc định...")
        exam = Exam(title='Bài thi IT & EQ đầu vào', duration_minutes=45, pass_threshold=7.0)
        db.session.add(exam)
        db.session.commit()
    
    exam_id = exam.id
    
    # 2. Xóa các câu trả lời cũ của ứng viên liên quan đến các câu hỏi cũ
    # (Bắt buộc để tránh lỗi Foreign Key Constraint)
    print("Đang dọn dẹp các câu trả lời cũ...")
    old_questions = ExamQuestion.query.filter_by(exam_id=exam_id).all()
    old_q_ids = [q.id for q in old_questions]
    if old_q_ids:
        deleted_answers = CandidateAnswer.query.filter(CandidateAnswer.question_id.in_(old_q_ids)).delete(synchronize_session=False)
        print(f"  -> Đã xóa {deleted_answers} câu trả lời của ứng viên.")
    
    # 3. Xóa câu hỏi cũ
    print("Đang xóa câu hỏi cũ...")
    deleted_questions = ExamQuestion.query.filter_by(exam_id=exam_id).delete()
    print(f"  -> Đã xóa {deleted_questions} câu hỏi.")
    
    # 4. Thêm 15 câu hỏi trắc nghiệm mới
    print("Đang thêm 15 câu hỏi trắc nghiệm mới...")
    mcq_data = [
        ("Hệ thống thông tin (Information System) bao gồm những thành phần nào?", 
         "Phần cứng và phần mềm", "Con người, quy trình, dữ liệu, phần mềm, phần cứng", "Chỉ dữ liệu và phần mềm", "Chỉ con người và dữ liệu", "B"),
        ("DBMS là gì?", 
         "Hệ điều hành", "Hệ quản trị cơ sở dữ liệu", "Phần mềm diệt virus", "Ngôn ngữ lập trình", "B"),
         ("SQL dùng để làm gì?",
          "Thiết kế giao diện", "Quản lý và truy vấn dữ liệu", "Viết ứng dụng mobile", "Quản lý mạng", "B"),
         ("Khóa chính (Primary Key) có đặc điểm gì?",
          "Có thể trùng", "Có thể NULL", "Không trùng và không NULL", "Chỉ dùng cho bảng lớn", "C"),
         ("ERD dùng để:",
          "Viết code", "Mô hình hóa dữ liệu", "Thiết kế giao diện", "Test phần mềm", "B"),
         ("Trong mô hình OSI, tầng nào xử lý địa chỉ IP?",
          "Transport", "Network", "Data Link", "Application", "B"),
         ("HTTP là gì?",
          "Giao thức truyền file", "Giao thức web", "Ngôn ngữ lập trình", "Hệ điều hành", "B"),
         ("CRUD là viết tắt của:",
          "Create, Read, Update, Delete", "Code, Run, Update, Debug", "Connect, Read, Upload, Download", "Create, Remove, Use, Deploy", "A"),
         ("Normalization trong database nhằm mục đích gì?",
          "Tăng dung lượng", "Giảm dư thừa dữ liệu", "Tăng tốc CPU", "Tạo giao diện đẹp", "B"),
         ("API là gì?",
          "Giao diện người dùng", "Cách các hệ thống giao tiếp với nhau", "Hệ điều hành", "Cơ sở dữ liệu", "B"),
         ("SaaS là mô hình gì?",
          "Phần mềm cài đặt offline", "Phần mềm cung cấp qua internet", "Phần cứng máy chủ", "Mạng LAN", "B"),
         ("Dữ liệu “structured data” là gì?",
          "Dữ liệu có cấu trúc rõ ràng (bảng)", "Video", "Hình ảnh", "Âm thanh", "A"),
         ("Use Case Diagram dùng để:",
          "Thiết kế database", "Mô tả chức năng hệ thống", "Viết code", "Test phần mềm", "B"),
         ("Phương pháp Agile có đặc điểm gì?",
          "Làm một lần xong luôn", "Linh hoạt, chia nhỏ sprint", "Không cần khách hàng", "Không cần test", "B"),
         ("Một hệ thống ERP dùng để:",
          "Chơi game", "Quản lý tổng thể doanh nghiệp", "Thiết kế web", "Quản lý mạng", "B")
    ]
    
    order = 1
    for text, a, b, c, d, correct in mcq_data:
        q = ExamQuestion(
            exam_id=exam_id,
            question_text=text,
            question_type='MCQ',
            order_num=order,
            option_a=a,
            option_b=b,
            option_c=c,
            option_d=d,
            correct_option=correct
        )
        db.session.add(q)
        order += 1
        
    # 5. Thêm 5 câu hỏi tự luận mới
    print("Đang thêm 5 câu hỏi tự luận mới...")
    essay_data = [
        "Trong quá trình làm dự án hệ thống thông tin, nếu bạn và đồng đội bất đồng quan điểm về cách thiết kế (database, use case, kiến trúc), bạn sẽ xử lý như thế nào?",
        "Khi hệ thống bạn đang phát triển gặp lỗi nghiêm trọng (bug production) và khách hàng đang cần gấp, bạn sẽ xử lý tình huống này ra sao?",
        "Nếu bạn được giao một công nghệ mới (ví dụ: framework, database, hoặc hệ thống chưa từng dùng), bạn sẽ học và áp dụng như thế nào để hoàn thành công việc?",
        "Trong quá trình làm việc, nếu bạn phát hiện một lỗ hổng hoặc sai sót trong hệ thống do đồng nghiệp gây ra, bạn sẽ xử lý như thế nào để đảm bảo hiệu quả công việc và giữ mối quan hệ tốt?",
        "Theo bạn, trong ngành Hệ thống thông tin, điều gì quan trọng hơn: kỹ năng kỹ thuật (code, database, system design) hay kỹ năng mềm (giao tiếp, teamwork)? Hãy giải thích trong bối cảnh thực tế dự án."
    ]
    
    for text in essay_data:
        q = ExamQuestion(
            exam_id=exam_id,
            question_text=text,
            question_type='Essay',
            order_num=order
        )
        db.session.add(q)
        order += 1

    db.session.commit()
    print("✅ HOÀN TẤT! Đã cập nhật thành công bộ đề thi mới (15 câu trắc nghiệm, 5 câu tự luận).")
