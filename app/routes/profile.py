from flask import flash, Blueprint, render_template, request, redirect, url_for
from flask_login import login_required, current_user
from app.models.course import Course
from app.models.user_activity import UserActivity
from datetime import timedelta
from app.database import db

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@login_required
def profile():
    if current_user.role == 'teacher':
        courses = Course.query.filter_by(author_id=current_user.id).all()
    else:
        courses = [course for course in current_user.courses if course.status == Course.STATUS_PUBLISHED]

    activities = UserActivity.query \
        .filter_by(user_id=current_user.id) \
        .order_by(UserActivity.timestamp.desc()) \
        .limit(20).all()

    return render_template('profile.html', user=current_user, courses=courses, activities=activities, timedelta=timedelta)

@profile_bp.route('/profile/update_bio', methods=['POST'])
@login_required
def update_bio():
    bio = request.form.get('bio')
    current_user.bio = bio
    try:
        db.session.commit()

        activity = UserActivity(
            user_id=current_user.id,
            activity_type='update_bio',
            description='Вы обновили биографию'
        )
        db.session.add(activity)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        flash(f"Ошибка при обновлении биографии: {str(e)}", "error")
        return redirect(url_for('profile.profile'))

    flash("Биография успешно обновлена.", "success")
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
