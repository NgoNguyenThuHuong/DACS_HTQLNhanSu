from flask import Blueprint, render_template, request, redirect, url_for, flash, current_app
from flask_login import login_required, current_user
from app.models import JobPost, Candidate, Exam, ExamQuestion, ExamResult, CandidateAnswer
from app.extensions import db
import os
from werkzeug.utils import secure_filename
from datetime import datetime

recruitment = Blueprint('recruitment', __name__)

@recruitment.route('/recruitment')
def public_portal():
    jobs = db.session.query(JobPost).filter(JobPost.status == 'Open').all()
    return render_template('modules/recruitment/portal.html', jobs=jobs)

@recruitment.route('/recruitment/apply/<int:job_id>', methods=['GET', 'POST'])
def apply(job_id):
    job = db.session.query(JobPost).filter(JobPost.id == job_id).first_or_404()
    if request.method == 'POST':
        fullname = request.form.get('fullname')
        email    = request.form.get('email')
        phone    = request.form.get('phone')
        file     = request.files.get('cv')

        if not fullname or not email:
            flash('Vui lòng điền đầy đủ họ tên và email.', 'warning')
            return render_template('modules/recruitment/apply.html', job=job)

        cv_filename = None
        if file and file.filename:
            cv_filename = secure_filename(f"{fullname}_{file.filename}")
            file.save(os.path.join(current_app.config['CV_UPLOAD_FOLDER'], cv_filename))

        candidate = Candidate(
            job_id=job.id,
            fullname=fullname,
            email=email,
            phone=phone,
            cv_path=cv_filename,
            status='Applied'
        )
        db.session.add(candidate)
        db.session.commit()

        flash('Nộp hồ sơ thành công! Vui lòng làm bài kiểm tra trực tuyến bên dưới.', 'success')
        return redirect(url_for('recruitment.start_test', candidate_id=candidate.id))

    return render_template('modules/recruitment/apply.html', job=job)

@recruitment.route('/recruitment/test/<int:candidate_id>')
def start_test(candidate_id):
    candidate = db.session.query(Candidate).filter(Candidate.id == candidate_id).first_or_404()
    exam = db.session.query(Exam).first()
    if not exam:
        flash('Hiện không có bài thi nào được thiết lập. Hồ sơ của bạn đã được ghi nhận.', 'info')
        return redirect(url_for('recruitment.public_portal'))

    questions = db.session.query(ExamQuestion).filter(ExamQuestion.exam_id == exam.id).order_by(ExamQuestion.order_num).all()
    return render_template('modules/recruitment/test.html',
                           candidate=candidate, exam=exam, questions=questions)

@recruitment.route('/recruitment/submit_test/<int:candidate_id>', methods=['POST'])
def submit_test(candidate_id):
    candidate = db.session.query(Candidate).filter(Candidate.id == candidate_id).first_or_404()
    exam_id   = request.form.get('exam_id', type=int)
    exam      = db.session.query(Exam).filter(Exam.id == exam_id).first_or_404()
    questions = db.session.query(ExamQuestion).filter(ExamQuestion.exam_id == exam_id).all()

    result = ExamResult(
        candidate_id=candidate.id,
        exam_id=exam_id,
        status='Under_Review'
    )
    db.session.add(result)
    db.session.flush()

    score_correct = 0
    total_mcq     = 0

    for q in questions:
        given = request.form.get(f'q_{q.id}', '').strip()

        if q.question_type == 'MCQ':
            total_mcq += 1
            correct = (given.upper() == q.correct_option.upper()) if given and q.correct_option else False
            if correct:
                score_correct += 1
            answer = CandidateAnswer(
                result_id=result.id,
                question_id=q.id,
                given_answer=given.upper() if given else None,
                is_correct=correct
            )
        else:
            answer = CandidateAnswer(
                result_id=result.id,
                question_id=q.id,
                given_answer=given if given else None,
                is_correct=None
            )
        db.session.add(answer)

    final_score = round((score_correct / total_mcq) * 10, 1) if total_mcq > 0 else 0

    result.mcq_score   = final_score
    result.mcq_correct = score_correct
    result.mcq_total   = total_mcq

    candidate.status = 'Testing'
    db.session.commit()

    passed = final_score >= exam.pass_threshold
    return render_template('modules/recruitment/thank_you.html',
                           candidate=candidate,
                           score=final_score,
                           total_mcq=total_mcq,
                           score_correct=score_correct,
                           passed=passed,
                           threshold=exam.pass_threshold)
