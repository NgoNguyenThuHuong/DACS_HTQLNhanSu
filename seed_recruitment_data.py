from app import create_app
from app.extensions import db
from app.models import JobPost, Exam, ExamQuestion

app = create_app()

def seed_data():
    with app.app_context():
        # Job 1: Data Scientist
        job1 = JobPost(
            title="Data Scientist",
            description="Phân tích dữ liệu lớn, xây dựng và triển khai các mô hình Machine Learning/AI để giải quyết bài toán kinh doanh.",
            requirements="Thành thạo Python, SQL. Hiểu biết sâu về Machine Learning (Scikit-learn, XGBoost) và Deep Learning (TensorFlow/PyTorch).",
            status="Open"
        )
        db.session.add(job1)

        exam1 = Exam(
            title="Kiểm tra năng lực Data Scientist",
            duration_minutes=60,
            pass_threshold=7.0
        )
        db.session.add(exam1)
        db.session.flush()

        mcq_ds = [
            ("Thư viện Python nào phổ biến nhất để xử lý dữ liệu dạng bảng?", "NumPy", "Pandas", "Matplotlib", "Scikit-learn", "B"),
            ("Hàm mất mát (Loss function) nào thường dùng cho bài toán phân lớp nhị phân (Binary Classification)?", "MSE", "MAE", "Binary Cross Entropy", "Categorical Cross Entropy", "C"),
            ("Thuật toán nào sau đây thuộc nhóm học không giám sát (Unsupervised Learning)?", "Linear Regression", "Logistic Regression", "K-Means Clustering", "Random Forest", "C"),
            ("Overfitting là hiện tượng gì?", "Mô hình học chưa đủ tốt trên tập train", "Mô hình học quá thuộc lòng tập train và dự đoán kém trên tập test", "Mô hình thiếu dữ liệu huấn luyện", "Mô hình có quá ít tham số", "B"),
            ("Chỉ số nào không phù hợp để đánh giá mô hình phân lớp khi dữ liệu mất cân bằng (imbalanced data)?", "Accuracy", "Precision", "Recall", "F1-score", "A"),
            ("Lớp layer nào trong CNN dùng để trích xuất đặc trưng hình ảnh?", "Dense Layer", "Dropout Layer", "Convolutional Layer", "Pooling Layer", "C"),
            ("Phương pháp nào giúp giảm hiện tượng Overfitting trong Deep Learning?", "Tăng learning rate", "Dropout", "Giảm số lượng dữ liệu", "Tăng số vòng lặp (epochs)", "B"),
            ("K-Fold Cross Validation dùng để làm gì?", "Tăng tốc độ huấn luyện", "Đánh giá mô hình khách quan hơn, tránh overfitting", "Làm sạch dữ liệu", "Tăng số lượng đặc trưng (features)", "B"),
            ("Lệnh SQL nào dùng để gom nhóm dữ liệu?", "ORDER BY", "GROUP BY", "WHERE", "HAVING", "B"),
            ("P-value trong kiểm định giả thuyết thống kê có ý nghĩa gì?", "Xác suất mô hình chính xác 100%", "Mức độ sai số của dữ liệu", "Xác suất quan sát được kết quả nếu giả thuyết không (H0) đúng", "Tỉ lệ dữ liệu bị nhiễu", "C"),
            ("Cấu trúc dữ liệu nào đằng sau thuật toán Random Forest?", "Mảng (Array)", "Đồ thị (Graph)", "Cây quyết định (Decision Tree)", "Danh sách liên kết (Linked List)", "C"),
            ("Thuật toán PCA (Principal Component Analysis) dùng để làm gì?", "Phân lớp", "Hồi quy", "Giảm chiều dữ liệu", "Gom cụm", "C"),
            ("Trong SQL, LEFT JOIN khác INNER JOIN ở điểm nào?", "Lấy tất cả các dòng từ bảng bên trái dù không khớp", "Lấy tất cả các dòng từ bảng bên phải", "Lấy các dòng khớp ở cả 2 bảng", "Không có sự khác biệt", "A"),
            ("Kiểu dữ liệu dictionary trong Python được triển khai bằng cấu trúc dữ liệu nào?", "Array", "Linked List", "Hash Table", "Binary Tree", "C"),
            ("Mô hình BERT được ứng dụng phổ biến trong lĩnh vực nào?", "Computer Vision (CV)", "Natural Language Processing (NLP)", "Reinforcement Learning", "Time Series Forecasting", "B")
        ]

        for i, q in enumerate(mcq_ds, 1):
            eq = ExamQuestion(
                exam_id=exam1.id,
                question_text=q[0],
                question_type='MCQ',
                option_a=q[1],
                option_b=q[2],
                option_c=q[3],
                option_d=q[4],
                correct_option=q[5],
                order_num=i
            )
            db.session.add(eq)

        essay_ds = [
            "Hãy trình bày quy trình chuẩn từ khi nhận dữ liệu thô (raw data) đến khi triển khai (deploy) một mô hình Machine Learning.",
            "Phân biệt giữa L1 Regularization (Lasso) và L2 Regularization (Ridge). Khi nào nên sử dụng loại nào?",
            "Làm thế nào để xử lý bài toán mất cân bằng dữ liệu (Imbalanced Data)? Trình bày ít nhất 3 phương pháp.",
            "Hãy giải thích cách thức hoạt động của thuật toán Gradient Descent.",
            "Trong môi trường sản xuất (Production), làm sao để theo dõi (monitor) xem một mô hình ML có bị suy giảm chất lượng (Model Drift) hay không?"
        ]

        for i, q_text in enumerate(essay_ds, 16):
            eq = ExamQuestion(
                exam_id=exam1.id,
                question_text=q_text,
                question_type='Essay',
                order_num=i
            )
            db.session.add(eq)


        # Job 2: Frontend Developer
        job2 = JobPost(
            title="Frontend Developer",
            description="Phát triển và duy trì các giao diện web tương tác cao, tối ưu hóa trải nghiệm người dùng (UX) và hiệu năng web.",
            requirements="Thành thạo HTML, CSS, JavaScript. Kinh nghiệm với ReactJS, VueJS. Hiểu biết về Responsive Design, Web Performance.",
            status="Open"
        )
        db.session.add(job2)

        exam2 = Exam(
            title="Kiểm tra năng lực Frontend Developer",
            duration_minutes=45,
            pass_threshold=7.0
        )
        db.session.add(exam2)
        db.session.flush()

        mcq_fe = [
            ("Thẻ HTML nào sau đây dùng để tạo một danh sách không thứ tự?", "<ol>", "<ul>", "<li>", "<dl>", "B"),
            ("Thuộc tính CSS nào điều khiển sự thay đổi màu nền một cách mượt mà?", "transition", "transform", "animation", "opacity", "A"),
            ("Trong JavaScript, từ khóa nào khai báo một biến chỉ có phạm vi trong block (block-scoped) và có thể thay đổi giá trị?", "var", "let", "const", "def", "B"),
            ("Đâu không phải là một kiểu dữ liệu nguyên thủy (primitive type) trong JavaScript?", "String", "Number", "Object", "Boolean", "C"),
            ("CSS Flexbox được sử dụng chủ yếu để giải quyết vấn đề gì?", "Tạo hoạt ảnh (animation)", "Sắp xếp bố cục 1 chiều (hàng hoặc cột)", "Tạo hiệu ứng 3D", "Làm trong suốt phần tử", "B"),
            ("Sự khác biệt chính giữa '==' và '===' trong JavaScript là gì?", "'==' chỉ kiểm tra kiểu dữ liệu, '===' kiểm tra giá trị", "'==' kiểm tra cả kiểu dữ liệu và giá trị, '===' chỉ kiểm tra giá trị", "'==' thực hiện ép kiểu trước khi so sánh, '===' thì không", "Không có sự khác biệt", "C"),
            ("Trong ReactJS, Hook nào được dùng để quản lý state nội bộ của functional component?", "useEffect", "useContext", "useReducer", "useState", "D"),
            ("Virtual DOM trong React giúp giải quyết vấn đề gì?", "Tăng cường bảo mật", "Quản lý cơ sở dữ liệu tốt hơn", "Giảm thiểu thao tác trực tiếp lên Real DOM để tăng hiệu năng", "Tạo giao diện đẹp hơn", "C"),
            ("Phương thức mảng nào trong JS tạo ra một mảng mới với các phần tử thỏa mãn một điều kiện cho trước?", "map()", "filter()", "reduce()", "forEach()", "B"),
            ("Để một website hiển thị tốt trên các thiết bị có kích thước màn hình khác nhau, ta sử dụng kỹ thuật nào?", "Server-Side Rendering", "Responsive Web Design", "Progressive Web App", "Single Page Application", "B"),
            ("CORS (Cross-Origin Resource Sharing) là gì?", "Một loại cơ sở dữ liệu", "Một cơ chế bảo mật của trình duyệt ngăn chặn request khác domain", "Một thư viện JavaScript", "Một thẻ HTML", "B"),
            ("Trong CSS, đơn vị 'rem' được tính dựa trên phần tử nào?", "Phần tử cha trực tiếp (parent)", "Phần tử gốc (root/html)", "Chiều rộng cửa sổ trình duyệt (viewport width)", "Không có đơn vị tham chiếu", "B"),
            ("Lệnh console.log(typeof null) trong JavaScript sẽ in ra gì?", "'null'", "'undefined'", "'object'", "'number'", "C"),
            ("Redux là gì?", "Một framework CSS", "Một thư viện quản lý trạng thái (state management)", "Một hệ quản trị cơ sở dữ liệu", "Một ngôn ngữ lập trình", "B"),
            ("Trong Vue.js, directive nào dùng để render danh sách các phần tử từ một mảng?", "v-for", "v-if", "v-show", "v-bind", "A")
        ]

        for i, q in enumerate(mcq_fe, 1):
            eq = ExamQuestion(
                exam_id=exam2.id,
                question_text=q[0],
                question_type='MCQ',
                option_a=q[1],
                option_b=q[2],
                option_c=q[3],
                option_d=q[4],
                correct_option=q[5],
                order_num=i
            )
            db.session.add(eq)

        essay_fe = [
            "Trình bày vòng đời (Lifecycle) của một component trong ReactJS (từ lúc mount đến lúc unmount).",
            "Giải thích sự khác biệt giữa Client-Side Rendering (CSR) và Server-Side Rendering (SSR).",
            "Trình bày các kỹ thuật bạn sử dụng để tối ưu hóa hiệu năng tải trang (Web Performance Optimization).",
            "Event Delegation trong JavaScript là gì? Tại sao lại sử dụng nó thay vì gắn event listener cho từng phần tử con?",
            "Giả sử bạn phải làm một trang web hỗ trợ tính năng đa ngôn ngữ (i18n), bạn sẽ thiết kế và triển khai nó như thế nào?"
        ]

        for i, q_text in enumerate(essay_fe, 16):
            eq = ExamQuestion(
                exam_id=exam2.id,
                question_text=q_text,
                question_type='Essay',
                order_num=i
            )
            db.session.add(eq)

        db.session.commit()
        print("Đã thêm thành công 2 vị trí ứng tuyển và bài thi kèm câu hỏi!")

if __name__ == '__main__':
    seed_data()
