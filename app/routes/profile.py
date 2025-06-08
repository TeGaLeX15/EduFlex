from flask import flash, Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.course import Course
from app.database import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    if current_user.role == 'teacher':
        courses = Course.query.filter_by(author_id=current_user.id).all()
    else:
        courses = [course for course in current_user.courses if course.status == Course.STATUS_PUBLISHED]

    return render_template('profile.html', user=current_user, courses=courses)

@profile_bp.route('/profile/update_bio', methods=['POST'])
@login_required
def update_bio():
    bio = request.form.get('bio')
    current_user.bio = bio
    db.session.commit()
    return redirect(url_for('profile.profile'))

@profile_bp.route('/profile/start_course/<int:course_id>', methods=['GET'])
@login_required
def start_course(course_id):
    course = Course.query.get(course_id)
    if course:
        if course not in current_user.courses:
            current_user.courses.append(course)
            db.session.commit()
            flash(f'Вы успешно начали обучение на курсе "{course.title}"!', 'success')
        else:
            flash('Вы уже проходите этот курс.', 'warning')
        return redirect(url_for('courses.course_detail', slug=course.slug))
    else:
        flash('Курс не найден.', 'danger')
        return redirect(url_for('courses.courses_main'))
