from app.repositories.base_repo import BaseRepository
from app.models import Candidate, JobPost, Exam, ExamQuestion, ExamResult, CandidateAnswer
from app.extensions import db
from sqlalchemy.orm import joinedload

class RecruitmentRepository(BaseRepository):
    model = Candidate

    def get_candidates_filtered(self, status="", search=""):
        query = db.session.query(Candidate).options(joinedload(Candidate.results), joinedload(Candidate.job))
        if status:
            query = query.filter(Candidate.status == status)
        if search:
            query = query.filter(
                (Candidate.fullname.ilike(f'%{search}%')) |
                (Candidate.email.ilike(f'%{search}%'))
            )
        return query.order_by(Candidate.created_at.desc()).all()

    def get_candidate_by_id(self, can_id):
        return db.session.query(Candidate)\
            .options(joinedload(Candidate.results), joinedload(Candidate.job))\
            .filter(Candidate.id == can_id)\
            .first()

    def get_candidates_stats(self):
        stats_raw = db.session.query(
            Candidate.status,
            db.func.count(Candidate.id)
        ).group_by(Candidate.status).all()
        
        stats_dict = dict(stats_raw)
        
        jobs = db.session.query(JobPost).options(joinedload(JobPost.candidates)).all()
        job_labels = [j.title for j in jobs]
        job_counts = [len(j.candidates) for j in jobs]
        
        return {
            'total': db.session.query(Candidate).count(),
            'applied': stats_dict.get('Applied', 0),
            'testing': stats_dict.get('Testing', 0),
            'passed': stats_dict.get('Passed', 0),
            'failed': stats_dict.get('Failed', 0),
            'job_labels': job_labels,
            'job_counts': job_counts
        }

    # Job Posts
    def get_all_jobs(self):
        return db.session.query(JobPost).order_by(JobPost.created_at.desc()).all()

    def get_job_by_id(self, job_id):
        return db.session.query(JobPost).filter(JobPost.id == job_id).first()

    def add_job_post(self, title, description, requirements):
        job = JobPost(title=title, description=description, requirements=requirements)
        db.session.add(job)
        return job

    # Exams
    def get_all_exams(self):
        return db.session.query(Exam).all()

    def get_exam_by_id(self, exam_id):
        return db.session.query(Exam).options(joinedload(Exam.questions)).filter(Exam.id == exam_id).first()

    def add_exam(self, title, duration_minutes, pass_threshold):
        exam = Exam(title=title, duration_minutes=duration_minutes, pass_threshold=pass_threshold)
        db.session.add(exam)
        return exam

    def delete_exam(self, exam):
        db.session.delete(exam)

    # Exam Questions
    def get_question_by_id(self, q_id):
        return db.session.query(ExamQuestion).filter(ExamQuestion.id == q_id).first()

    def add_question(self, exam_id, question_text, question_type, option_a=None, option_b=None, 
                     option_c=None, option_d=None, correct_option=None, order_num=1):
        q = ExamQuestion(
            exam_id=exam_id,
            question_text=question_text,
            question_type=question_type,
            option_a=option_a,
            option_b=option_b,
            option_c=option_c,
            option_d=option_d,
            correct_option=correct_option,
            order_num=order_num
        )
        db.session.add(q)
        return q

    def delete_question(self, question):
        db.session.delete(question)

    # Exam Results
    def get_result_by_id(self, result_id):
        return db.session.query(ExamResult).filter(ExamResult.id == result_id).first()

    def get_results_by_candidate(self, can_id):
        return db.session.query(ExamResult).filter(ExamResult.candidate_id == can_id).all()
