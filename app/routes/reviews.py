from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.platform_review import PlatformReview
from app.models.user_activity import UserActivity
from app.database import db

reviews_bp = Blueprint("reviews", __name__)

@reviews_bp.route("/leave-review")
@login_required
def leave_review():
    review_text = session.pop("temp_review_text", "")
    rating = session.pop("temp_rating", "")
    return render_template("leave_review.html", review_text=review_text, rating=rating)

@reviews_bp.route("/leave-review/submit", methods=["POST"])
@login_required
def submit_review():
    review_text = request.form.get("review_text", "").strip()
    rating = request.form.get("rating", "").strip()

    session["temp_review_text"] = review_text
    session["temp_rating"] = rating

    if not review_text or not rating:
        flash("Пожалуйста, заполните отзыв и выберите оценку.", "error")
        return redirect(url_for("reviews.leave_review"))

    if len(review_text) < 25:
        flash("Отзыв должен содержать минимум 25 символов.", "warning")
        return redirect(url_for("reviews.leave_review"))

    try:
        rating_value = int(rating)
        if rating_value < 1 or rating_value > 5:
            raise ValueError
    except ValueError:
        flash("Некорректная оценка. Пожалуйста, выберите от 1 до 5 звёзд.", "error")
        return redirect(url_for("reviews.leave_review"))

    try:
        new_review = PlatformReview(
            user_id=current_user.id,
            content=review_text,
            rating=rating_value
        )
        db.session.add(new_review)
        db.session.commit()

        activity = UserActivity(
            user_id=current_user.id,
            activity_type='leave_review',
            description=f'Вы оставили отзыв о платформе с рейтингом {rating_value} звезд'
        )
        db.session.add(activity)
        db.session.commit()

        session.pop("temp_review_text", None)
        session.pop("temp_rating", None)

        flash("Спасибо за ваш отзыв!", "success")
        return redirect(url_for("courses.about"))

    except Exception as e:
        db.session.rollback()
        flash(f"Произошла ошибка при сохранении отзыва: {str(e)}", "error")
        return redirect(url_for("reviews.leave_review"))
